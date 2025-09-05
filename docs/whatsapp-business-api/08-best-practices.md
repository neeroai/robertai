# Mejores Prácticas - WhatsApp Business API

## Introducción

Esta guía presenta las mejores prácticas para implementar WhatsApp Business API de manera efectiva y escalable con Bird.com AI Employees en el ecosistema RobertAI.

## 1. Seguridad y Autenticación

### Gestión Segura de Credenciales

```python
# security_manager.py
import os
from cryptography.fernet import Fernet
from typing import Dict, Optional
import keyring
import logging

class SecureCredentialManager:
    """Gestor seguro de credenciales para WhatsApp Business API"""
    
    def __init__(self):
        self.encryption_key = self._get_or_create_key()
        self.cipher_suite = Fernet(self.encryption_key)
    
    def _get_or_create_key(self) -> bytes:
        """Obtener o crear clave de encriptación"""
        try:
            key = keyring.get_password("robertai", "encryption_key")
            if key:
                return key.encode()
        except:
            pass
        
        # Generar nueva clave
        key = Fernet.generate_key()
        try:
            keyring.set_password("robertai", "encryption_key", key.decode())
        except:
            logging.warning("No se pudo guardar la clave en keyring")
        
        return key
    
    def encrypt_credential(self, credential: str) -> str:
        """Encriptar credencial"""
        return self.cipher_suite.encrypt(credential.encode()).decode()
    
    def decrypt_credential(self, encrypted_credential: str) -> str:
        """Desencriptar credencial"""
        return self.cipher_suite.decrypt(encrypted_credential.encode()).decode()
    
    def get_whatsapp_credentials(self) -> Dict[str, str]:
        """Obtener credenciales de WhatsApp de forma segura"""
        credentials = {}
        
        # Credenciales desde variables de entorno (recomendado para producción)
        env_credentials = {
            'access_token': 'WHATSAPP_ACCESS_TOKEN',
            'phone_number_id': 'WHATSAPP_PHONE_NUMBER_ID',
            'business_account_id': 'WHATSAPP_BUSINESS_ACCOUNT_ID',
            'webhook_verify_token': 'WHATSAPP_WEBHOOK_VERIFY_TOKEN',
            'webhook_secret': 'WHATSAPP_WEBHOOK_SECRET'
        }
        
        for key, env_var in env_credentials.items():
            value = os.getenv(env_var)
            if not value:
                raise ValueError(f"Credencial faltante: {env_var}")
            credentials[key] = value
        
        return credentials
    
    def validate_credentials(self, credentials: Dict[str, str]) -> bool:
        """Validar formato de credenciales"""
        required_fields = [
            'access_token', 'phone_number_id', 'business_account_id',
            'webhook_verify_token', 'webhook_secret'
        ]
        
        for field in required_fields:
            if not credentials.get(field):
                logging.error(f"Credencial faltante: {field}")
                return False
            
            if len(credentials[field]) < 10:  # Validación básica de longitud
                logging.error(f"Credencial muy corta: {field}")
                return False
        
        return True

# Uso del gestor de credenciales
cred_manager = SecureCredentialManager()
credentials = cred_manager.get_whatsapp_credentials()

if cred_manager.validate_credentials(credentials):
    logging.info("Credenciales válidas")
else:
    logging.error("Error en validación de credenciales")
```

### Verificación de Firma HMAC

```python
# webhook_security.py
import hmac
import hashlib
import time
from typing import Optional
import logging

class WebhookSecurityManager:
    def __init__(self, webhook_secret: str):
        self.webhook_secret = webhook_secret.encode()
        self.max_timestamp_diff = 300  # 5 minutos
    
    def verify_signature(self, payload: bytes, signature: str, 
                        timestamp: Optional[str] = None) -> bool:
        """Verificar firma HMAC-SHA256 con validación temporal"""
        
        if not signature or not signature.startswith('sha256='):
            logging.warning("Firma faltante o formato inválido")
            return False
        
        # Verificar timestamp si se proporciona
        if timestamp:
            try:
                webhook_time = int(timestamp)
                current_time = int(time.time())
                
                if abs(current_time - webhook_time) > self.max_timestamp_diff:
                    logging.warning(f"Webhook timestamp muy antiguo: {timestamp}")
                    return False
            except ValueError:
                logging.warning("Timestamp inválido en webhook")
                return False
        
        # Calcular firma esperada
        expected_signature = 'sha256=' + hmac.new(
            self.webhook_secret,
            payload,
            hashlib.sha256
        ).hexdigest()
        
        # Comparación segura contra timing attacks
        is_valid = hmac.compare_digest(signature, expected_signature)
        
        if not is_valid:
            logging.warning(f"Firma HMAC inválida. Esperada: {expected_signature[:20]}..., Recibida: {signature[:20]}...")
        
        return is_valid
    
    def generate_signature(self, payload: bytes) -> str:
        """Generar firma HMAC-SHA256 para testing"""
        return 'sha256=' + hmac.new(
            self.webhook_secret,
            payload,
            hashlib.sha256
        ).hexdigest()

# Uso en FastAPI
from fastapi import Request, HTTPException

security_manager = WebhookSecurityManager(os.getenv('WHATSAPP_WEBHOOK_SECRET'))

@app.post("/webhooks/whatsapp")
async def receive_webhook(request: Request):
    signature = request.headers.get('X-Hub-Signature-256')
    timestamp = request.headers.get('X-Hub-Signature-Timestamp')
    body = await request.body()
    
    if not security_manager.verify_signature(body, signature, timestamp):
        raise HTTPException(status_code=401, detail="Firma inválida")
    
    # Procesar webhook...
    return "OK"
```

