#!/usr/bin/env python3
"""
Massive Queue Processor for RobertAI
High-performance message processing system for thousands of concurrent users
"""

import asyncio
import json
import time
import logging
from typing import Dict, Any, Optional, List, Callable, Union, Tuple
from dataclasses import dataclass, field
from datetime import datetime, timedelta
from enum import Enum
import aioredis
from redis.asyncio import Redis
import uuid
import msgpack
from concurrent.futures import ThreadPoolExecutor
import heapq

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class MessageType(Enum):
    TEXT = "text"
    IMAGE = "image"
    AUDIO = "audio"
    VIDEO = "video"
    DOCUMENT = "document"
    INTERACTIVE = "interactive"
    TEMPLATE = "template"
    SYSTEM = "system"

class MessagePriority(Enum):
    CRITICAL = 1    # System messages, errors
    HIGH = 2        # Real-time responses, user interactions
    NORMAL = 3      # Regular messages
    LOW = 4         # Bulk messages, analytics
    BATCH = 5       # Non-urgent batch processing

class ProcessingStatus(Enum):
    PENDING = "pending"
    PROCESSING = "processing"
    COMPLETED = "completed"
    FAILED = "failed"
    RETRY = "retry"
    DEAD_LETTER = "dead_letter"

@dataclass
class QueuedMessage:
    """Mensaje en cola con metadatos completos"""
    id: str
    user_id: str
    message_type: MessageType
    priority: MessagePriority
    content: Dict[str, Any]
    created_at: float = field(default_factory=time.time)
    scheduled_at: Optional[float] = None  # Para mensajes programados
    retry_count: int = 0
    max_retries: int = 3
    processing_timeout: float = 30.0  # segundos
    status: ProcessingStatus = ProcessingStatus.PENDING
    processing_started_at: Optional[float] = None
    completed_at: Optional[float] = None
    error_details: Optional[str] = None
    metadata: Dict[str, Any] = field(default_factory=dict)
    
    def __lt__(self, other):
        """Para ordenamiento en heap por prioridad"""
        if self.priority.value != other.priority.value:
            return self.priority.value < other.priority.value
        return self.created_at < other.created_at
    
    @property
    def is_expired(self) -> bool:
        """Verificar si el mensaje ha expirado"""
        if self.processing_started_at:
            return time.time() > (self.processing_started_at + self.processing_timeout)
        return False
    
    @property
    def should_retry(self) -> bool:
        """Verificar si el mensaje debe ser reintentado"""
        return self.retry_count < self.max_retries and self.status == ProcessingStatus.FAILED
    
    def mark_processing(self):
        """Marcar mensaje como siendo procesado"""
        self.status = ProcessingStatus.PROCESSING
        self.processing_started_at = time.time()
    
    def mark_completed(self):
        """Marcar mensaje como completado"""
        self.status = ProcessingStatus.COMPLETED
        self.completed_at = time.time()
    
    def mark_failed(self, error: str):
        """Marcar mensaje como fallido"""
        self.status = ProcessingStatus.FAILED
        self.error_details = error
        self.retry_count += 1

@dataclass
class QueueStats:
    """Estadísticas de la cola"""
    total_messages_processed: int = 0
    total_messages_failed: int = 0
    messages_per_second: float = 0.0
    avg_processing_time: float = 0.0
    queue_sizes: Dict[MessagePriority, int] = field(default_factory=dict)
    active_workers: int = 0
    total_workers: int = 0
    retry_queue_size: int = 0
    dead_letter_queue_size: int = 0
    last_updated: datetime = field(default_factory=datetime.now)

