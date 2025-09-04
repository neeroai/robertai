#!/usr/bin/env python3
"""
Massive Load Balancer for RobertAI WhatsApp Deployment
Distributes conversations across multiple WhatsApp Business API numbers
"""

import asyncio
import hashlib
import time
from typing import Dict, List, Optional, Any, Tuple
from dataclasses import dataclass, field
from datetime import datetime, timedelta
from enum import Enum
import logging
import json
import aioredis
import random

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class NumberStatus(Enum):
    ACTIVE = "active"
    RATE_LIMITED = "rate_limited"
    FAILED = "failed"
    MAINTENANCE = "maintenance"

@dataclass
class WhatsAppNumber:
    """Configuración de número WhatsApp Business"""
    phone_number: str
    phone_number_id: str
    business_account_id: str
    access_token: str
    display_name: str
    status: NumberStatus = NumberStatus.ACTIVE
    current_load: int = 0
    max_load: int = 1000  # Usuarios concurrentes máximos
    rate_limit_count: int = 0
    rate_limit_window_start: float = 0
    last_health_check: datetime = field(default_factory=datetime.now)
    error_count: int = 0
    total_messages: int = 0
    
    @property
    def rate_limit_per_minute(self) -> int:
        """Rate limit por minuto para este número"""
        return 60  # WhatsApp limit per number
    
    @property
    def is_available(self) -> bool:
        """Verifica si el número está disponible para nuevas conversaciones"""
        return (
            self.status == NumberStatus.ACTIVE and
            self.current_load < self.max_load and
            not self.is_rate_limited() and
            self.error_count < 10
        )
    
    def is_rate_limited(self) -> bool:
        """Verifica si el número está siendo rate-limited"""
        current_time = time.time()
        
        # Reset rate limit window si ha pasado 1 minuto
        if current_time - self.rate_limit_window_start > 60:
            self.rate_limit_count = 0
            self.rate_limit_window_start = current_time
            return False
        
        return self.rate_limit_count >= self.rate_limit_per_minute
    
    def increment_rate_limit(self):
        """Incrementar contador de rate limit"""
        current_time = time.time()
        if current_time - self.rate_limit_window_start > 60:
            self.rate_limit_count = 1
            self.rate_limit_window_start = current_time
        else:
            self.rate_limit_count += 1
    
    def record_success(self):
        """Registrar mensaje exitoso"""
        self.total_messages += 1
        self.increment_rate_limit()
        self.error_count = max(0, self.error_count - 1)  # Reduce error count on success
    
    def record_error(self):
        """Registrar error en mensaje"""
        self.error_count += 1
        if self.error_count >= 10:
            self.status = NumberStatus.FAILED
            logger.error(f"Number {self.phone_number} marked as FAILED due to high error rate")