## 2. Performance y Escalabilidad

### Sistema de Cola de Mensajes

```python
# message_queue.py
import asyncio
from asyncio import Queue, PriorityQueue
from typing import Dict, Any, Optional, Callable
from dataclasses import dataclass, field
from datetime import datetime, timedelta
import logging
import json

@dataclass
class QueuedMessage:
    priority: int
    created_at: datetime
    message_data: Dict[str, Any]
    retry_count: int = 0
    max_retries: int = 3
    
    def __lt__(self, other):
        return self.priority < other.priority

class MessageQueueManager:
    """Gestor de cola de mensajes con prioridades y reintentos"""
    
    def __init__(self, max_workers: int = 10, max_queue_size: int = 1000):
        self.message_queue = PriorityQueue(maxsize=max_queue_size)
        self.failed_queue = Queue()
        self.max_workers = max_workers
        self.workers = []
        self.running = False
        self.stats = {
            'messages_processed': 0,
            'messages_failed': 0,
            'messages_queued': 0,
            'average_processing_time': 0.0
        }
    
    async def start(self):
        """Iniciar workers de procesamiento"""
        self.running = True
        self.workers = [
            asyncio.create_task(self._worker(f"worker-{i}"))
            for i in range(self.max_workers)
        ]
        
        # Worker para manejar mensajes fallidos
        self.workers.append(
            asyncio.create_task(self._failed_message_worker())
        )
        
        logging.info(f"Cola de mensajes iniciada con {self.max_workers} workers")
    
    async def stop(self):
        """Detener cola de mensajes"""
        self.running = False
        
        # Cancelar workers
        for worker in self.workers:
            worker.cancel()
        
        await asyncio.gather(*self.workers, return_exceptions=True)
        logging.info("Cola de mensajes detenida")
    
    async def enqueue_message(self, message_data: Dict[str, Any], 
                            priority: int = 5) -> bool:
        """Agregar mensaje a la cola"""
        try:
            queued_msg = QueuedMessage(
                priority=priority,
                created_at=datetime.now(),
                message_data=message_data
            )
            
            await self.message_queue.put(queued_msg)
            self.stats['messages_queued'] += 1
            
            logging.info(f"Mensaje encolado con prioridad {priority}")
            return True
            
        except asyncio.QueueFull:
            logging.error("Cola de mensajes llena")
            return False
    
    async def _worker(self, worker_name: str):
        """Worker para procesar mensajes"""
        logging.info(f"Worker {worker_name} iniciado")
        
        while self.running:
            try:
                # Obtener mensaje de la cola
                queued_msg = await asyncio.wait_for(
                    self.message_queue.get(),
                    timeout=1.0
                )
                
                start_time = datetime.now()
                
                try:
                    # Procesar mensaje
                    await self._process_message(queued_msg.message_data)
                    
                    # Actualizar estadísticas
                    processing_time = (datetime.now() - start_time).total_seconds()
                    self.stats['messages_processed'] += 1
                    self._update_average_processing_time(processing_time)
                    
                    logging.info(f"Mensaje procesado por {worker_name} en {processing_time:.2f}s")
                    
                except Exception as e:
                    logging.error(f"Error procesando mensaje en {worker_name}: {e}")
                    
                    # Reencolar si no ha excedido max_retries
                    if queued_msg.retry_count < queued_msg.max_retries:
                        queued_msg.retry_count += 1
                        queued_msg.priority += 1  # Menor prioridad en reintentos
                        
                        # Delay antes del reintento
                        await asyncio.sleep(2 ** queued_msg.retry_count)
                        await self.message_queue.put(queued_msg)
                        
                        logging.info(f"Mensaje reencolado. Intento {queued_msg.retry_count}/{queued_msg.max_retries}")
                    else:
                        # Enviar a cola de fallidos
                        await self.failed_queue.put(queued_msg)
                        self.stats['messages_failed'] += 1
                        logging.error(f"Mensaje fallido definitivamente después de {queued_msg.max_retries} intentos")
                
                self.message_queue.task_done()
                
            except asyncio.TimeoutError:
                continue  # Timeout esperando mensaje
            except Exception as e:
                logging.error(f"Error crítico en worker {worker_name}: {e}")
    
    async def _failed_message_worker(self):
        """Worker para manejar mensajes fallidos"""
        while self.running:
            try:
                failed_msg = await asyncio.wait_for(
                    self.failed_queue.get(),
                    timeout=5.0
                )
                
                # Guardar mensaje fallido para análisis
                await self._save_failed_message(failed_msg)
                
                # Notificar fallo crítico si es necesario
                if self._is_critical_message(failed_msg):
                    await self._notify_critical_failure(failed_msg)
                
            except asyncio.TimeoutError:
                continue
    
    async def _process_message(self, message_data: Dict[str, Any]):
        """Procesar mensaje individual"""
        # Aquí se integra con WhatsApp Business API
        # Implementación específica del envío de mensaje
        
        client = WhatsAppBusinessClient(
            access_token=os.getenv('WHATSAPP_ACCESS_TOKEN'),
            phone_number_id=os.getenv('WHATSAPP_PHONE_NUMBER_ID')
        )
        
        async with client:
            return await client.send_message(message_data)
    
    def get_queue_stats(self) -> Dict[str, Any]:
        """Obtener estadísticas de la cola"""
        return {
            **self.stats,
            'queue_size': self.message_queue.qsize(),
            'failed_queue_size': self.failed_queue.qsize(),
            'workers_active': len([w for w in self.workers if not w.done()])
        }
```

