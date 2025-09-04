#!/usr/bin/env python3
"""
Real-time Monitoring and Alerting System for RobertAI Massive Deployment
Comprehensive monitoring solution for thousands of concurrent users
"""

import asyncio
import json
import time
import logging
from typing import Dict, Any, Optional, List, Callable, Union
from dataclasses import dataclass, field, asdict
from datetime import datetime, timedelta
from enum import Enum
import aiohttp
import aioredis
from redis.asyncio import Redis
import psutil
import statistics
from collections import deque, defaultdict
import subprocess
import os

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class AlertLevel(Enum):
    INFO = "info"
    WARNING = "warning"
    ERROR = "error"
    CRITICAL = "critical"

class MetricType(Enum):
    COUNTER = "counter"
    GAUGE = "gauge"
    HISTOGRAM = "histogram"
    SUMMARY = "summary"

@dataclass
class Metric:
    """Métrica individual con historial"""
    name: str
    type: MetricType
    value: float
    timestamp: float = field(default_factory=time.time)
    labels: Dict[str, str] = field(default_factory=dict)
    unit: str = ""
    description: str = ""

@dataclass
class AlertRule:
    """Regla de alerta configurable"""
    name: str
    metric_name: str
    condition: str  # "gt", "lt", "eq", "ne", "gte", "lte"
    threshold: float
    duration_seconds: int = 60  # Duración antes de disparar alerta
    level: AlertLevel = AlertLevel.WARNING
    message_template: str = ""
    cooldown_seconds: int = 300  # 5 minutos de cooldown
    enabled: bool = True
    labels: Dict[str, str] = field(default_factory=dict)

@dataclass
class Alert:
    """Alerta disparada"""
    rule_name: str
    level: AlertLevel
    message: str
    metric_value: float
    threshold: float
    timestamp: datetime = field(default_factory=datetime.now)
    labels: Dict[str, str] = field(default_factory=dict)
    resolved: bool = False
    resolved_at: Optional[datetime] = None

