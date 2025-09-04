#!/usr/bin/env python3
"""
Massive Cache Strategy for RobertAI
Multi-layer caching system optimized for thousands of concurrent users
"""

import asyncio
import json
import hashlib
import time
import pickle
import logging
from typing import Dict, Any, Optional, List, Union, Tuple
from dataclasses import dataclass, field
from datetime import datetime, timedelta
from enum import Enum
import aioredis
from redis.asyncio import Redis, RedisCluster
import zlib
import msgpack

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class CacheLevel(Enum):
    L1_MEMORY = "L1"  # In-memory cache (fastest)
    L2_REDIS = "L2"   # Redis cache (fast)
    L3_PERSISTENT = "L3"  # Persistent cache (slower but reliable)

@dataclass
class CacheMetrics:
    """Métricas del sistema de cache"""
    hits: int = 0
    misses: int = 0
    total_requests: int = 0
    l1_hits: int = 0
    l2_hits: int = 0
    l3_hits: int = 0
    avg_response_time: float = 0.0
    cache_size_bytes: int = 0
    
    @property
    def hit_rate(self) -> float:
        return self.hits / self.total_requests if self.total_requests > 0 else 0.0
    
    @property
    def l1_hit_rate(self) -> float:
        return self.l1_hits / self.total_requests if self.total_requests > 0 else 0.0

@dataclass 
class CacheEntry:
    """Entrada del cache con metadatos"""
    key: str
    value: Any
    created_at: float
    ttl: int
    access_count: int = 0
    last_access: float = field(default_factory=time.time)
    compressed: bool = False
    size_bytes: int = 0
    
    @property
    def is_expired(self) -> bool:
        return time.time() > (self.created_at + self.ttl)
    
    @property
    def age_seconds(self) -> float:
        return time.time() - self.created_at
    
    def touch(self):
        """Actualizar último acceso"""
        self.access_count += 1
        self.last_access = time.time()