### Cache Distribuido con Redis

```python
# distributed_cache.py
import aioredis
import json
import pickle
from typing import Any, Optional, Dict
from datetime import timedelta
import logging

class DistributedCache:
    """Cache distribuido para optimizar respuestas de AI"""
    
    def __init__(self, redis_url: str, default_ttl: int = 3600):
        self.redis_url = redis_url
        self.default_ttl = default_ttl
        self.redis_client = None
    
    async def connect(self):
        """Conectar a Redis"""
        try:
            self.redis_client = await aioredis.from_url(
                self.redis_url,
                encoding="utf-8",
                decode_responses=False  # Para manejar datos binarios
            )
            logging.info("Conectado a Redis para cache distribuido")
        except Exception as e:
            logging.error(f"Error conectando a Redis: {e}")
            raise
    
    async def disconnect(self):
        """Desconectar de Redis"""
        if self.redis_client:
            await self.redis_client.close()
    
    async def get(self, key: str, default: Any = None) -> Any:
        """Obtener valor del cache"""
        try:
            data = await self.redis_client.get(f"robertai:cache:{key}")
            if data:
                return pickle.loads(data)
            return default
        except Exception as e:
            logging.error(f"Error obteniendo del cache: {e}")
            return default
    
    async def set(self, key: str, value: Any, ttl: Optional[int] = None) -> bool:
        """Guardar valor en cache"""
        try:
            ttl = ttl or self.default_ttl
            data = pickle.dumps(value)
            
            await self.redis_client.setex(
                f"robertai:cache:{key}",
                ttl,
                data
            )
            return True
        except Exception as e:
            logging.error(f"Error guardando en cache: {e}")
            return False
    
    async def get_conversation_context(self, user_id: str) -> Optional[Dict]:
        """Obtener contexto de conversación"""
        return await self.get(f"conversation:{user_id}")
    
    async def set_conversation_context(self, user_id: str, context: Dict, 
                                     ttl: int = 86400) -> bool:
        """Guardar contexto de conversación (24h TTL)"""
        return await self.set(f"conversation:{user_id}", context, ttl)
    
    async def get_ai_response_cache(self, input_hash: str) -> Optional[Dict]:
        """Obtener respuesta AI cacheada"""
        return await self.get(f"ai_response:{input_hash}")
    
    async def set_ai_response_cache(self, input_hash: str, response: Dict, 
                                  ttl: int = 1800) -> bool:
        """Cachear respuesta AI (30 min TTL)"""
        return await self.set(f"ai_response:{input_hash}", response, ttl)
    
    async def increment_user_message_count(self, user_id: str) -> int:
        """Incrementar contador de mensajes por usuario"""
        try:
            key = f"robertai:stats:user_messages:{user_id}"
            count = await self.redis_client.incr(key)
            
            # Expiración diaria del contador
            if count == 1:
                await self.redis_client.expire(key, 86400)
            
            return count
        except Exception as e:
            logging.error(f"Error incrementando contador: {e}")
            return 0

# Uso del cache distribuido
cache = DistributedCache(os.getenv('REDIS_URL', 'redis://localhost:6379'))

async def get_cached_ai_response(user_input: str, context: Dict) -> Optional[Dict]:
    """Obtener respuesta AI con cache"""
    
    # Crear hash del input para cache
    input_data = {"input": user_input, "context": context}
    input_hash = hashlib.sha256(
        json.dumps(input_data, sort_keys=True).encode()
    ).hexdigest()
    
    # Buscar en cache
    cached_response = await cache.get_ai_response_cache(input_hash)
    if cached_response:
        logging.info("Respuesta AI obtenida del cache")
        return cached_response
    
    # Generar nueva respuesta
    ai_response = await generate_ai_response(user_input, context)
    
    # Guardar en cache
    await cache.set_ai_response_cache(input_hash, ai_response)
    
    return ai_response
```

## 3. Monitoreo y Observabilidad

### Sistema de Métricas Completo