class RealTimeMonitor:
    """Monitor en tiempo real para despliegue masivo"""
    
    def __init__(self,
                 redis_url: str = "redis://localhost:6379",
                 metrics_retention_hours: int = 24,
                 alert_retention_hours: int = 72):
        
        self.redis_url = redis_url
        self.metrics_retention_hours = metrics_retention_hours
        self.alert_retention_hours = alert_retention_hours
        
        # Storage
        self.redis_client: Optional[Redis] = None
        self.metrics: Dict[str, deque] = defaultdict(lambda: deque(maxlen=10000))
        self.alerts: List[Alert] = []
        self.alert_rules: Dict[str, AlertRule] = {}
        
        # Estado de alertas activas
        self.active_alerts: Dict[str, Alert] = {}
        self.alert_cooldowns: Dict[str, float] = {}
        
        # Handlers de alertas
        self.alert_handlers: Dict[AlertLevel, List[Callable]] = {
            level: [] for level in AlertLevel
        }
        
        # Tasks de background
        self.monitoring_task: Optional[asyncio.Task] = None
        self.alert_processor_task: Optional[asyncio.Task] = None
        self.metrics_cleanup_task: Optional[asyncio.Task] = None
        
        # Sistema corriendo
        self.running = False
        
        # Métricas del sistema
        self.system_metrics_enabled = True
        self.last_cpu_times = None
        
        # Dashboard data
        self.dashboard_data = {
            "users": {"active": 0, "total": 0, "peak": 0},
            "messages": {"per_second": 0, "total": 0, "failed": 0},
            "performance": {"avg_response_time": 0, "p99_response_time": 0},
            "system": {"cpu_usage": 0, "memory_usage": 0, "disk_usage": 0},
            "queues": {"pending": 0, "processing": 0, "failed": 0},
            "cache": {"hit_rate": 0, "size": 0},
            "alerts": {"active": 0, "total_today": 0}
        }
    
    async def initialize(self):
        """Inicializar sistema de monitoreo"""
        
        # Conectar a Redis
        self.redis_client = await aioredis.from_url(
            self.redis_url,
            encoding="utf-8",
            decode_responses=True
        )
        
        # Configurar alertas por defecto
        await self._setup_default_alert_rules()
        
        # Cargar alertas persistentes
        await self._load_persistent_alerts()
        
        logger.info("Real-time monitoring system initialized")
    
    async def start(self):
        """Iniciar monitoreo en tiempo real"""
        if self.running:
            logger.warning("Monitoring already running")
            return
        
        self.running = True
        
        # Iniciar tasks de background
        self.monitoring_task = asyncio.create_task(self._monitoring_loop())
        self.alert_processor_task = asyncio.create_task(self._alert_processor_loop())
        self.metrics_cleanup_task = asyncio.create_task(self._metrics_cleanup_loop())
        
        logger.info("Real-time monitoring started")
    
    async def stop(self):
        """Detener monitoreo"""
        self.running = False
        
        # Cancelar tasks
        tasks = [
            self.monitoring_task,
            self.alert_processor_task,
            self.metrics_cleanup_task
        ]
        
        for task in tasks:
            if task:
                task.cancel()
        
        await asyncio.gather(*tasks, return_exceptions=True)
        
        # Persistir alertas
        await self._persist_alerts()
        
        # Cerrar conexiones
        if self.redis_client:
            await self.redis_client.close()
        
        logger.info("Real-time monitoring stopped")
    
    # Gestión de métricas
    
    async def record_metric(self, name: str, value: float, 
                           metric_type: MetricType = MetricType.GAUGE,
                           labels: Optional[Dict[str, str]] = None,
                           unit: str = "",
                           description: str = ""):
        """Registrar métrica"""
        
        metric = Metric(
            name=name,
            type=metric_type,
            value=value,
            labels=labels or {},
            unit=unit,
            description=description
        )
        
        # Agregar a historial en memoria
        self.metrics[name].append(metric)
        
        # Persistir en Redis
        await self._persist_metric(metric)
        
        # Evaluar reglas de alerta
        await self._evaluate_alert_rules(metric)
    
    async def increment_counter(self, name: str, amount: float = 1.0,
                               labels: Optional[Dict[str, str]] = None):
        """Incrementar contador"""
        
        # Obtener valor actual
        current_value = await self.get_current_metric_value(name)
        new_value = current_value + amount
        
        await self.record_metric(
            name=name,
            value=new_value,
            metric_type=MetricType.COUNTER,
            labels=labels
        )
    
    async def set_gauge(self, name: str, value: float,
                       labels: Optional[Dict[str, str]] = None):
        """Establecer valor de gauge"""
        
        await self.record_metric(
            name=name,
            value=value,
            metric_type=MetricType.GAUGE,
            labels=labels
        )
    
    async def record_histogram(self, name: str, value: float,
                              labels: Optional[Dict[str, str]] = None):
        """Registrar valor en histograma"""
        
        await self.record_metric(
            name=name,
            value=value,
            metric_type=MetricType.HISTOGRAM,
            labels=labels
        )
    
    async def get_current_metric_value(self, name: str) -> float:
        """Obtener valor actual de métrica"""
        
        if name in self.metrics and self.metrics[name]:
            return self.metrics[name][-1].value
        
        # Buscar en Redis
        try:
            latest_key = f"robertai:metrics:{name}:latest"
            value = await self.redis_client.get(latest_key)
            return float(value) if value else 0.0
        except:
            return 0.0
    
    async def get_metric_history(self, name: str, 
                                hours: int = 1) -> List[Metric]:
        """Obtener historial de métrica"""
        
        end_time = time.time()
        start_time = end_time - (hours * 3600)
        
        history = []
        
        # Filtrar métricas en memoria
        if name in self.metrics:
            for metric in self.metrics[name]:
                if metric.timestamp >= start_time:
                    history.append(metric)
        
        # Complementar con datos de Redis si es necesario
        if len(history) < 10:  # Si hay pocos datos en memoria
            redis_history = await self._get_metric_history_from_redis(name, start_time, end_time)
            history.extend(redis_history)
        
        # Ordenar por timestamp
        history.sort(key=lambda x: x.timestamp)
        
        return history
    
    async def get_metric_stats(self, name: str, hours: int = 1) -> Dict[str, float]:
        """Obtener estadísticas de métrica"""
        
        history = await self.get_metric_history(name, hours)
        
        if not history:
            return {"count": 0, "avg": 0, "min": 0, "max": 0, "p50": 0, "p90": 0, "p99": 0}
        
        values = [m.value for m in history]
        
        return {
            "count": len(values),
            "avg": statistics.mean(values),
            "min": min(values),
            "max": max(values),
            "p50": statistics.quantiles(values, n=2)[0] if len(values) > 1 else values[0],
            "p90": statistics.quantiles(values, n=10)[8] if len(values) > 1 else values[0],
            "p99": statistics.quantiles(values, n=100)[98] if len(values) > 1 else values[0]
        }
    
    # Sistema de alertas
    
    def add_alert_rule(self, rule: AlertRule):
        """Agregar regla de alerta"""
        self.alert_rules[rule.name] = rule
        logger.info(f"Added alert rule: {rule.name}")
    
    def remove_alert_rule(self, rule_name: str):
        """Remover regla de alerta"""
        if rule_name in self.alert_rules:
            del self.alert_rules[rule_name]
            logger.info(f"Removed alert rule: {rule_name}")
    
    def add_alert_handler(self, level: AlertLevel, handler: Callable):
        """Agregar handler de alerta"""
        self.alert_handlers[level].append(handler)
        logger.info(f"Added alert handler for level {level.value}")
    
    async def _evaluate_alert_rules(self, metric: Metric):
        """Evaluar reglas de alerta para métrica"""
        
        for rule_name, rule in self.alert_rules.items():
            if not rule.enabled or rule.metric_name != metric.name:
                continue
            
            # Verificar cooldown
            if rule_name in self.alert_cooldowns:
                if time.time() - self.alert_cooldowns[rule_name] < rule.cooldown_seconds:
                    continue
            
            # Evaluar condición
            should_alert = self._evaluate_condition(metric.value, rule.condition, rule.threshold)
            
            if should_alert:
                # Verificar duración si es necesaria
                if rule.duration_seconds > 0:
                    if not await self._check_condition_duration(rule, metric):
                        continue
                
                # Disparar alerta
                await self._fire_alert(rule, metric)
    
    def _evaluate_condition(self, value: float, condition: str, threshold: float) -> bool:
        """Evaluar condición de alerta"""
        
        conditions = {
            "gt": value > threshold,
            "gte": value >= threshold,
            "lt": value < threshold,
            "lte": value <= threshold,
            "eq": abs(value - threshold) < 0.001,  # Para flotantes
            "ne": abs(value - threshold) >= 0.001
        }
        
        return conditions.get(condition, False)
    
    async def _check_condition_duration(self, rule: AlertRule, current_metric: Metric) -> bool:
        """Verificar si condición se mantiene por duración requerida"""
        
        # Obtener métricas de los últimos N segundos
        start_time = current_metric.timestamp - rule.duration_seconds
        history = await self.get_metric_history(rule.metric_name, hours=1)
        
        # Filtrar por tiempo
        recent_metrics = [m for m in history if m.timestamp >= start_time]
        
        if len(recent_metrics) < 2:  # Insuficientes datos
            return False
        
        # Verificar que todos los valores en duración cumplan condición
        for metric in recent_metrics:
            if not self._evaluate_condition(metric.value, rule.condition, rule.threshold):
                return False
        
        return True
    
    async def _fire_alert(self, rule: AlertRule, metric: Metric):
        """Disparar alerta"""
        
        # Crear mensaje de alerta
        message = rule.message_template or f"Alert {rule.name}: {metric.name} is {metric.value} (threshold: {rule.threshold})"
        
        alert = Alert(
            rule_name=rule.name,
            level=rule.level,
            message=message,
            metric_value=metric.value,
            threshold=rule.threshold,
            labels={**rule.labels, **metric.labels}
        )
        
        # Agregar a listas
        self.alerts.append(alert)
        self.active_alerts[rule.name] = alert
        
        # Establecer cooldown
        self.alert_cooldowns[rule.name] = time.time()
        
        # Enviar a handlers
        await self._send_alert_to_handlers(alert)
        
        # Persistir alerta
        await self._persist_alert(alert)
        
        logger.warning(f"ALERT FIRED: {alert.message}")
    
    async def _send_alert_to_handlers(self, alert: Alert):
        """Enviar alerta a handlers registrados"""
        
        handlers = self.alert_handlers.get(alert.level, [])
        
        for handler in handlers:
            try:
                if asyncio.iscoroutinefunction(handler):
                    await handler(alert)
                else:
                    handler(alert)
            except Exception as e:
                logger.error(f"Error in alert handler: {e}")
    
    async def resolve_alert(self, rule_name: str):
        """Resolver alerta activa"""
        
        if rule_name in self.active_alerts:
            alert = self.active_alerts[rule_name]
            alert.resolved = True
            alert.resolved_at = datetime.now()
            
            del self.active_alerts[rule_name]
            
            logger.info(f"Resolved alert: {rule_name}")
    
    # Métricas del sistema
    
    async def collect_system_metrics(self):
        """Recopilar métricas del sistema"""
        
        if not self.system_metrics_enabled:
            return
        
        try:
            # CPU
            cpu_percent = psutil.cpu_percent(interval=None)
            await self.set_gauge("system_cpu_usage_percent", cpu_percent)
            
            # Memoria
            memory = psutil.virtual_memory()
            await self.set_gauge("system_memory_usage_percent", memory.percent)
            await self.set_gauge("system_memory_used_bytes", memory.used)
            await self.set_gauge("system_memory_available_bytes", memory.available)
            
            # Disco
            disk = psutil.disk_usage('/')
            disk_percent = (disk.used / disk.total) * 100
            await self.set_gauge("system_disk_usage_percent", disk_percent)
            await self.set_gauge("system_disk_used_bytes", disk.used)
            await self.set_gauge("system_disk_free_bytes", disk.free)
            
            # Procesos
            process_count = len(psutil.pids())
            await self.set_gauge("system_process_count", process_count)
            
            # Load average (solo Linux/Mac)
            try:
                load_avg = os.getloadavg()
                await self.set_gauge("system_load_average_1m", load_avg[0])
                await self.set_gauge("system_load_average_5m", load_avg[1])
                await self.set_gauge("system_load_average_15m", load_avg[2])
            except:
                pass
            
        except Exception as e:
            logger.error(f"Error collecting system metrics: {e}")
    
    async def collect_application_metrics(self, load_balancer=None, cache=None, queue=None):
        """Recopilar métricas de la aplicación"""
        
        try:
            # Load balancer metrics
            if load_balancer:
                lb_stats = await load_balancer.get_load_balancer_stats()
                
                await self.set_gauge("lb_total_users", lb_stats["total_assigned_users"])
                await self.set_gauge("lb_capacity_utilization", lb_stats["capacity_utilization"])
                await self.set_gauge("lb_active_numbers", lb_stats["active_numbers"])
                
                # Métricas por número
                for number_stat in lb_stats.get("numbers", []):
                    labels = {"phone_number": number_stat["phone_number"]}
                    await self.set_gauge("lb_number_load", number_stat["current_load"], labels)
                    await self.set_gauge("lb_number_errors", number_stat["error_count"], labels)
            
            # Cache metrics
            if cache:
                cache_stats = cache.get_cache_stats()
                
                await self.set_gauge("cache_hit_rate", cache_stats["metrics"]["hit_rate"])
                await self.set_gauge("cache_l1_hits", cache_stats["metrics"]["l1_hits"])
                await self.set_gauge("cache_l2_hits", cache_stats["metrics"]["l2_hits"])
                await self.set_gauge("cache_size", cache_stats["l1_cache"]["size"])
                await self.set_gauge("cache_memory_usage", cache_stats["l1_cache"]["size_bytes"])
            
            # Queue metrics
            if queue:
                queue_stats = await queue.get_queue_status()
                
                await self.set_gauge("queue_pending_messages", queue_stats["total_pending_messages"])
                await self.set_gauge("queue_active_workers", queue_stats["active_workers"])
                await self.set_gauge("queue_retry_size", queue_stats["retry_queue_size"])
                await self.set_gauge("queue_dead_letter_size", queue_stats["dead_letter_queue_size"])
                await self.set_gauge("queue_messages_per_second", queue_stats["stats"]["messages_per_second"])
            
        except Exception as e:
            logger.error(f"Error collecting application metrics: {e}")
    
    # Dashboard y APIs
    
    async def get_dashboard_data(self) -> Dict[str, Any]:
        """Obtener datos para dashboard"""
        
        try:
            # Actualizar datos del dashboard
            self.dashboard_data.update({
                "users": {
                    "active": await self.get_current_metric_value("lb_total_users"),
                    "total": await self.get_current_metric_value("total_users_registered"),
                    "peak": (await self.get_metric_stats("lb_total_users", 24))["max"]
                },
                "messages": {
                    "per_second": await self.get_current_metric_value("queue_messages_per_second"),
                    "total": await self.get_current_metric_value("messages_total_processed"),
                    "failed": await self.get_current_metric_value("messages_total_failed")
                },
                "performance": {
                    "avg_response_time": await self.get_current_metric_value("response_time_avg"),
                    "p99_response_time": (await self.get_metric_stats("response_time", 1))["p99"]
                },
                "system": {
                    "cpu_usage": await self.get_current_metric_value("system_cpu_usage_percent"),
                    "memory_usage": await self.get_current_metric_value("system_memory_usage_percent"),
                    "disk_usage": await self.get_current_metric_value("system_disk_usage_percent")
                },
                "queues": {
                    "pending": await self.get_current_metric_value("queue_pending_messages"),
                    "processing": await self.get_current_metric_value("queue_active_workers"),
                    "failed": await self.get_current_metric_value("queue_dead_letter_size")
                },
                "cache": {
                    "hit_rate": await self.get_current_metric_value("cache_hit_rate"),
                    "size": await self.get_current_metric_value("cache_size")
                },
                "alerts": {
                    "active": len(self.active_alerts),
                    "total_today": len([a for a in self.alerts if a.timestamp.date() == datetime.now().date()])
                },
                "last_updated": datetime.now().isoformat()
            })
            
        except Exception as e:
            logger.error(f"Error updating dashboard data: {e}")
        
        return self.dashboard_data
    
    async def get_alerts_summary(self) -> Dict[str, Any]:
        """Obtener resumen de alertas"""
        
        active_alerts = list(self.active_alerts.values())
        recent_alerts = [a for a in self.alerts if a.timestamp > datetime.now() - timedelta(hours=24)]
        
        return {
            "active_alerts": [asdict(alert) for alert in active_alerts],
            "recent_alerts": [asdict(alert) for alert in recent_alerts[-50:]],  # Últimas 50
            "alert_counts_by_level": {
                level.value: len([a for a in recent_alerts if a.level == level])
                for level in AlertLevel
            },
            "total_alerts_today": len([a for a in recent_alerts if a.timestamp.date() == datetime.now().date()]),
            "last_updated": datetime.now().isoformat()
        }
    
    # Background tasks
    
    async def _monitoring_loop(self):
        """Loop principal de monitoreo"""
        
        while self.running:
            try:
                # Recopilar métricas del sistema
                await self.collect_system_metrics()
                
                # Actualizar datos del dashboard
                await self.get_dashboard_data()
                
                await asyncio.sleep(10)  # Cada 10 segundos
                
            except asyncio.CancelledError:
                break
            except Exception as e:
                logger.error(f"Error in monitoring loop: {e}")
                await asyncio.sleep(5)
    
    async def _alert_processor_loop(self):
        """Loop de procesamiento de alertas"""
        
        while self.running:
            try:
                # Verificar resolución automática de alertas
                await self._check_alert_resolution()
                
                # Limpiar alertas antiguas
                await self._cleanup_old_alerts()
                
                await asyncio.sleep(30)  # Cada 30 segundos
                
            except asyncio.CancelledError:
                break
            except Exception as e:
                logger.error(f"Error in alert processor: {e}")
                await asyncio.sleep(10)
    
    async def _metrics_cleanup_loop(self):
        """Loop de limpieza de métricas"""
        
        while self.running:
            try:
                await self._cleanup_old_metrics()
                await asyncio.sleep(3600)  # Cada hora
                
            except asyncio.CancelledError:
                break
            except Exception as e:
                logger.error(f"Error in metrics cleanup: {e}")
    
    async def _check_alert_resolution(self):
        """Verificar resolución automática de alertas"""
        
        for rule_name, alert in list(self.active_alerts.items()):
            rule = self.alert_rules.get(rule_name)
            if not rule:
                continue
            
            # Obtener valor actual de la métrica
            current_value = await self.get_current_metric_value(rule.metric_name)
            
            # Verificar si la condición ya no se cumple
            if not self._evaluate_condition(current_value, rule.condition, rule.threshold):
                await self.resolve_alert(rule_name)
    
    async def _cleanup_old_alerts(self):
        """Limpiar alertas antiguas"""
        
        cutoff_time = datetime.now() - timedelta(hours=self.alert_retention_hours)
        
        # Filtrar alertas antiguas
        self.alerts = [a for a in self.alerts if a.timestamp > cutoff_time]
    
    async def _cleanup_old_metrics(self):
        """Limpiar métricas antiguas"""
        
        cutoff_time = time.time() - (self.metrics_retention_hours * 3600)
        
        for name, metric_history in self.metrics.items():
            # Filtrar métricas antiguas
            while metric_history and metric_history[0].timestamp < cutoff_time:
                metric_history.popleft()
    
    # Persistencia
    
    async def _persist_metric(self, metric: Metric):
        """Persistir métrica en Redis"""
        
        try:
            # Guardar valor más reciente
            latest_key = f"robertai:metrics:{metric.name}:latest"
            await self.redis_client.set(latest_key, str(metric.value), ex=3600)
            
            # Guardar en serie temporal (opcional para métricas críticas)
            if metric.type in [MetricType.COUNTER, MetricType.GAUGE]:
                ts_key = f"robertai:metrics:{metric.name}:timeseries"
                timestamp = int(metric.timestamp)
                await self.redis_client.zadd(ts_key, {str(metric.value): timestamp})
                
                # Mantener solo últimas N entradas
                await self.redis_client.zremrangebyrank(ts_key, 0, -1000)
                await self.redis_client.expire(ts_key, self.metrics_retention_hours * 3600)
        
        except Exception as e:
            logger.error(f"Error persisting metric: {e}")
    
    async def _persist_alert(self, alert: Alert):
        """Persistir alerta en Redis"""
        
        try:
            key = f"robertai:alerts:{alert.timestamp.isoformat()}:{alert.rule_name}"
            data = json.dumps(asdict(alert), default=str)
            ttl = self.alert_retention_hours * 3600
            
            await self.redis_client.setex(key, ttl, data)
        
        except Exception as e:
            logger.error(f"Error persisting alert: {e}")
    
    async def _persist_alerts(self):
        """Persistir todas las alertas activas"""
        
        for alert in self.active_alerts.values():
            await self._persist_alert(alert)
    
    async def _load_persistent_alerts(self):
        """Cargar alertas persistentes desde Redis"""
        
        try:
            pattern = "robertai:alerts:*"
            keys = []
            
            async for key in self.redis_client.scan_iter(match=pattern):
                keys.append(key)
            
            for key in keys[-100:]:  # Últimas 100 alertas
                try:
                    data = await self.redis_client.get(key)
                    if data:
                        alert_dict = json.loads(data)
                        alert = Alert(**alert_dict)
                        
                        if not alert.resolved:
                            self.active_alerts[alert.rule_name] = alert
                        
                        self.alerts.append(alert)
                
                except Exception as e:
                    logger.warning(f"Error loading alert {key}: {e}")
            
            logger.info(f"Loaded {len(self.alerts)} alerts from Redis")
            
        except Exception as e:
            logger.error(f"Error loading persistent alerts: {e}")
    
    async def _get_metric_history_from_redis(self, name: str, start_time: float, end_time: float) -> List[Metric]:
        """Obtener historial de métrica desde Redis"""
        
        try:
            ts_key = f"robertai:metrics:{name}:timeseries"
            
            # Obtener datos del rango temporal
            results = await self.redis_client.zrangebyscore(
                ts_key, 
                start_time, 
                end_time, 
                withscores=True
            )
            
            metrics = []
            for value_str, timestamp in results:
                try:
                    metric = Metric(
                        name=name,
                        type=MetricType.GAUGE,  # Asumir gauge por defecto
                        value=float(value_str),
                        timestamp=timestamp
                    )
                    metrics.append(metric)
                except:
                    continue
            
            return metrics
            
        except Exception as e:
            logger.error(f"Error getting metric history from Redis: {e}")
            return []
    
    async def _setup_default_alert_rules(self):
        """Configurar reglas de alerta por defecto"""
        
        default_rules = [
            AlertRule(
                name="high_cpu_usage",
                metric_name="system_cpu_usage_percent",
                condition="gt",
                threshold=80.0,
                duration_seconds=60,
                level=AlertLevel.WARNING,
                message_template="High CPU usage: {value}%"
            ),
            AlertRule(
                name="critical_cpu_usage", 
                metric_name="system_cpu_usage_percent",
                condition="gt",
                threshold=95.0,
                duration_seconds=30,
                level=AlertLevel.CRITICAL,
                message_template="CRITICAL: CPU usage at {value}%"
            ),
            AlertRule(
                name="high_memory_usage",
                metric_name="system_memory_usage_percent",
                condition="gt", 
                threshold=85.0,
                duration_seconds=120,
                level=AlertLevel.WARNING,
                message_template="High memory usage: {value}%"
            ),
            AlertRule(
                name="queue_backup",
                metric_name="queue_pending_messages",
                condition="gt",
                threshold=1000.0,
                duration_seconds=60,
                level=AlertLevel.ERROR,
                message_template="Message queue backup: {value} pending messages"
            ),
            AlertRule(
                name="low_cache_hit_rate",
                metric_name="cache_hit_rate",
                condition="lt",
                threshold=0.7,  # 70%
                duration_seconds=300,
                level=AlertLevel.WARNING,
                message_template="Low cache hit rate: {value}"
            ),
            AlertRule(
                name="high_response_time",
                metric_name="response_time_avg",
                condition="gt",
                threshold=5.0,  # 5 segundos
                duration_seconds=120,
                level=AlertLevel.ERROR,
                message_template="High average response time: {value}s"
            )
        ]
        
        for rule in default_rules:
            self.add_alert_rule(rule)
        
        logger.info(f"Added {len(default_rules)} default alert rules")