class MassiveLoadBalancer:
    """Load Balancer para miles de usuarios concurrentes"""
    
    def __init__(self, redis_url: str = "redis://localhost:6379"):
        self.numbers: List[WhatsAppNumber] = []
        self.user_assignments: Dict[str, str] = {}  # user_id -> phone_number
        self.redis_url = redis_url
        self.redis_client = None
        self.health_check_interval = 30  # segundos
        self.health_check_task = None
        
    async def initialize(self):
        """Inicializar load balancer"""
        # Conectar a Redis
        self.redis_client = await aioredis.from_url(
            self.redis_url, 
            encoding="utf-8", 
            decode_responses=True
        )
        
        # Cargar asignaciones persistentes desde Redis
        await self._load_user_assignments()
        
        # Iniciar health checks
        self.health_check_task = asyncio.create_task(self._health_check_loop())
        
        logger.info(f"Load balancer initialized with {len(self.numbers)} numbers")
    
    async def shutdown(self):
        """Cerrar load balancer"""
        if self.health_check_task:
            self.health_check_task.cancel()
        
        if self.redis_client:
            await self.redis_client.close()
        
        logger.info("Load balancer shutdown complete")
    
    def add_whatsapp_number(self, 
                           phone_number: str,
                           phone_number_id: str, 
                           business_account_id: str,
                           access_token: str,
                           display_name: str,
                           max_load: int = 1000) -> WhatsAppNumber:
        """Agregar número WhatsApp al pool"""
        
        number = WhatsAppNumber(
            phone_number=phone_number,
            phone_number_id=phone_number_id,
            business_account_id=business_account_id,
            access_token=access_token,
            display_name=display_name,
            max_load=max_load
        )
        
        self.numbers.append(number)
        logger.info(f"Added WhatsApp number: {phone_number} (max_load: {max_load})")
        
        return number
    
    async def assign_number_to_user(self, user_id: str, 
                                   force_reassign: bool = False) -> Optional[WhatsAppNumber]:
        """Asignar número a usuario usando consistent hashing"""
        
        # Si ya tiene asignación y no forzamos reasignación
        if not force_reassign and user_id in self.user_assignments:
            phone_number = self.user_assignments[user_id]
            number = self._get_number_by_phone(phone_number)
            if number and number.is_available:
                return number
        
        # Buscar mejor número disponible
        available_numbers = [n for n in self.numbers if n.is_available]
        
        if not available_numbers:
            logger.error("No available WhatsApp numbers for assignment")
            return None
        
        # Usar consistent hashing para distribución uniforme
        user_hash = hashlib.md5(user_id.encode()).hexdigest()
        hash_int = int(user_hash[:8], 16)
        
        # Ordenar números por carga actual para balanceamiento
        available_numbers.sort(key=lambda x: (x.current_load, x.rate_limit_count))
        
        # Seleccionar número con consistent hashing + load balancing
        number_index = hash_int % len(available_numbers)
        selected_number = available_numbers[number_index]
        
        # Si el número seleccionado está muy cargado, usar el menos cargado
        least_loaded = available_numbers[0]
        if (selected_number.current_load > least_loaded.current_load + 100 and
            least_loaded.current_load < selected_number.max_load * 0.8):
            selected_number = least_loaded
        
        # Actualizar asignación
        self.user_assignments[user_id] = selected_number.phone_number
        selected_number.current_load += 1
        
        # Persistir en Redis
        await self._save_user_assignment(user_id, selected_number.phone_number)
        
        logger.info(f"Assigned user {user_id} to {selected_number.phone_number} "
                   f"(load: {selected_number.current_load}/{selected_number.max_load})")
        
        return selected_number
    
    def _get_number_by_phone(self, phone_number: str) -> Optional[WhatsAppNumber]:
        """Obtener número por teléfono"""
        for number in self.numbers:
            if number.phone_number == phone_number:
                return number
        return None
    
    async def handle_rate_limit(self, user_id: str, 
                               failed_number: WhatsAppNumber) -> Optional[WhatsAppNumber]:
        """Manejar rate limiting reasignando usuario"""
        
        logger.warning(f"Rate limit hit for {failed_number.phone_number}, reassigning user {user_id}")
        
        # Marcar número como rate limited temporalmente
        failed_number.status = NumberStatus.RATE_LIMITED
        
        # Buscar número alternativo
        alternative = await self.assign_number_to_user(user_id, force_reassign=True)
        
        if not alternative:
            logger.error(f"No alternative number available for user {user_id}")
            return None
        
        # Programar rehabilitación del número fallido
        asyncio.create_task(self._rehabilitate_number_after_delay(failed_number, 60))
        
        return alternative
    
    async def _rehabilitate_number_after_delay(self, number: WhatsAppNumber, delay_seconds: int):
        """Rehabilitar número después de un delay"""
        await asyncio.sleep(delay_seconds)
        
        if number.status == NumberStatus.RATE_LIMITED:
            number.status = NumberStatus.ACTIVE
            number.rate_limit_count = 0
            number.rate_limit_window_start = time.time()
            logger.info(f"Rehabilitated number {number.phone_number}")
    
    async def get_optimal_number_for_message(self, user_id: str, 
                                           message_type: str = "text",
                                           priority: str = "normal") -> Tuple[Optional[WhatsAppNumber], str]:
        """Obtener número óptimo para enviar mensaje"""
        
        # Obtener número asignado al usuario
        number = await self.assign_number_to_user(user_id)
        
        if not number:
            return None, "no_numbers_available"
        
        # Verificar disponibilidad específica para el tipo de mensaje
        if number.is_rate_limited():
            # Intentar reasignación por rate limit
            alternative = await self.handle_rate_limit(user_id, number)
            if alternative:
                return alternative, "reassigned_due_to_rate_limit"
            else:
                return None, "all_numbers_rate_limited"
        
        if not number.is_available:
            # Intentar reasignación por disponibilidad
            alternative = await self.assign_number_to_user(user_id, force_reassign=True)
            if alternative:
                return alternative, "reassigned_due_to_unavailability"
            else:
                return None, "no_available_numbers"
        
        return number, "success"
    
    async def record_message_result(self, user_id: str, phone_number: str, 
                                   success: bool, error_details: Optional[str] = None):
        """Registrar resultado de envío de mensaje"""
        
        number = self._get_number_by_phone(phone_number)
        if not number:
            logger.warning(f"Unknown phone number in record_message_result: {phone_number}")
            return
        
        if success:
            number.record_success()
            logger.debug(f"Message success recorded for {phone_number}")
        else:
            number.record_error()
            logger.warning(f"Message error recorded for {phone_number}: {error_details}")
            
            # Si es error de rate limit específicamente
            if error_details and "rate limit" in error_details.lower():
                await self.handle_rate_limit(user_id, number)
    
    async def get_load_balancer_stats(self) -> Dict[str, Any]:
        """Obtener estadísticas del load balancer"""
        
        total_load = sum(n.current_load for n in self.numbers)
        total_capacity = sum(n.max_load for n in self.numbers)
        active_numbers = len([n for n in self.numbers if n.status == NumberStatus.ACTIVE])
        
        number_stats = []
        for number in self.numbers:
            number_stats.append({
                "phone_number": number.phone_number,
                "display_name": number.display_name,
                "status": number.status.value,
                "current_load": number.current_load,
                "max_load": number.max_load,
                "load_percentage": (number.current_load / number.max_load) * 100,
                "rate_limit_count": number.rate_limit_count,
                "error_count": number.error_count,
                "total_messages": number.total_messages,
                "is_available": number.is_available
            })
        
        return {
            "total_assigned_users": len(self.user_assignments),
            "total_current_load": total_load,
            "total_capacity": total_capacity,
            "capacity_utilization": (total_load / total_capacity) * 100 if total_capacity > 0 else 0,
            "active_numbers": active_numbers,
            "total_numbers": len(self.numbers),
            "numbers": number_stats,
            "last_updated": datetime.now().isoformat()
        }
    
    async def _health_check_loop(self):
        """Loop de verificación de salud de números"""
        while True:
            try:
                await asyncio.sleep(self.health_check_interval)
                await self._perform_health_checks()
            except asyncio.CancelledError:
                break
            except Exception as e:
                logger.error(f"Error in health check loop: {e}")
    
    async def _perform_health_checks(self):
        """Realizar verificaciones de salud en todos los números"""
        
        for number in self.numbers:
            try:
                # Actualizar timestamp
                number.last_health_check = datetime.now()
                
                # Verificar si el número debe ser rehabilitado
                if (number.status == NumberStatus.RATE_LIMITED and 
                    not number.is_rate_limited()):
                    number.status = NumberStatus.ACTIVE
                    logger.info(f"Number {number.phone_number} automatically rehabilitated")
                
                # Verificar si hay demasiados errores
                if (number.error_count >= 5 and 
                    number.status == NumberStatus.ACTIVE):
                    number.status = NumberStatus.FAILED
                    logger.warning(f"Number {number.phone_number} marked as FAILED due to errors")
                
                # Auto-recovery para números fallidos después de tiempo
                if (number.status == NumberStatus.FAILED and 
                    number.error_count < 3):  # Si los errores han bajado
                    number.status = NumberStatus.ACTIVE
                    logger.info(f"Number {number.phone_number} auto-recovered from FAILED status")
                
            except Exception as e:
                logger.error(f"Error checking health of {number.phone_number}: {e}")
    
    async def _save_user_assignment(self, user_id: str, phone_number: str):
        """Guardar asignación de usuario en Redis"""
        try:
            await self.redis_client.hset(
                "robertai:user_assignments", 
                user_id, 
                phone_number
            )
            # Expirar después de 24 horas de inactividad
            await self.redis_client.expire("robertai:user_assignments", 86400)
        except Exception as e:
            logger.error(f"Error saving user assignment to Redis: {e}")
    
    async def _load_user_assignments(self):
        """Cargar asignaciones de usuario desde Redis"""
        try:
            assignments = await self.redis_client.hgetall("robertai:user_assignments")
            self.user_assignments = assignments or {}
            logger.info(f"Loaded {len(self.user_assignments)} user assignments from Redis")
        except Exception as e:
            logger.warning(f"Error loading user assignments from Redis: {e}")
            self.user_assignments = {}