```python
# monitoring.py
from prometheus_client import Counter, Histogram, Gauge, generate_latest
import time
from typing import Dict, Any, Optional
import logging
from datetime import datetime, timedelta
import asyncio

class WhatsAppMetrics:
    """Sistema de métricas para WhatsApp Business API"""
    
    def __init__(self):
        # Contadores
        self.messages_sent = Counter(
            'whatsapp_messages_sent_total',
            'Número total de mensajes enviados',
            ['type', 'status']
        )
        
        self.messages_received = Counter(
            'whatsapp_messages_received_total',
            'Número total de mensajes recibidos',
            ['type', 'from_user']
        )
        
        self.api_errors = Counter(
            'whatsapp_api_errors_total',
            'Errores de la API de WhatsApp',
            ['error_code', 'error_type']
        )
        
        # Histogramas
        self.message_processing_time = Histogram(
            'whatsapp_message_processing_seconds',
            'Tiempo de procesamiento de mensajes',
            ['message_type']
        )
        
        self.ai_response_time = Histogram(
            'whatsapp_ai_response_seconds',
            'Tiempo de respuesta del AI',
            ['ai_action_type']
        )
        
        # Gauges
        self.active_conversations = Gauge(
            'whatsapp_active_conversations',
            'Número de conversaciones activas'
        )
        
        self.queue_size = Gauge(
            'whatsapp_message_queue_size',
            'Tamaño de la cola de mensajes'
        )
        
        self.cache_hit_rate = Gauge(
            'whatsapp_cache_hit_rate',
            'Tasa de acierto del cache'
        )
        
        # Estadísticas locales
        self.local_stats = {
            'cache_hits': 0,
            'cache_misses': 0,
            'conversation_starts': 0,
            'conversation_ends': 0
        }
    
    def record_message_sent(self, message_type: str, status: str):
        """Registrar mensaje enviado"""
        self.messages_sent.labels(
            type=message_type,
            status=status
        ).inc()
    
    def record_message_received(self, message_type: str, from_user: bool = True):
        """Registrar mensaje recibido"""
        self.messages_received.labels(
            type=message_type,
            from_user=str(from_user).lower()
        ).inc()
    
    def record_api_error(self, error_code: int, error_type: str):
        """Registrar error de API"""
        self.api_errors.labels(
            error_code=str(error_code),
            error_type=error_type
        ).inc()
    
    def record_processing_time(self, message_type: str, processing_time: float):
        """Registrar tiempo de procesamiento"""
        self.message_processing_time.labels(
            message_type=message_type
        ).observe(processing_time)
    
    def record_ai_response_time(self, action_type: str, response_time: float):
        """Registrar tiempo de respuesta del AI"""
        self.ai_response_time.labels(
            ai_action_type=action_type
        ).observe(response_time)
    
    def update_active_conversations(self, count: int):
        """Actualizar número de conversaciones activas"""
        self.active_conversations.set(count)
    
    def update_queue_size(self, size: int):
        """Actualizar tamaño de cola"""
        self.queue_size.set(size)
    
    def record_cache_hit(self):
        """Registrar acierto de cache"""
        self.local_stats['cache_hits'] += 1
        self._update_cache_hit_rate()
    
    def record_cache_miss(self):
        """Registrar fallo de cache"""
        self.local_stats['cache_misses'] += 1
        self._update_cache_hit_rate()
    
    def _update_cache_hit_rate(self):
        """Actualizar tasa de acierto del cache"""
        total = self.local_stats['cache_hits'] + self.local_stats['cache_misses']
        if total > 0:
            hit_rate = self.local_stats['cache_hits'] / total
            self.cache_hit_rate.set(hit_rate)
    
    def get_metrics(self) -> bytes:
        """Obtener métricas en formato Prometheus"""
        return generate_latest()

# Singleton de métricas
metrics = WhatsAppMetrics()

# Decorador para medir tiempo de procesamiento
def measure_processing_time(message_type: str):
    def decorator(func):
        async def wrapper(*args, **kwargs):
            start_time = time.time()
            try:
                result = await func(*args, **kwargs)
                metrics.record_message_sent(message_type, 'success')
                return result
            except Exception as e:
                metrics.record_message_sent(message_type, 'error')
                raise
            finally:
                processing_time = time.time() - start_time
                metrics.record_processing_time(message_type, processing_time)
        return wrapper
    return decorator

# Ejemplo de uso
@measure_processing_time('text')
async def send_text_message_with_metrics(to: str, text: str):
    # Lógica de envío de mensaje...
    pass
```

### Sistema de Alertas