# Singleton instance
real_time_monitor = RealTimeMonitor()

# Handlers de alerta por defecto
async def slack_alert_handler(alert: Alert):
    """Handler de Slack para alertas"""
    
    slack_webhook_url = os.getenv('SLACK_WEBHOOK_URL')
    if not slack_webhook_url:
        return
    
    color_map = {
        AlertLevel.INFO: "#36a64f",
        AlertLevel.WARNING: "#ffb347", 
        AlertLevel.ERROR: "#ff6b6b",
        AlertLevel.CRITICAL: "#ff4757"
    }
    
    payload = {
        "attachments": [
            {
                "color": color_map.get(alert.level, "#000000"),
                "title": f"🚨 RobertAI Alert - {alert.level.value.upper()}",
                "text": alert.message,
                "fields": [
                    {
                        "title": "Metric Value",
                        "value": str(alert.metric_value),
                        "short": True
                    },
                    {
                        "title": "Threshold", 
                        "value": str(alert.threshold),
                        "short": True
                    },
                    {
                        "title": "Time",
                        "value": alert.timestamp.strftime('%Y-%m-%d %H:%M:%S'),
                        "short": True
                    },
                    {
                        "title": "Rule",
                        "value": alert.rule_name,
                        "short": True
                    }
                ],
                "footer": "RobertAI Monitoring",
                "ts": int(alert.timestamp.timestamp())
            }
        ]
    }
    
    try:
        async with aiohttp.ClientSession() as session:
            async with session.post(slack_webhook_url, json=payload) as response:
                if response.status != 200:
                    logger.error(f"Failed to send Slack alert: {response.status}")
    except Exception as e:
        logger.error(f"Error sending Slack alert: {e}")