# Singleton instance
load_balancer = MassiveLoadBalancer()

# Ejemplo de configuración para despliegue masivo
async def configure_massive_deployment():
    """Configurar load balancer para despliegue masivo"""
    
    # Configurar múltiples números WhatsApp Business
    numbers_config = [
        {
            "phone_number": "+573001234567",
            "phone_number_id": "PHONE_ID_1", 
            "business_account_id": "BUSINESS_ID_1",
            "access_token": "ACCESS_TOKEN_1",
            "display_name": "RobertAI Principal",
            "max_load": 2000
        },
        {
            "phone_number": "+573001234568",
            "phone_number_id": "PHONE_ID_2",
            "business_account_id": "BUSINESS_ID_2", 
            "access_token": "ACCESS_TOKEN_2",
            "display_name": "RobertAI Secundario",
            "max_load": 2000
        },
        {
            "phone_number": "+573001234569",
            "phone_number_id": "PHONE_ID_3",
            "business_account_id": "BUSINESS_ID_3",
            "access_token": "ACCESS_TOKEN_3", 
            "display_name": "RobertAI Respaldo",
            "max_load": 1500
        }
    ]
    
    await load_balancer.initialize()
    
    # Agregar números al load balancer
    for config in numbers_config:
        load_balancer.add_whatsapp_number(**config)
    
    logger.info("Massive deployment configuration completed")
    return load_balancer