```python
# alerting.py
import asyncio
from typing import Dict, List, Callable, Any
from dataclasses import dataclass
from datetime import datetime, timedelta
import logging
import aiohttp

@dataclass
class Alert:
    name: str
    level: str  # 'info', 'warning', 'error', 'critical'
    message: str
    timestamp: datetime
    metadata: Dict[str, Any]

class AlertManager:
    """Gestor de alertas para WhatsApp Business API"""
    
    def __init__(self):
        self.alert_handlers = []
        self.alert_thresholds = {
            'error_rate': 0.05,  # 5% de mensajes fallidos
            'response_time': 5.0,  # 5 segundos
            'queue_size': 1000,
            'failed_webhooks': 10
        }
        self.alert_history = []
        self.alert_cooldowns = {}  # Prevenir spam de alertas
    
    def add_handler(self, handler: Callable[[Alert], None]):
        """Agregar handler de alertas"""
        self.alert_handlers.append(handler)
    
    async def check_system_health(self, metrics_data: Dict[str, Any]):
        """Verificar salud del sistema y generar alertas"""
        
        alerts_to_send = []
        
        # Verificar tasa de errores
        error_rate = metrics_data.get('error_rate', 0)
        if error_rate > self.alert_thresholds['error_rate']:
            alerts_to_send.append(Alert(
                name='high_error_rate',
                level='warning',
                message=f'Alta tasa de errores: {error_rate:.2%}',
                timestamp=datetime.now(),
                metadata={'error_rate': error_rate}
            ))
        
        # Verificar tiempo de respuesta
        avg_response_time = metrics_data.get('avg_response_time', 0)
        if avg_response_time > self.alert_thresholds['response_time']:
            alerts_to_send.append(Alert(
                name='slow_response_time',
                level='warning',
                message=f'Tiempo de respuesta lento: {avg_response_time:.2f}s',
                timestamp=datetime.now(),
                metadata={'response_time': avg_response_time}
            ))
        
        # Verificar tamaño de cola
        queue_size = metrics_data.get('queue_size', 0)
        if queue_size > self.alert_thresholds['queue_size']:
            alerts_to_send.append(Alert(
                name='large_queue_size',
                level='error',
                message=f'Cola de mensajes grande: {queue_size} elementos',
                timestamp=datetime.now(),
                metadata={'queue_size': queue_size}
            ))
        
        # Enviar alertas
        for alert in alerts_to_send:
            await self.send_alert(alert)
    
    async def send_alert(self, alert: Alert):
        """Enviar alerta a todos los handlers"""
        
        # Verificar cooldown
        if self._is_in_cooldown(alert.name):
            return
        
        # Registrar en historial
        self.alert_history.append(alert)
        
        # Aplicar cooldown
        self._set_cooldown(alert.name, timedelta(minutes=15))
        
        # Enviar a handlers
        for handler in self.alert_handlers:
            try:
                await handler(alert)
            except Exception as e:
                logging.error(f"Error enviando alerta: {e}")
        
        logging.info(f"Alerta enviada: {alert.name} - {alert.message}")
    
    def _is_in_cooldown(self, alert_name: str) -> bool:
        """Verificar si alerta está en cooldown"""
        cooldown_until = self.alert_cooldowns.get(alert_name)
        if cooldown_until and datetime.now() < cooldown_until:
            return True
        return False
    
    def _set_cooldown(self, alert_name: str, duration: timedelta):
        """Establecer cooldown para alerta"""
        self.alert_cooldowns[alert_name] = datetime.now() + duration

# Handlers de alertas
async def slack_alert_handler(alert: Alert):
    """Enviar alerta a Slack"""
    webhook_url = os.getenv('SLACK_WEBHOOK_URL')
    if not webhook_url:
        return
    
    color_map = {
        'info': '#36a64f',
        'warning': '#ffb347', 
        'error': '#ff6b6b',
        'critical': '#ff4757'
    }
    
    payload = {
        "attachments": [
            {
                "color": color_map.get(alert.level, '#000000'),
                "title": f"WhatsApp API Alert: {alert.name}",
                "text": alert.message,
                "fields": [
                    {
                        "title": "Level",
                        "value": alert.level.upper(),
                        "short": True
                    },
                    {
                        "title": "Time",
                        "value": alert.timestamp.strftime('%Y-%m-%d %H:%M:%S'),
                        "short": True
                    }
                ],
                "footer": "RobertAI WhatsApp Monitoring"
            }
        ]
    }
    
    async with aiohttp.ClientSession() as session:
        async with session.post(webhook_url, json=payload) as response:
            if response.status != 200:
                logging.error(f"Error enviando alerta a Slack: {response.status}")

async def email_alert_handler(alert: Alert):
    """Enviar alerta por email"""
    # Implementación de envío de email
    pass

# Configuración del sistema de alertas
alert_manager = AlertManager()
alert_manager.add_handler(slack_alert_handler)
alert_manager.add_handler(email_alert_handler)
```

## 4. Optimización de Conversaciones

### Gestión Inteligente de Contexto