def console_alert_handler(alert: Alert):
    """Handler de consola para alertas"""
    
    level_symbols = {
        AlertLevel.INFO: "ℹ️",
        AlertLevel.WARNING: "⚠️",
        AlertLevel.ERROR: "❌",
        AlertLevel.CRITICAL: "🔥"
    }
    
    symbol = level_symbols.get(alert.level, "📢")
    
    print(f"\n{symbol} ALERT [{alert.level.value.upper()}] - {alert.timestamp}")
    print(f"Rule: {alert.rule_name}")
    print(f"Message: {alert.message}")
    print(f"Value: {alert.metric_value} (threshold: {alert.threshold})")
    print("-" * 50)

# Configuración inicial
async def setup_monitoring():
    """Configurar sistema de monitoreo"""
    
    await real_time_monitor.initialize()
    
    # Registrar handlers de alertas
    real_time_monitor.add_alert_handler(AlertLevel.WARNING, slack_alert_handler)
    real_time_monitor.add_alert_handler(AlertLevel.ERROR, slack_alert_handler)
    real_time_monitor.add_alert_handler(AlertLevel.CRITICAL, slack_alert_handler)
    
    # Handler de consola para todas las alertas
    for level in AlertLevel:
        real_time_monitor.add_alert_handler(level, console_alert_handler)
    
    await real_time_monitor.start()
    
    return real_time_monitor

if __name__ == "__main__":
    # Ejemplo de uso
    async def main():
        monitor = await setup_monitoring()
        
        # Simular métricas
        for i in range(100):
            await monitor.set_gauge("test_cpu", 50 + (i % 50))
            await monitor.increment_counter("test_messages", 5)
            await asyncio.sleep(1)
        
        # Mostrar dashboard
        dashboard = await monitor.get_dashboard_data()
        print(json.dumps(dashboard, indent=2))
        
        await monitor.stop()
    
    asyncio.run(main())