class MassiveCacheStrategy:
    """Sistema de cache masivo con múltiples niveles"""
    
    def __init__(self, 
                 redis_cluster_url: str = "redis://localhost:6379",
                 max_memory_cache_size: int = 10000,  # Número máximo de entradas en memoria
                 max_memory_size_bytes: int = 100 * 1024 * 1024,  # 100MB max en memoria
                 compression_threshold: int = 1024,  # Comprimir si > 1KB
                 default_ttl: int = 3600):  # 1 hora por defecto
        
        self.redis_cluster_url = redis_cluster_url
        self.max_memory_cache_size = max_memory_cache_size
        self.max_memory_size_bytes = max_memory_size_bytes
        self.compression_threshold = compression_threshold
        self.default_ttl = default_ttl
        
        # L1 Cache - In Memory
        self.l1_cache: Dict[str, CacheEntry] = {}
        self.l1_access_order: List[str] = []  # Para LRU eviction
        self.l1_size_bytes = 0
        
        # L2 Cache - Redis Cluster
        self.redis_client: Optional[Union[Redis, RedisCluster]] = None
        
        # L3 Cache - Persistent (implementación básica con Redis)
        self.persistent_client: Optional[Redis] = None
        
        # Métricas
        self.metrics = CacheMetrics()
        
        # Cache warmup data
        self.warmup_keys: List[str] = []
        
        # Background tasks
        self.cleanup_task: Optional[asyncio.Task] = None
        self.metrics_task: Optional[asyncio.Task] = None
        
    async def initialize(self):
        """Inicializar sistema de cache"""
        try:
            # Conectar a Redis Cluster para L2
            if "cluster" in self.redis_cluster_url.lower():
                # Redis Cluster setup
                cluster_nodes = [
                    {"host": "localhost", "port": 7000},
                    {"host": "localhost", "port": 7001},
                    {"host": "localhost", "port": 7002}
                ]
                self.redis_client = RedisCluster(startup_nodes=cluster_nodes, decode_responses=False)
            else:
                # Single Redis instance
                self.redis_client = await aioredis.from_url(
                    self.redis_cluster_url, 
                    encoding=None,  # Handle binary data
                    decode_responses=False
                )
            
            # Conectar a Redis persistente para L3 (puede ser la misma instancia)
            self.persistent_client = await aioredis.from_url(
                self.redis_cluster_url.replace("6379", "6380"),  # Otra DB para persistente
                encoding=None,
                decode_responses=False,
                db=1  # Usar DB diferente para persistencia
            )
            
            # Iniciar tareas de background
            self.cleanup_task = asyncio.create_task(self._cleanup_loop())
            self.metrics_task = asyncio.create_task(self._metrics_loop())
            
            # Cache warmup con datos comunes
            await self._warmup_cache()
            
            logger.info("Massive cache strategy initialized successfully")
            
        except Exception as e:
            logger.error(f"Failed to initialize cache: {e}")
            raise
    
    async def shutdown(self):
        """Cerrar sistema de cache"""
        # Cancelar tareas de background
        if self.cleanup_task:
            self.cleanup_task.cancel()
        if self.metrics_task:
            self.metrics_task.cancel()
        
        # Cerrar conexiones Redis
        if self.redis_client:
            await self.redis_client.close()
        if self.persistent_client:
            await self.persistent_client.close()
        
        # Limpiar cache L1
        self.l1_cache.clear()
        self.l1_access_order.clear()
        
        logger.info("Cache system shutdown complete")
    
    async def get(self, key: str, default: Any = None) -> Any:
        """Obtener valor del cache con estrategia multi-nivel"""
        start_time = time.time()
        self.metrics.total_requests += 1
        
        try:
            # L1 - In Memory Cache (más rápido)
            if key in self.l1_cache:
                entry = self.l1_cache[key]
                if not entry.is_expired:
                    entry.touch()
                    self._update_l1_access_order(key)
                    self.metrics.hits += 1
                    self.metrics.l1_hits += 1
                    self._update_response_time(start_time)
                    logger.debug(f"L1 cache hit for key: {key}")
                    return self._decompress_if_needed(entry.value, entry.compressed)
                else:
                    # Eliminar entrada expirada
                    await self._remove_from_l1(key)
            
            # L2 - Redis Cache
            try:
                redis_value = await self.redis_client.get(f"robertai:l2:{key}")
                if redis_value:
                    # Deserializar valor
                    try:
                        cache_data = msgpack.unpackb(redis_value)
                        value = cache_data['value']
                        compressed = cache_data.get('compressed', False)
                        
                        # Promover a L1 si es accedido frecuentemente
                        await self._promote_to_l1(key, value, compressed)
                        
                        self.metrics.hits += 1
                        self.metrics.l2_hits += 1
                        self._update_response_time(start_time)
                        logger.debug(f"L2 cache hit for key: {key}")
                        
                        return self._decompress_if_needed(value, compressed)
                        
                    except Exception as e:
                        logger.warning(f"Error deserializing L2 cache for key {key}: {e}")
            
            except Exception as e:
                logger.warning(f"L2 cache error for key {key}: {e}")
            
            # L3 - Persistent Cache
            try:
                persistent_value = await self.persistent_client.get(f"robertai:l3:{key}")
                if persistent_value:
                    try:
                        cache_data = msgpack.unpackb(persistent_value)
                        value = cache_data['value']
                        compressed = cache_data.get('compressed', False)
                        ttl = cache_data.get('ttl', self.default_ttl)
                        
                        # Promover a L2 y L1
                        await self._promote_to_l2(key, value, compressed, ttl)
                        await self._promote_to_l1(key, value, compressed)
                        
                        self.metrics.hits += 1
                        self.metrics.l3_hits += 1
                        self._update_response_time(start_time)
                        logger.debug(f"L3 cache hit for key: {key}")
                        
                        return self._decompress_if_needed(value, compressed)
                        
                    except Exception as e:
                        logger.warning(f"Error deserializing L3 cache for key {key}: {e}")
            
            except Exception as e:
                logger.warning(f"L3 cache error for key {key}: {e}")
            
            # Cache miss - no encontrado en ningún nivel
            self.metrics.misses += 1
            self._update_response_time(start_time)
            logger.debug(f"Cache miss for key: {key}")
            
            return default
            
        except Exception as e:
            logger.error(f"Error in cache get for key {key}: {e}")
            self.metrics.misses += 1
            return default
    
    async def set(self, key: str, value: Any, ttl: Optional[int] = None, 
                 levels: List[CacheLevel] = None) -> bool:
        """Guardar valor en cache con estrategia multi-nivel"""
        
        if ttl is None:
            ttl = self.default_ttl
        
        if levels is None:
            levels = [CacheLevel.L1_MEMORY, CacheLevel.L2_REDIS]
        
        try:
            # Preparar valor para almacenamiento
            serialized_value, compressed, size_bytes = await self._prepare_value_for_storage(value)
            
            success = True
            
            # L1 - In Memory
            if CacheLevel.L1_MEMORY in levels:
                success &= await self._set_l1(key, serialized_value, ttl, compressed, size_bytes)
            
            # L2 - Redis
            if CacheLevel.L2_REDIS in levels:
                success &= await self._set_l2(key, serialized_value, ttl, compressed)
            
            # L3 - Persistent
            if CacheLevel.L3_PERSISTENT in levels:
                success &= await self._set_l3(key, serialized_value, ttl, compressed)
            
            if success:
                logger.debug(f"Successfully cached key: {key} in levels: {[l.value for l in levels]}")
            
            return success
            
        except Exception as e:
            logger.error(f"Error setting cache for key {key}: {e}")
            return False
    
    async def delete(self, key: str) -> bool:
        """Eliminar clave de todos los niveles de cache"""
        success = True
        
        try:
            # Eliminar de L1
            if key in self.l1_cache:
                await self._remove_from_l1(key)
            
            # Eliminar de L2
            try:
                await self.redis_client.delete(f"robertai:l2:{key}")
            except Exception as e:
                logger.warning(f"Error deleting from L2: {e}")
                success = False
            
            # Eliminar de L3
            try:
                await self.persistent_client.delete(f"robertai:l3:{key}")
            except Exception as e:
                logger.warning(f"Error deleting from L3: {e}")
                success = False
            
            return success
            
        except Exception as e:
            logger.error(f"Error deleting cache key {key}: {e}")
            return False
    
    async def get_cached_ai_response(self, input_text: str, context: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """Obtener respuesta AI cacheada"""
        
        # Crear hash único para la consulta
        query_data = {
            "input": input_text.lower().strip(),
            "context_hash": self._hash_context(context)
        }
        query_hash = self._generate_cache_key("ai_response", query_data)
        
        return await self.get(query_hash)
    
    async def cache_ai_response(self, input_text: str, context: Dict[str, Any], 
                               response: Dict[str, Any], ttl: int = 1800) -> bool:
        """Cachear respuesta AI (30 min TTL por defecto)"""
        
        query_data = {
            "input": input_text.lower().strip(),
            "context_hash": self._hash_context(context)
        }
        query_hash = self._generate_cache_key("ai_response", query_data)
        
        # Agregar metadata a la respuesta
        cached_response = {
            **response,
            "cached_at": datetime.now().isoformat(),
            "cache_ttl": ttl
        }
        
        return await self.set(
            query_hash, 
            cached_response, 
            ttl=ttl,
            levels=[CacheLevel.L1_MEMORY, CacheLevel.L2_REDIS]
        )
    
    async def get_conversation_context(self, user_id: str) -> Optional[Dict[str, Any]]:
        """Obtener contexto de conversación"""
        key = self._generate_cache_key("conversation", {"user_id": user_id})
        return await self.get(key)
    
    async def set_conversation_context(self, user_id: str, context: Dict[str, Any], 
                                     ttl: int = 86400) -> bool:
        """Guardar contexto de conversación (24h TTL)"""
        key = self._generate_cache_key("conversation", {"user_id": user_id})
        
        return await self.set(
            key, 
            context, 
            ttl=ttl,
            levels=[CacheLevel.L1_MEMORY, CacheLevel.L2_REDIS, CacheLevel.L3_PERSISTENT]
        )
    
    async def get_user_profile(self, user_id: str) -> Optional[Dict[str, Any]]:
        """Obtener perfil de usuario"""
        key = self._generate_cache_key("user_profile", {"user_id": user_id})
        return await self.get(key)
    
    async def set_user_profile(self, user_id: str, profile: Dict[str, Any], 
                              ttl: int = 604800) -> bool:
        """Guardar perfil de usuario (7 días TTL)"""
        key = self._generate_cache_key("user_profile", {"user_id": user_id})
        
        return await self.set(
            key,
            profile,
            ttl=ttl,
            levels=[CacheLevel.L2_REDIS, CacheLevel.L3_PERSISTENT]
        )
    
    async def invalidate_user_cache(self, user_id: str) -> bool:
        """Invalidar todo el cache de un usuario"""
        patterns = [
            f"conversation:{user_id}",
            f"user_profile:{user_id}",
            f"ai_response:*:{user_id}*"
        ]
        
        success = True
        for pattern in patterns:
            try:
                # Buscar claves que coincidan con el patrón
                keys = []
                if hasattr(self.redis_client, 'scan_iter'):
                    async for key in self.redis_client.scan_iter(match=f"robertai:l2:{pattern}"):
                        keys.append(key.decode() if isinstance(key, bytes) else key)
                
                # Eliminar claves encontradas
                for key in keys:
                    cache_key = key.replace("robertai:l2:", "")
                    await self.delete(cache_key)
                    
            except Exception as e:
                logger.warning(f"Error invalidating pattern {pattern}: {e}")
                success = False
        
        return success
    
    def get_cache_stats(self) -> Dict[str, Any]:
        """Obtener estadísticas del cache"""
        return {
            "metrics": {
                "total_requests": self.metrics.total_requests,
                "hits": self.metrics.hits,
                "misses": self.metrics.misses,
                "hit_rate": self.metrics.hit_rate,
                "l1_hits": self.metrics.l1_hits,
                "l2_hits": self.metrics.l2_hits,
                "l3_hits": self.metrics.l3_hits,
                "l1_hit_rate": self.metrics.l1_hit_rate,
                "avg_response_time_ms": self.metrics.avg_response_time * 1000
            },
            "l1_cache": {
                "size": len(self.l1_cache),
                "max_size": self.max_memory_cache_size,
                "size_bytes": self.l1_size_bytes,
                "max_size_bytes": self.max_memory_size_bytes,
                "utilization": len(self.l1_cache) / self.max_memory_cache_size * 100
            },
            "configuration": {
                "compression_threshold": self.compression_threshold,
                "default_ttl": self.default_ttl,
                "max_memory_cache_size": self.max_memory_cache_size
            },
            "last_updated": datetime.now().isoformat()
        }
    
    # Métodos internos privados
    
    def _generate_cache_key(self, prefix: str, data: Dict[str, Any]) -> str:
        """Generar clave de cache única"""
        data_str = json.dumps(data, sort_keys=True)
        data_hash = hashlib.md5(data_str.encode()).hexdigest()
        return f"{prefix}:{data_hash}"
    
    def _hash_context(self, context: Dict[str, Any]) -> str:
        """Crear hash del contexto para cache"""
        # Solo incluir elementos relevantes del contexto para cache
        relevant_context = {
            "user_type": context.get("user_type"),
            "conversation_stage": context.get("conversation_stage"),
            "last_intent": context.get("last_intent")
        }
        return hashlib.md5(json.dumps(relevant_context, sort_keys=True).encode()).hexdigest()
    
    async def _prepare_value_for_storage(self, value: Any) -> Tuple[Any, bool, int]:
        """Preparar valor para almacenamiento (serialización y compresión)"""
        
        # Serializar valor
        if isinstance(value, (dict, list)):
            serialized = json.dumps(value)
        else:
            serialized = str(value)
        
        # Verificar si necesita compresión
        size_bytes = len(serialized.encode())
        compressed = False
        
        if size_bytes > self.compression_threshold:
            compressed_data = zlib.compress(serialized.encode())
            if len(compressed_data) < size_bytes:
                serialized = compressed_data
                compressed = True
                size_bytes = len(compressed_data)
        
        return serialized, compressed, size_bytes
    
    def _decompress_if_needed(self, value: Any, compressed: bool) -> Any:
        """Descomprimir valor si es necesario"""
        if compressed:
            try:
                decompressed = zlib.decompress(value).decode()
                return json.loads(decompressed)
            except:
                return value
        
        if isinstance(value, str):
            try:
                return json.loads(value)
            except:
                return value
        
        return value
    
    async def _set_l1(self, key: str, value: Any, ttl: int, compressed: bool, size_bytes: int) -> bool:
        """Guardar en L1 (memoria)"""
        try:
            # Verificar espacio disponible
            if (len(self.l1_cache) >= self.max_memory_cache_size or 
                self.l1_size_bytes + size_bytes > self.max_memory_size_bytes):
                await self._evict_l1_entries()
            
            # Crear entrada
            entry = CacheEntry(
                key=key,
                value=value,
                created_at=time.time(),
                ttl=ttl,
                compressed=compressed,
                size_bytes=size_bytes
            )
            
            self.l1_cache[key] = entry
            self._update_l1_access_order(key)
            self.l1_size_bytes += size_bytes
            
            return True
            
        except Exception as e:
            logger.error(f"Error setting L1 cache: {e}")
            return False
    
    async def _set_l2(self, key: str, value: Any, ttl: int, compressed: bool) -> bool:
        """Guardar en L2 (Redis)"""
        try:
            cache_data = {
                "value": value,
                "compressed": compressed,
                "ttl": ttl,
                "created_at": time.time()
            }
            
            serialized_data = msgpack.packb(cache_data)
            await self.redis_client.setex(f"robertai:l2:{key}", ttl, serialized_data)
            
            return True
            
        except Exception as e:
            logger.error(f"Error setting L2 cache: {e}")
            return False
    
    async def _set_l3(self, key: str, value: Any, ttl: int, compressed: bool) -> bool:
        """Guardar en L3 (persistente)"""
        try:
            cache_data = {
                "value": value,
                "compressed": compressed,
                "ttl": ttl,
                "created_at": time.time()
            }
            
            serialized_data = msgpack.packb(cache_data)
            await self.persistent_client.setex(f"robertai:l3:{key}", ttl * 2, serialized_data)  # TTL extendido
            
            return True
            
        except Exception as e:
            logger.error(f"Error setting L3 cache: {e}")
            return False
    
    async def _promote_to_l1(self, key: str, value: Any, compressed: bool):
        """Promover entrada a L1"""
        size_bytes = len(str(value).encode())
        await self._set_l1(key, value, self.default_ttl, compressed, size_bytes)
    
    async def _promote_to_l2(self, key: str, value: Any, compressed: bool, ttl: int):
        """Promover entrada a L2"""
        await self._set_l2(key, value, ttl, compressed)
    
    def _update_l1_access_order(self, key: str):
        """Actualizar orden de acceso para LRU"""
        if key in self.l1_access_order:
            self.l1_access_order.remove(key)
        self.l1_access_order.append(key)
    
    async def _remove_from_l1(self, key: str):
        """Remover entrada de L1"""
        if key in self.l1_cache:
            entry = self.l1_cache.pop(key)
            self.l1_size_bytes -= entry.size_bytes
            
        if key in self.l1_access_order:
            self.l1_access_order.remove(key)
    
    async def _evict_l1_entries(self):
        """Expulsar entradas de L1 usando LRU"""
        while (len(self.l1_cache) >= self.max_memory_cache_size * 0.9 or
               self.l1_size_bytes >= self.max_memory_size_bytes * 0.9):
            
            if not self.l1_access_order:
                break
                
            # Remover entrada menos recientemente usada
            lru_key = self.l1_access_order[0]
            await self._remove_from_l1(lru_key)
    
    def _update_response_time(self, start_time: float):
        """Actualizar tiempo de respuesta promedio"""
        response_time = time.time() - start_time
        if self.metrics.avg_response_time == 0:
            self.metrics.avg_response_time = response_time
        else:
            # Media móvil simple
            self.metrics.avg_response_time = (
                self.metrics.avg_response_time * 0.9 + response_time * 0.1
            )
    
    async def _warmup_cache(self):
        """Precalentar cache con datos comunes"""
        common_responses = {
            "greeting": {
                "text": "¡Hola! 👋 Soy RobertAI, tu asistente personal. ¿En qué puedo ayudarte?",
                "type": "text"
            },
            "help": {
                "text": "Puedo ayudarte con:\n• 📅 Recordatorios y alarmas\n• 📸 Análisis de imágenes\n• 🎤 Transcripción de audio\n• 📄 Procesamiento de documentos\n\n¿Qué te gustaría hacer?",
                "type": "interactive",
                "buttons": ["Ver demo", "Crear recordatorio", "Explorar funciones"]
            },
            "fallback": {
                "text": "No estoy seguro de cómo ayudarte con eso. ¿Podrías reformular tu pregunta?",
                "type": "text"
            }
        }
        
        for key, response in common_responses.items():
            await self.set(
                f"common_response:{key}",
                response,
                ttl=86400,  # 24 horas
                levels=[CacheLevel.L1_MEMORY, CacheLevel.L2_REDIS]
            )
        
        logger.info(f"Cache warmed up with {len(common_responses)} common responses")
    
    async def _cleanup_loop(self):
        """Loop de limpieza periódica"""
        while True:
            try:
                await asyncio.sleep(300)  # Cada 5 minutos
                await self._cleanup_expired_entries()
            except asyncio.CancelledError:
                break
            except Exception as e:
                logger.error(f"Error in cleanup loop: {e}")
    
    async def _metrics_loop(self):
        """Loop de métricas periódicas"""
        while True:
            try:
                await asyncio.sleep(60)  # Cada minuto
                stats = self.get_cache_stats()
                logger.info(f"Cache stats: {stats['metrics']}")
            except asyncio.CancelledError:
                break
            except Exception as e:
                logger.error(f"Error in metrics loop: {e}")
    
    async def _cleanup_expired_entries(self):
        """Limpiar entradas expiradas de L1"""
        current_time = time.time()
        expired_keys = []
        
        for key, entry in self.l1_cache.items():
            if entry.is_expired:
                expired_keys.append(key)
        
        for key in expired_keys:
            await self._remove_from_l1(key)
        
        if expired_keys:
            logger.info(f"Cleaned up {len(expired_keys)} expired L1 cache entries")

# Singleton instance
massive_cache = MassiveCacheStrategy()

# Funciones de utilidad
async def get_or_compute(key: str, compute_func, ttl: int = 3600, 
                        levels: List[CacheLevel] = None) -> Any:
    """Obtener del cache o computar si no existe"""
    
    # Intentar obtener del cache
    cached_value = await massive_cache.get(key)
    if cached_value is not None:
        return cached_value
    
    # Computar valor
    computed_value = await compute_func() if asyncio.iscoroutinefunction(compute_func) else compute_func()
    
    # Guardar en cache
    await massive_cache.set(key, computed_value, ttl=ttl, levels=levels)
    
    return computed_value

# Decorador para cache automático
def cache_result(ttl: int = 3600, levels: List[CacheLevel] = None):
    """Decorador para cachear automáticamente resultados de funciones"""
    def decorator(func):
        async def wrapper(*args, **kwargs):
            # Crear clave de cache basada en función y argumentos
            func_name = func.__name__
            args_str = str(args) + str(sorted(kwargs.items()))
            cache_key = f"func:{func_name}:{hashlib.md5(args_str.encode()).hexdigest()}"
            
            return await get_or_compute(
                cache_key,
                lambda: func(*args, **kwargs),
                ttl=ttl,
                levels=levels
            )
        
        return wrapper
    return decorator

if __name__ == "__main__":
    # Ejemplo de uso
    async def main():
        # Inicializar cache
        await massive_cache.initialize()
        
        # Prueba de operaciones básicas
        await massive_cache.set("test_key", {"message": "Hello World"}, ttl=60)
        
        cached_value = await massive_cache.get("test_key")
        print(f"Cached value: {cached_value}")
        
        # Prueba de cache de respuesta AI
        await massive_cache.cache_ai_response(
            "Hola",
            {"user_id": "test_user"},
            {"text": "¡Hola! ¿Cómo estás?", "confidence": 0.95}
        )
        
        ai_response = await massive_cache.get_cached_ai_response(
            "Hola",
            {"user_id": "test_user"}
        )
        print(f"AI Response: {ai_response}")
        
        # Mostrar estadísticas
        stats = massive_cache.get_cache_stats()
        print(json.dumps(stats, indent=2))
        
        await massive_cache.shutdown()
    
    asyncio.run(main())