```python
# conversation_optimization.py
from typing import Dict, List, Optional, Any
from datetime import datetime, timedelta
import asyncio
import json
import hashlib

class ConversationContextManager:
    """Gestor inteligente de contexto conversacional"""
    
    def __init__(self, cache_manager, max_context_length: int = 10):
        self.cache = cache_manager
        self.max_context_length = max_context_length
        self.context_weights = {
            'recent': 1.0,    # Mensajes recientes
            'relevant': 0.8,  # Mensajes temáticamente relevantes
            'important': 0.9, # Mensajes marcados como importantes
            'old': 0.3        # Mensajes antiguos
        }
    
    async def get_optimized_context(self, user_id: str, 
                                  current_message: str) -> Dict[str, Any]:
        """Obtener contexto optimizado para el usuario"""
        
        # Obtener historial completo
        full_context = await self.cache.get_conversation_context(user_id) or {
            'messages': [],
            'user_profile': {},
            'conversation_metadata': {}
        }
        
        messages = full_context.get('messages', [])
        
        if not messages:
            return full_context
        
        # Optimizar contexto basado en relevancia y recencia
        optimized_messages = await self._select_relevant_messages(
            messages, current_message
        )
        
        # Generar resumen si hay demasiados mensajes
        if len(optimized_messages) > self.max_context_length:
            summary = await self._generate_context_summary(optimized_messages)
            optimized_messages = optimized_messages[-self.max_context_length:]
            full_context['conversation_summary'] = summary
        
        full_context['messages'] = optimized_messages
        
        return full_context
    
    async def _select_relevant_messages(self, messages: List[Dict], 
                                      current_message: str) -> List[Dict]:
        """Seleccionar mensajes relevantes"""
        
        scored_messages = []
        current_time = datetime.now()
        
        for message in messages:
            score = 0
            message_time = datetime.fromisoformat(message.get('timestamp', current_time.isoformat()))
            
            # Puntuación por recencia (mensajes de última hora tienen mayor peso)
            time_diff = (current_time - message_time).total_seconds()
            if time_diff < 3600:  # 1 hora
                score += self.context_weights['recent']
            elif time_diff < 86400:  # 1 día
                score += self.context_weights['recent'] * 0.5
            else:
                score += self.context_weights['old']
            
            # Puntuación por relevancia semántica
            relevance_score = await self._calculate_semantic_similarity(
                current_message, message.get('content', '')
            )
            score += relevance_score * self.context_weights['relevant']
            
            # Puntuación por importancia (menciones de productos, precios, etc.)
            if self._contains_important_entities(message.get('content', '')):
                score += self.context_weights['important']
            
            scored_messages.append((message, score))
        
        # Ordenar por puntuación y devolver los mejores
        scored_messages.sort(key=lambda x: x[1], reverse=True)
        
        return [msg for msg, score in scored_messages if score > 0.3]
    
    async def _calculate_semantic_similarity(self, text1: str, text2: str) -> float:
        """Calcular similitud semántica entre dos textos"""
        # Implementación simplificada - usaría embeddings reales en producción
        
        words1 = set(text1.lower().split())
        words2 = set(text2.lower().split())
        
        if not words1 or not words2:
            return 0.0
        
        intersection = words1.intersection(words2)
        union = words1.union(words2)
        
        return len(intersection) / len(union) if union else 0.0
    
    def _contains_important_entities(self, text: str) -> bool:
        """Verificar si el texto contiene entidades importantes"""
        important_keywords = [
            'precio', 'costo', 'comprar', 'orden', 'pedido',
            'producto', 'servicio', 'cita', 'reserva', 'problema'
        ]
        
        text_lower = text.lower()
        return any(keyword in text_lower for keyword in important_keywords)
    
    async def _generate_context_summary(self, messages: List[Dict]) -> str:
        """Generar resumen del contexto"""
        # En producción, usaría un modelo de resumen
        # Implementación simplificada
        
        topics = set()
        user_intents = []
        
        for message in messages:
            content = message.get('content', '').lower()
            
            # Extraer temas principales
            if 'producto' in content:
                topics.add('consulta de productos')
            if 'precio' in content or 'costo' in content:
                topics.add('información de precios')
            if 'problema' in content or 'ayuda' in content:
                topics.add('solicitud de soporte')
        
        summary = f"Conversación sobre: {', '.join(topics) if topics else 'consulta general'}"
        
        return summary
    
    async def update_context(self, user_id: str, message_data: Dict, 
                           ai_response: Dict):
        """Actualizar contexto de conversación"""
        
        context = await self.cache.get_conversation_context(user_id) or {
            'messages': [],
            'user_profile': {},
            'conversation_metadata': {}
        }
        
        # Agregar nuevo intercambio
        new_message = {
            'timestamp': datetime.now().isoformat(),
            'user_message': message_data.get('content', ''),
            'ai_response': ai_response.get('text', ''),
            'message_type': message_data.get('type', 'text'),
            'metadata': {
                'confidence': ai_response.get('confidence', 1.0),
                'processing_time': ai_response.get('processing_time', 0),
                'ai_actions_used': ai_response.get('actions_used', [])
            }
        }
        
        context['messages'].append(new_message)
        
        # Actualizar perfil de usuario
        await self._update_user_profile(context, message_data, ai_response)
        
        # Mantener sólo los últimos N mensajes en contexto completo
        if len(context['messages']) > 50:
            # Generar resumen de mensajes antiguos
            old_messages = context['messages'][:-30]
            context['historical_summary'] = await self._generate_context_summary(old_messages)
            context['messages'] = context['messages'][-30:]
        
        # Guardar contexto actualizado
        await self.cache.set_conversation_context(user_id, context)
    
    async def _update_user_profile(self, context: Dict, message_data: Dict, 
                                 ai_response: Dict):
        """Actualizar perfil del usuario basado en la interacción"""
        
        profile = context.setdefault('user_profile', {})
        
        # Actualizar contador de mensajes
        profile['total_messages'] = profile.get('total_messages', 0) + 1
        profile['last_interaction'] = datetime.now().isoformat()
        
        # Detectar preferencias
        content = message_data.get('content', '').lower()
        
        preferences = profile.setdefault('preferences', {})
        
        if 'rápido' in content or 'urgente' in content:
            preferences['prefers_quick_response'] = True
        
        if 'detalle' in content or 'explicación' in content:
            preferences['prefers_detailed_response'] = True
        
        # Detectar intereses
        interests = profile.setdefault('interests', set())
        
        if 'inteligencia artificial' in content or 'ai' in content:
            interests.add('ai_technology')
        if 'desarrollo' in content or 'programación' in content:
            interests.add('software_development')
        
        # Convertir set a list para JSON serialization
        profile['interests'] = list(interests) if isinstance(interests, set) else interests
        
        # Actualizar nivel de satisfacción basado en respuestas
        if ai_response.get('user_feedback'):
            feedback = ai_response['user_feedback']
            satisfaction_history = profile.setdefault('satisfaction_history', [])
            satisfaction_history.append({
                'timestamp': datetime.now().isoformat(),
                'rating': feedback.get('rating'),
                'comment': feedback.get('comment')
            })
            
            # Mantener solo los últimos 10 feedbacks
            profile['satisfaction_history'] = satisfaction_history[-10:]
```