class MassiveQueueProcessor:
    """Procesador de colas masivo para miles de usuarios"""
    
    def __init__(self,
                 redis_url: str = "redis://localhost:6379",
                 max_workers: int = 100,
                 max_concurrent_per_user: int = 3,
                 batch_size: int = 50):
        
        self.redis_url = redis_url
        self.max_workers = max_workers
        self.max_concurrent_per_user = max_concurrent_per_user
        self.batch_size = batch_size
        
        # Redis clients
        self.redis_client: Optional[Redis] = None
        
        # Colas en memoria por prioridad
        self.priority_queues: Dict[MessagePriority, List[QueuedMessage]] = {
            priority: [] for priority in MessagePriority
        }
        
        # Control de concurrencia por usuario
        self.user_processing_count: Dict[str, int] = {}
        
        # Workers y tasks
        self.workers: List[asyncio.Task] = []
        self.running = False
        
        # Message processors por tipo
        self.message_processors: Dict[MessageType, Callable] = {}
        
        # Estadísticas
        self.stats = QueueStats()
        self.stats.total_workers = max_workers
        
        # Thread pool para procesamiento CPU-intensive
        self.thread_pool = ThreadPoolExecutor(max_workers=20)
        
        # Colas de retry y dead letter
        self.retry_queue: List[QueuedMessage] = []
        self.dead_letter_queue: List[QueuedMessage] = []
        
        # Control de rate limiting
        self.rate_limiter = {}  # user_id -> última vez que procesó mensaje
        
        # Tasks de background
        self.monitoring_task: Optional[asyncio.Task] = None
        self.retry_processor_task: Optional[asyncio.Task] = None
        self.scheduled_processor_task: Optional[asyncio.Task] = None
        
    async def initialize(self):
        """Inicializar el procesador de colas"""
        
        # Conectar a Redis
        self.redis_client = await aioredis.from_url(
            self.redis_url,
            encoding="utf-8",
            decode_responses=False
        )
        
        # Registrar procesadores por defecto
        self._register_default_processors()
        
        # Cargar mensajes persistentes desde Redis
        await self._load_persistent_queues()
        
        logger.info(f"Queue processor initialized with {self.max_workers} workers")
    
    async def start(self):
        """Iniciar el procesamiento de colas"""
        if self.running:
            logger.warning("Queue processor already running")
            return
        
        self.running = True
        
        # Iniciar workers
        self.workers = [
            asyncio.create_task(self._worker(f"worker-{i}"))
            for i in range(self.max_workers)
        ]
        
        # Iniciar tasks de background
        self.monitoring_task = asyncio.create_task(self._monitoring_loop())
        self.retry_processor_task = asyncio.create_task(self._retry_processor_loop())
        self.scheduled_processor_task = asyncio.create_task(self._scheduled_processor_loop())
        
        self.stats.active_workers = len(self.workers)
        
        logger.info(f"Started {len(self.workers)} workers and background tasks")
    
    async def stop(self):
        """Detener el procesamiento de colas"""
        if not self.running:
            return
        
        self.running = False
        
        # Cancelar workers
        for worker in self.workers:
            worker.cancel()
        
        # Cancelar tasks de background
        tasks_to_cancel = [
            self.monitoring_task,
            self.retry_processor_task,
            self.scheduled_processor_task
        ]
        
        for task in tasks_to_cancel:
            if task:
                task.cancel()
        
        # Esperar que terminen
        all_tasks = self.workers + [t for t in tasks_to_cancel if t]
        await asyncio.gather(*all_tasks, return_exceptions=True)
        
        # Persistir colas pendientes
        await self._persist_queues()
        
        # Cerrar conexiones
        if self.redis_client:
            await self.redis_client.close()
        
        self.thread_pool.shutdown(wait=True)
        
        self.stats.active_workers = 0
        
        logger.info("Queue processor stopped")
    
    def register_processor(self, message_type: MessageType, processor: Callable):
        """Registrar procesador personalizado para tipo de mensaje"""
        self.message_processors[message_type] = processor
        logger.info(f"Registered custom processor for {message_type.value}")
    
    async def enqueue_message(self, 
                             user_id: str,
                             message_type: MessageType,
                             content: Dict[str, Any],
                             priority: MessagePriority = MessagePriority.NORMAL,
                             scheduled_at: Optional[float] = None,
                             metadata: Optional[Dict[str, Any]] = None) -> str:
        """Encolar mensaje para procesamiento"""
        
        message_id = str(uuid.uuid4())
        
        queued_message = QueuedMessage(
            id=message_id,
            user_id=user_id,
            message_type=message_type,
            priority=priority,
            content=content,
            scheduled_at=scheduled_at,
            metadata=metadata or {}
        )
        
        # Si es un mensaje programado, guardarlo por separado
        if scheduled_at and scheduled_at > time.time():
            await self._enqueue_scheduled_message(queued_message)
        else:
            # Encolarlo inmediatamente
            heapq.heappush(self.priority_queues[priority], queued_message)
            
            # Actualizar estadísticas
            self.stats.queue_sizes[priority] = len(self.priority_queues[priority])
            
            # Persistir en Redis si es crítico
            if priority in [MessagePriority.CRITICAL, MessagePriority.HIGH]:
                await self._persist_message(queued_message)
        
        logger.debug(f"Enqueued message {message_id} for user {user_id} with priority {priority.value}")
        
        return message_id
    
    async def get_queue_status(self) -> Dict[str, Any]:
        """Obtener estado actual de las colas"""
        
        total_pending = sum(len(queue) for queue in self.priority_queues.values())
        
        queue_sizes = {}
        for priority, queue in self.priority_queues.items():
            queue_sizes[priority.value] = len(queue)
        
        return {
            "total_pending_messages": total_pending,
            "queue_sizes_by_priority": queue_sizes,
            "active_workers": len([w for w in self.workers if not w.done()]),
            "total_workers": self.max_workers,
            "retry_queue_size": len(self.retry_queue),
            "dead_letter_queue_size": len(self.dead_letter_queue),
            "users_processing": len(self.user_processing_count),
            "stats": {
                "total_processed": self.stats.total_messages_processed,
                "total_failed": self.stats.total_messages_failed,
                "messages_per_second": self.stats.messages_per_second,
                "avg_processing_time": self.stats.avg_processing_time
            },
            "last_updated": datetime.now().isoformat()
        }
    
    # Workers y procesamiento
    
    async def _worker(self, worker_name: str):
        """Worker para procesar mensajes"""
        logger.info(f"{worker_name} started")
        
        while self.running:
            try:
                message = await self._get_next_message()
                
                if not message:
                    await asyncio.sleep(0.1)  # Breve pausa si no hay mensajes
                    continue
                
                # Verificar rate limiting por usuario
                if not self._check_user_rate_limit(message.user_id):
                    # Reencolar el mensaje con delay
                    await asyncio.sleep(0.1)
                    heapq.heappush(self.priority_queues[message.priority], message)
                    continue
                
                # Verificar concurrencia por usuario
                user_concurrent = self.user_processing_count.get(message.user_id, 0)
                if user_concurrent >= self.max_concurrent_per_user:
                    # Reencolar y esperar
                    heapq.heappush(self.priority_queues[message.priority], message)
                    await asyncio.sleep(0.2)
                    continue
                
                # Procesar mensaje
                await self._process_message(message, worker_name)
                
            except asyncio.CancelledError:
                break
            except Exception as e:
                logger.error(f"Error in {worker_name}: {e}")
                await asyncio.sleep(1)
        
        logger.info(f"{worker_name} stopped")
    
    async def _get_next_message(self) -> Optional[QueuedMessage]:
        """Obtener próximo mensaje para procesar (por prioridad)"""
        
        # Revisar colas por orden de prioridad
        for priority in MessagePriority:
            if self.priority_queues[priority]:
                return heapq.heappop(self.priority_queues[priority])
        
        return None
    
    async def _process_message(self, message: QueuedMessage, worker_name: str):
        """Procesar mensaje individual"""
        
        start_time = time.time()
        
        try:
            # Marcar como procesando
            message.mark_processing()
            
            # Incrementar contador de concurrencia del usuario
            self.user_processing_count[message.user_id] = \
                self.user_processing_count.get(message.user_id, 0) + 1
            
            # Obtener procesador para el tipo de mensaje
            processor = self.message_processors.get(
                message.message_type, 
                self._default_message_processor
            )
            
            # Procesar mensaje
            if asyncio.iscoroutinefunction(processor):
                result = await processor(message)
            else:
                # Ejecutar en thread pool si no es async
                result = await asyncio.get_event_loop().run_in_executor(
                    self.thread_pool, processor, message
                )
            
            # Marcar como completado
            message.mark_completed()
            
            # Actualizar estadísticas
            processing_time = time.time() - start_time
            self.stats.total_messages_processed += 1
            self._update_avg_processing_time(processing_time)
            
            logger.debug(f"{worker_name} processed message {message.id} in {processing_time:.3f}s")
            
        except Exception as e:
            # Marcar como fallido
            message.mark_failed(str(e))
            
            self.stats.total_messages_failed += 1
            
            logger.error(f"Error processing message {message.id}: {e}")
            
            # Enviar a cola de retry si aplica
            if message.should_retry:
                self.retry_queue.append(message)
            else:
                self.dead_letter_queue.append(message)
        
        finally:
            # Decrementar contador de concurrencia del usuario
            if message.user_id in self.user_processing_count:
                self.user_processing_count[message.user_id] -= 1
                if self.user_processing_count[message.user_id] <= 0:
                    del self.user_processing_count[message.user_id]
    
    def _check_user_rate_limit(self, user_id: str) -> bool:
        """Verificar rate limiting por usuario"""
        current_time = time.time()
        last_processed = self.rate_limiter.get(user_id, 0)
        
        # Permitir máximo 1 mensaje por segundo por usuario
        if current_time - last_processed < 1.0:
            return False
        
        self.rate_limiter[user_id] = current_time
        return True
    
    def _update_avg_processing_time(self, processing_time: float):
        """Actualizar tiempo promedio de procesamiento"""
        if self.stats.avg_processing_time == 0:
            self.stats.avg_processing_time = processing_time
        else:
            # Media móvil exponencial
            self.stats.avg_processing_time = (
                self.stats.avg_processing_time * 0.9 + processing_time * 0.1
            )
    
    # Procesadores de mensajes
    
    def _register_default_processors(self):
        """Registrar procesadores por defecto"""
        
        self.message_processors = {
            MessageType.TEXT: self._process_text_message,
            MessageType.IMAGE: self._process_image_message,
            MessageType.AUDIO: self._process_audio_message,
            MessageType.VIDEO: self._process_video_message,
            MessageType.DOCUMENT: self._process_document_message,
            MessageType.INTERACTIVE: self._process_interactive_message,
            MessageType.TEMPLATE: self._process_template_message,
            MessageType.SYSTEM: self._process_system_message
        }
    
    async def _default_message_processor(self, message: QueuedMessage) -> Dict[str, Any]:
        """Procesador por defecto"""
        logger.warning(f"Using default processor for message type {message.message_type}")
        await asyncio.sleep(0.1)  # Simular procesamiento
        return {"status": "processed", "processor": "default"}
    
    async def _process_text_message(self, message: QueuedMessage) -> Dict[str, Any]:
        """Procesar mensaje de texto"""
        content = message.content
        
        # Simular procesamiento de texto con AI
        # En implementación real, aquí iría la integración con Bird.com AI
        
        response = {
            "type": "text",
            "text": f"Procesé tu mensaje: {content.get('text', '')[:50]}...",
            "processing_time": time.time() - message.created_at,
            "worker_info": {
                "processed_at": datetime.now().isoformat(),
                "message_id": message.id
            }
        }
        
        # Simular latencia variable
        await asyncio.sleep(0.1 + (message.priority.value * 0.02))
        
        return response
    
    async def _process_image_message(self, message: QueuedMessage) -> Dict[str, Any]:
        """Procesar mensaje con imagen"""
        content = message.content
        
        # Simular análisis de imagen
        await asyncio.sleep(0.3)  # Procesamiento más lento para imágenes
        
        return {
            "type": "text",
            "text": f"Analicé tu imagen. Veo: {content.get('caption', 'una imagen interesante')}",
            "image_analysis": {
                "objects_detected": ["person", "background"],
                "confidence": 0.85,
                "processing_time": 0.3
            }
        }
    
    async def _process_audio_message(self, message: QueuedMessage) -> Dict[str, Any]:
        """Procesar mensaje de audio"""
        # Simular transcripción
        await asyncio.sleep(0.5)
        
        return {
            "type": "text", 
            "text": "Transcribí tu audio: 'Mensaje de audio transcrito'",
            "transcription": {
                "text": "Mensaje de audio transcrito",
                "confidence": 0.92,
                "language": "es"
            }
        }
    
    async def _process_video_message(self, message: QueuedMessage) -> Dict[str, Any]:
        """Procesar mensaje de video"""
        await asyncio.sleep(1.0)  # Procesamiento más lento
        
        return {
            "type": "text",
            "text": "Procesé tu video. Duración: 30 segundos",
            "video_analysis": {
                "duration": 30,
                "frames_analyzed": 150
            }
        }
    
    async def _process_document_message(self, message: QueuedMessage) -> Dict[str, Any]:
        """Procesar mensaje con documento"""
        await asyncio.sleep(0.4)
        
        return {
            "type": "text",
            "text": "Extraje el contenido de tu documento",
            "document_analysis": {
                "pages": 3,
                "text_extracted": True,
                "summary": "Documento procesado exitosamente"
            }
        }
    
    async def _process_interactive_message(self, message: QueuedMessage) -> Dict[str, Any]:
        """Procesar mensaje interactivo"""
        content = message.content
        selection = content.get('selection')
        
        return {
            "type": "text",
            "text": f"Procesé tu selección: {selection}",
            "next_step": "continue_flow"
        }
    
    async def _process_template_message(self, message: QueuedMessage) -> Dict[str, Any]:
        """Procesar mensaje de template"""
        await asyncio.sleep(0.1)
        
        return {
            "type": "template",
            "template_name": "response_template",
            "parameters": message.content.get('parameters', {})
        }
    
    async def _process_system_message(self, message: QueuedMessage) -> Dict[str, Any]:
        """Procesar mensaje del sistema"""
        content = message.content
        command = content.get('command')
        
        if command == "health_check":
            return {
                "status": "healthy",
                "queue_status": await self.get_queue_status()
            }
        
        return {"status": "processed", "command": command}
    
    # Background tasks
    
    async def _monitoring_loop(self):
        """Loop de monitoreo de estadísticas"""
        last_processed = 0
        
        while self.running:
            try:
                await asyncio.sleep(10)  # Cada 10 segundos
                
                # Calcular mensajes por segundo
                current_processed = self.stats.total_messages_processed
                messages_in_interval = current_processed - last_processed
                self.stats.messages_per_second = messages_in_interval / 10.0
                last_processed = current_processed
                
                # Actualizar tamaños de cola
                for priority, queue in self.priority_queues.items():
                    self.stats.queue_sizes[priority] = len(queue)
                
                self.stats.retry_queue_size = len(self.retry_queue)
                self.stats.dead_letter_queue_size = len(self.dead_letter_queue)
                self.stats.last_updated = datetime.now()
                
                logger.info(f"Queue stats - Processed: {current_processed}, "
                          f"Rate: {self.stats.messages_per_second:.2f}/s, "
                          f"Failed: {self.stats.total_messages_failed}, "
                          f"Pending: {sum(self.stats.queue_sizes.values())}")
                
            except asyncio.CancelledError:
                break
            except Exception as e:
                logger.error(f"Error in monitoring loop: {e}")
    
    async def _retry_processor_loop(self):
        """Loop para procesar mensajes de retry"""
        while self.running:
            try:
                if self.retry_queue:
                    message = self.retry_queue.pop(0)
                    
                    # Calcular delay exponencial
                    delay = min(2 ** message.retry_count, 60)  # Máximo 60 segundos
                    await asyncio.sleep(delay)
                    
                    # Reencolar con prioridad normal
                    message.status = ProcessingStatus.PENDING
                    heapq.heappush(self.priority_queues[MessagePriority.NORMAL], message)
                    
                    logger.info(f"Requeued message {message.id} after {delay}s delay (attempt {message.retry_count})")
                
                await asyncio.sleep(1)
                
            except asyncio.CancelledError:
                break
            except Exception as e:
                logger.error(f"Error in retry processor: {e}")
    
    async def _scheduled_processor_loop(self):
        """Loop para procesar mensajes programados"""
        while self.running:
            try:
                current_time = time.time()
                
                # Buscar mensajes programados listos
                scheduled_messages = await self._get_due_scheduled_messages(current_time)
                
                for message in scheduled_messages:
                    # Mover a cola de procesamiento
                    heapq.heappush(self.priority_queues[message.priority], message)
                    logger.info(f"Activated scheduled message {message.id}")
                
                await asyncio.sleep(5)  # Revisar cada 5 segundos
                
            except asyncio.CancelledError:
                break
            except Exception as e:
                logger.error(f"Error in scheduled processor: {e}")
    
    # Persistencia en Redis
    
    async def _persist_message(self, message: QueuedMessage):
        """Persistir mensaje crítico en Redis"""
        try:
            key = f"robertai:queue:critical:{message.id}"
            data = msgpack.packb({
                "id": message.id,
                "user_id": message.user_id,
                "message_type": message.message_type.value,
                "priority": message.priority.value,
                "content": message.content,
                "created_at": message.created_at,
                "metadata": message.metadata
            })
            
            await self.redis_client.setex(key, 3600, data)  # 1 hora TTL
            
        except Exception as e:
            logger.error(f"Error persisting message: {e}")
    
    async def _load_persistent_queues(self):
        """Cargar mensajes persistentes desde Redis"""
        try:
            pattern = "robertai:queue:critical:*"
            keys = []
            
            async for key in self.redis_client.scan_iter(match=pattern):
                keys.append(key)
            
            for key in keys:
                try:
                    data = await self.redis_client.get(key)
                    if data:
                        message_data = msgpack.unpackb(data)
                        
                        # Recrear mensaje
                        message = QueuedMessage(
                            id=message_data["id"],
                            user_id=message_data["user_id"],
                            message_type=MessageType(message_data["message_type"]),
                            priority=MessagePriority(message_data["priority"]),
                            content=message_data["content"],
                            created_at=message_data["created_at"],
                            metadata=message_data.get("metadata", {})
                        )
                        
                        # Agregar a cola apropiada
                        heapq.heappush(self.priority_queues[message.priority], message)
                        
                        # Eliminar de Redis
                        await self.redis_client.delete(key)
                
                except Exception as e:
                    logger.warning(f"Error loading persisted message {key}: {e}")
            
            if keys:
                logger.info(f"Loaded {len(keys)} persisted messages from Redis")
                
        except Exception as e:
            logger.error(f"Error loading persistent queues: {e}")
    
    async def _persist_queues(self):
        """Persistir colas pendientes en Redis"""
        try:
            total_persisted = 0
            
            for priority, queue in self.priority_queues.items():
                for message in queue:
                    if message.status == ProcessingStatus.PENDING:
                        await self._persist_message(message)
                        total_persisted += 1
            
            if total_persisted > 0:
                logger.info(f"Persisted {total_persisted} pending messages to Redis")
                
        except Exception as e:
            logger.error(f"Error persisting queues: {e}")
    
    async def _enqueue_scheduled_message(self, message: QueuedMessage):
        """Encolar mensaje programado en Redis"""
        try:
            key = f"robertai:scheduled:{message.scheduled_at}:{message.id}"
            data = msgpack.packb({
                "id": message.id,
                "user_id": message.user_id,
                "message_type": message.message_type.value,
                "priority": message.priority.value,
                "content": message.content,
                "scheduled_at": message.scheduled_at,
                "metadata": message.metadata
            })
            
            await self.redis_client.setex(key, int(message.scheduled_at - time.time()) + 3600, data)
            
        except Exception as e:
            logger.error(f"Error enqueuing scheduled message: {e}")
    
    async def _get_due_scheduled_messages(self, current_time: float) -> List[QueuedMessage]:
        """Obtener mensajes programados que ya deben ejecutarse"""
        messages = []
        
        try:
            pattern = "robertai:scheduled:*"
            
            async for key in self.redis_client.scan_iter(match=pattern):
                try:
                    # Extraer timestamp del key
                    key_parts = key.decode().split(":")
                    scheduled_time = float(key_parts[2])
                    
                    if scheduled_time <= current_time:
                        data = await self.redis_client.get(key)
                        if data:
                            message_data = msgpack.unpackb(data)
                            
                            message = QueuedMessage(
                                id=message_data["id"],
                                user_id=message_data["user_id"],
                                message_type=MessageType(message_data["message_type"]),
                                priority=MessagePriority(message_data["priority"]),
                                content=message_data["content"],
                                scheduled_at=message_data["scheduled_at"],
                                metadata=message_data.get("metadata", {})
                            )
                            
                            messages.append(message)
                            
                            # Eliminar de scheduled messages
                            await self.redis_client.delete(key)
                
                except Exception as e:
                    logger.warning(f"Error processing scheduled message {key}: {e}")
        
        except Exception as e:
            logger.error(f"Error getting due scheduled messages: {e}")
        
        return messages