# Uso del load balancer
async def send_message_with_load_balancing(user_id: str, message_data: Dict[str, Any]) -> Dict[str, Any]:
    """Enviar mensaje usando load balancing automático"""
    
    # Obtener número óptimo para el usuario
    number, assignment_result = await load_balancer.get_optimal_number_for_message(user_id)
    
    if not number:
        return {
            "success": False,
            "error": f"No available WhatsApp number: {assignment_result}",
            "user_id": user_id
        }
    
    try:
        # Simular envío de mensaje (aquí iría la integración real con WhatsApp API)
        result = await send_whatsapp_message(
            phone_number_id=number.phone_number_id,
            access_token=number.access_token,
            message_data=message_data
        )
        
        # Registrar éxito
        await load_balancer.record_message_result(
            user_id=user_id,
            phone_number=number.phone_number,
            success=True
        )
        
        return {
            "success": True,
            "message_id": result.get("message_id"),
            "phone_number": number.phone_number,
            "assignment_result": assignment_result
        }
        
    except Exception as e:
        # Registrar error
        await load_balancer.record_message_result(
            user_id=user_id,
            phone_number=number.phone_number, 
            success=False,
            error_details=str(e)
        )
        
        return {
            "success": False,
            "error": str(e),
            "phone_number": number.phone_number,
            "user_id": user_id
        }

async def send_whatsapp_message(phone_number_id: str, access_token: str, 
                               message_data: Dict[str, Any]) -> Dict[str, Any]:
    """Placeholder para envío real de mensaje WhatsApp"""
    # Aquí iría la implementación real de la WhatsApp Business API
    await asyncio.sleep(0.1)  # Simular latencia de API
    
    if random.random() < 0.05:  # 5% de tasa de error simulada
        raise Exception("Simulated API error")
    
    return {
        "message_id": f"msg_{int(time.time())}_{random.randint(1000, 9999)}",
        "status": "sent"
    }

if __name__ == "__main__":
    # Ejemplo de uso
    async def main():
        # Configurar para despliegue masivo
        lb = await configure_massive_deployment()
        
        # Simular asignación de usuarios
        test_users = [f"user_{i}" for i in range(100)]
        
        for user_id in test_users:
            number = await lb.assign_number_to_user(user_id)
            print(f"User {user_id} assigned to {number.phone_number if number else 'NONE'}")
        
        # Mostrar estadísticas
        stats = await lb.get_load_balancer_stats()
        print(json.dumps(stats, indent=2))
        
        await lb.shutdown()
    
    asyncio.run(main())