## 5. Testing y Quality Assurance

### Suite de Testing Completa

```python
# test_whatsapp_api.py
import pytest
import asyncio
from unittest.mock import Mock, AsyncMock, patch
import json
from datetime import datetime

class TestWhatsAppBusinessAPI:
    """Suite de tests para WhatsApp Business API"""
    
    @pytest.fixture
    def whatsapp_client(self):
        return WhatsAppBusinessClient(
            access_token="test_token",
            phone_number_id="test_phone_id"
        )
    
    @pytest.fixture
    def sample_text_message(self):
        return {
            "messaging_product": "whatsapp",
            "recipient_type": "individual",
            "to": "573001234567",
            "type": "text",
            "text": {
                "preview_url": True,
                "body": "Test message from RobertAI"
            }
        }
    
    @pytest.fixture
    def sample_webhook_data(self):
        return {
            "object": "whatsapp_business_account",
            "entry": [
                {
                    "id": "WHATSAPP_BUSINESS_ACCOUNT_ID",
                    "changes": [
                        {
                            "value": {
                                "messaging_product": "whatsapp",
                                "metadata": {
                                    "display_phone_number": "15550559999",
                                    "phone_number_id": "PHONE_NUMBER_ID"
                                },
                                "messages": [
                                    {
                                        "from": "573001234567",
                                        "id": "wamid.ABC123",
                                        "timestamp": "1234567890",
                                        "text": {
                                            "body": "Hola, necesito ayuda"
                                        },
                                        "type": "text"
                                    }
                                ]
                            },
                            "field": "messages"
                        }
                    ]
                }
            ]
        }
    
    @pytest.mark.asyncio
    async def test_send_text_message_success(self, whatsapp_client, sample_text_message):
        """Test envío exitoso de mensaje de texto"""
        
        expected_response = {
            "messaging_product": "whatsapp",
            "contacts": [
                {
                    "input": "573001234567",
                    "wa_id": "573001234567"
                }
            ],
            "messages": [
                {
                    "id": "wamid.TEST123",
                    "message_status": "accepted"
                }
            ]
        }
        
        with patch('aiohttp.ClientSession.post') as mock_post:
            mock_response = AsyncMock()
            mock_response.status = 200
            mock_response.json.return_value = expected_response
            mock_post.return_value.__aenter__.return_value = mock_response
            
            async with whatsapp_client:
                result = await whatsapp_client.send_message(sample_text_message)
            
            assert result == expected_response
            assert mock_post.called
    
    @pytest.mark.asyncio
    async def test_send_message_rate_limit_error(self, whatsapp_client, sample_text_message):
        """Test manejo de rate limit"""
        
        error_response = {
            "error": {
                "message": "Rate limit exceeded",
                "type": "OAuthException",
                "code": 4,
                "error_subcode": 131026
            }
        }
        
        with patch('aiohttp.ClientSession.post') as mock_post:
            mock_response = AsyncMock()
            mock_response.status = 429
            mock_response.json.return_value = error_response
            mock_response.headers = {'Retry-After': '60'}
            mock_post.return_value.__aenter__.return_value = mock_response
            
            async with whatsapp_client:
                with pytest.raises(WhatsAppAPIError) as excinfo:
                    await whatsapp_client.send_message(sample_text_message)
                
                assert excinfo.value.code == 4
                assert excinfo.value.subcode == 131026
    
    @pytest.mark.asyncio
    async def test_webhook_signature_verification(self):
        """Test verificación de firma HMAC"""
        
        webhook_secret = "test_webhook_secret"
        security_manager = WebhookSecurityManager(webhook_secret)
        
        payload = b'{"test": "data"}'
        
        # Generar firma válida
        valid_signature = security_manager.generate_signature(payload)
        
        # Test firma válida
        assert security_manager.verify_signature(payload, valid_signature)
        
        # Test firma inválida
        invalid_signature = "sha256=invalid_signature"
        assert not security_manager.verify_signature(payload, invalid_signature)
        
        # Test firma faltante
        assert not security_manager.verify_signature(payload, "")
        
        # Test formato incorrecto
        assert not security_manager.verify_signature(payload, "invalid_format")
    
    @pytest.mark.asyncio
    async def test_message_queue_processing(self):
        """Test procesamiento de cola de mensajes"""
        
        queue_manager = MessageQueueManager(max_workers=2, max_queue_size=10)
        
        # Mock del procesador de mensajes
        processed_messages = []
        
        async def mock_process_message(message_data):
            processed_messages.append(message_data)
            await asyncio.sleep(0.1)  # Simular procesamiento
        
        # Reemplazar método de procesamiento
        queue_manager._process_message = mock_process_message
        
        # Iniciar queue manager
        await queue_manager.start()
        
        # Encolar mensajes de prueba
        test_messages = [
            {"to": "573001234567", "text": f"Message {i}"}
            for i in range(5)
        ]
        
        for msg in test_messages:
            await queue_manager.enqueue_message(msg)
        
        # Esperar procesamiento
        await asyncio.sleep(1.0)
        
        # Verificar que todos los mensajes fueron procesados
        assert len(processed_messages) == 5
        
        # Detener queue manager
        await queue_manager.stop()
    
    @pytest.mark.asyncio
    async def test_conversation_context_optimization(self):
        """Test optimización de contexto conversacional"""
        
        mock_cache = Mock()
        mock_cache.get_conversation_context = AsyncMock(return_value={
            'messages': [
                {
                    'timestamp': (datetime.now() - timedelta(minutes=5)).isoformat(),
                    'content': 'Quiero comprar un producto',
                    'type': 'text'
                },
                {
                    'timestamp': (datetime.now() - timedelta(hours=2)).isoformat(),
                    'content': 'Hola',
                    'type': 'text'
                },
                {
                    'timestamp': (datetime.now() - timedelta(minutes=10)).isoformat(),
                    'content': '¿Cuál es el precio del producto X?',
                    'type': 'text'
                }
            ],
            'user_profile': {},
            'conversation_metadata': {}
        })
        
        context_manager = ConversationContextManager(mock_cache)
        
        # Test optimización con mensaje relacionado
        current_message = "Quiero más información sobre el producto"
        optimized_context = await context_manager.get_optimized_context(
            "test_user", current_message
        )
        
        # Verificar que se mantienen mensajes relevantes
        assert len(optimized_context['messages']) > 0
        
        # Los mensajes sobre productos deberían tener mayor prioridad
        relevant_messages = [
            msg for msg in optimized_context['messages']
            if 'producto' in msg['content'].lower()
        ]
        assert len(relevant_messages) >= 2
    
    @pytest.mark.asyncio
    async def test_media_upload_validation(self):
        """Test validación de subida de archivos multimedia"""
        
        multimedia_manager = MultimediaManager("test_token", "test_phone_id")
        
        # Test archivo inexistente
        with pytest.raises(FileNotFoundError):
            await multimedia_manager._validate_media_file("nonexistent.jpg", "image")
        
        # Test tamaño excedido (simular archivo grande)
        with patch('os.path.getsize', return_value=10 * 1024 * 1024):  # 10MB
            with patch('os.path.exists', return_value=True):
                with pytest.raises(ValueError, match="excede tamaño máximo"):
                    await multimedia_manager._validate_media_file("large_image.jpg", "image")
        
        # Test formato no soportado
        with patch('os.path.getsize', return_value=1024):  # 1KB
            with patch('os.path.exists', return_value=True):
                with pytest.raises(ValueError, match="Formato no soportado"):
                    await multimedia_manager._validate_media_file("file.xyz", "image")
    
    def test_phone_number_validation(self):
        """Test validación de números de teléfono"""
        
        # Números válidos
        valid_numbers = [
            "573001234567",   # Colombia
            "12025551234",    # Estados Unidos
            "34612345678",    # España
            "5511987654321"   # Brasil
        ]
        
        for number in valid_numbers:
            assert validate_whatsapp_number(number), f"Número válido rechazado: {number}"
        
        # Números inválidos
        invalid_numbers = [
            "123",           # Muy corto
            "0123456789",    # Empieza con 0
            "12345678901234567",  # Muy largo
            "+573001234567",      # Con signo +
            "57-300-123-4567",    # Con guiones
            "abc123456789"        # Con letras
        ]
        
        for number in invalid_numbers:
            assert not validate_whatsapp_number(number), f"Número inválido aceptado: {number}"
    
    @pytest.mark.asyncio
    async def test_error_recovery_system(self):
        """Test sistema de recuperación de errores"""
        
        # Test de reintentos con backoff exponencial
        attempt_count = 0
        
        async def failing_function():
            nonlocal attempt_count
            attempt_count += 1
            if attempt_count < 3:
                raise Exception("Temporary failure")
            return "success"
        
        result = await exponential_backoff_retry(failing_function, max_retries=3)
        
        assert result == "success"
        assert attempt_count == 3
    
    @pytest.mark.asyncio
    async def test_metrics_collection(self):
        """Test recolección de métricas"""
        
        metrics = WhatsAppMetrics()
        
        # Registrar algunas métricas
        metrics.record_message_sent("text", "success")
        metrics.record_message_sent("image", "success")
        metrics.record_message_sent("text", "error")
        
        metrics.record_message_received("text", True)
        metrics.record_api_error(429, "rate_limit")
        
        metrics.record_processing_time("text", 1.5)
        metrics.record_ai_response_time("text_processing", 0.8)
        
        # Obtener métricas en formato Prometheus
        metrics_output = metrics.get_metrics()
        
        assert b'whatsapp_messages_sent_total' in metrics_output
        assert b'whatsapp_messages_received_total' in metrics_output
        assert b'whatsapp_api_errors_total' in metrics_output

# Configuración de pytest
pytest_plugins = ['pytest_asyncio']

# Ejecutar tests
if __name__ == "__main__":
    pytest.main(["-v", __file__])
```

## Próximos Pasos

1. **Configurar troubleshooting**: Continuar con [Guía de Resolución de Problemas](10-troubleshooting.md)
2. **Revisar especificación OpenAPI**: Ver [Especificación OpenAPI](09-openapi-spec.yaml)
3. **Implementar monitoreo**: Configurar métricas y alertas en producción

---

**Nota**: Estas mejores prácticas están optimizadas para uso en producción con alto volumen de mensajes y requieren infraestructura robusta para máximo rendimiento.