# Singleton instance
massive_queue = MassiveQueueProcessor()

# Funciones de utilidad
async def enqueue_user_message(user_id: str, message_type: str, content: Dict[str, Any],
                              priority: str = "normal") -> str:
    """Función de utilidad para encolar mensaje de usuario"""
    
    msg_type = MessageType(message_type)
    msg_priority = MessagePriority[priority.upper()]
    
    return await massive_queue.enqueue_message(
        user_id=user_id,
        message_type=msg_type,
        content=content,
        priority=msg_priority
    )

async def process_whatsapp_webhook(webhook_data: Dict[str, Any]) -> List[str]:
    """Procesar webhook de WhatsApp y encolar mensajes"""
    
    message_ids = []
    
    try:
        entries = webhook_data.get("entry", [])
        
        for entry in entries:
            changes = entry.get("changes", [])
            
            for change in changes:
                if change.get("field") == "messages":
                    value = change.get("value", {})
                    messages = value.get("messages", [])
                    
                    for message in messages:
                        user_id = message.get("from")
                        message_type = message.get("type", "text")
                        
                        # Determinar prioridad basada en tipo de mensaje
                        priority = MessagePriority.HIGH if message_type in ["interactive", "button"] else MessagePriority.NORMAL
                        
                        message_id = await massive_queue.enqueue_message(
                            user_id=user_id,
                            message_type=MessageType(message_type),
                            content=message,
                            priority=priority,
                            metadata={"webhook_entry": entry.get("id")}
                        )
                        
                        message_ids.append(message_id)
        
    except Exception as e:
        logger.error(f"Error processing WhatsApp webhook: {e}")
    
    return message_ids

if __name__ == "__main__":
    # Ejemplo de uso
    async def main():
        # Inicializar y empezar el procesador
        await massive_queue.initialize()
        await massive_queue.start()
        
        # Simular carga de mensajes
        for i in range(100):
            await massive_queue.enqueue_message(
                user_id=f"user_{i % 20}",  # 20 usuarios únicos
                message_type=MessageType.TEXT,
                content={"text": f"Test message {i}"},
                priority=MessagePriority.NORMAL
            )
        
        # Esperar procesamiento
        await asyncio.sleep(10)
        
        # Mostrar estadísticas
        status = await massive_queue.get_queue_status()
        print(json.dumps(status, indent=2))
        
        await massive_queue.stop()
    
    asyncio.run(main())