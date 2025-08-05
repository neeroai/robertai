# 10 - Webhooks y Eventos

## 🔔 Arquitectura de Eventos

### Flujo Bidireccional de Eventos

```
┌─────────────────────────────────────────────────────────────┐
│                    Bird.com Platform                          │
│  ┌─────────────────────────────────────────────────────┐   │
│  │                  Event Bus                            │   │
│  │  • Conversation Events  • System Events              │   │
│  │  • AI Events           • Integration Events          │   │
│  └────────────────┬─────────────────────────────────────┘   │
│                   │                                          │
│         ┌─────────▼─────────┐      ┌──────────────────┐    │
│         │ Outbound Webhooks │      │ Inbound Webhooks │    │
│         │ (Bird → External) │      │ (External → Bird) │    │
│         └─────────┬─────────┘      └─────────▲────────┘    │
└───────────────────┼──────────────────────────┼──────────────┘
                    │                          │
                    ▼                          │
┌─────────────────────────────────────────────┴───────────────┐
│                    External Systems                          │
│  • KOAJ API       • Analytics Platform    • CRM             │
│  • Inventory      • Payment Gateway       • Monitoring      │
└─────────────────────────────────────────────────────────────┘
```

## 📤 Outbound Webhooks (Bird → External)

### Configuración de Webhooks Salientes

```python
# Configuración en Bird.com
webhook_config = {
    "name": "koaj_events_webhook",
    "url": "https://api.neero.link/v1/bird/events/webhook",
    "events": [
        "conversation.started",
        "conversation.message.received",
        "conversation.message.sent",
        "conversation.ended",
        "conversation.escalated",
        "ai.intent.detected",
        "ai.action.executed",
        "ai.recommendation.generated"
    ],
    "headers": {
        "Authorization": "Bearer ${WEBHOOK_TOKEN}",
        "Content-Type": "application/json",
        "X-Bird-Webhook-Version": "1.0"
    },
    "retry_policy": {
        "max_attempts": 3,
        "backoff_type": "exponential",
        "initial_delay": 1000,
        "max_delay": 30000
    },
    "security": {
        "signing_algorithm": "HMAC-SHA256",
        "include_signature": True
    }
}
```

### Tipos de Eventos y Payloads

#### 1. Eventos de Conversación

```python
# conversation.started
{
    "event_id": "evt_123456789",
    "event_type": "conversation.started",
    "timestamp": "2025-07-29T10:30:00Z",
    "data": {
        "conversation_id": "conv_abc123",
        "channel": "whatsapp",
        "user": {
            "id": "user_xyz789",
            "phone": "+57301234567",
            "name": "María García",
            "is_new": False,
            "metadata": {
                "segment": "vip",
                "last_purchase": "2025-07-15"
            }
        },
        "context": {
            "entry_point": "qr_code",
            "campaign": "summer_sale",
            "location": "colombia"
        }
    }
}

# conversation.message.received
{
    "event_id": "evt_234567890",
    "event_type": "conversation.message.received",
    "timestamp": "2025-07-29T10:31:00Z",
    "data": {
        "conversation_id": "conv_abc123",
        "message_id": "msg_def456",
        "content": {
            "type": "text",
            "text": "Busco un vestido negro para una cena",
            "language": "es"
        },
        "user": {
            "id": "user_xyz789"
        },
        "metadata": {
            "sentiment": "positive",
            "confidence": 0.92
        }
    }
}

# conversation.ended
{
    "event_id": "evt_345678901",
    "event_type": "conversation.ended",
    "timestamp": "2025-07-29T10:45:00Z",
    "data": {
        "conversation_id": "conv_abc123",
        "duration": 900,  # segundos
        "message_count": 24,
        "resolution": {
            "status": "resolved",
            "outcome": "purchase_completed",
            "satisfaction_score": 5
        },
        "metrics": {
            "ai_messages": 12,
            "user_messages": 12,
            "actions_executed": 3,
            "products_shown": 8,
            "escalated": False
        }
    }
}
```

#### 2. Eventos de AI

```python
# ai.intent.detected
{
    "event_id": "evt_456789012",
    "event_type": "ai.intent.detected",
    "timestamp": "2025-07-29T10:31:05Z",
    "data": {
        "conversation_id": "conv_abc123",
        "message_id": "msg_def456",
        "intent": {
            "name": "product_search",
            "confidence": 0.89,
            "parameters": {
                "product_type": "vestido",
                "color": "negro",
                "occasion": "cena"
            }
        },
        "entities": [
            {"type": "product", "value": "vestido", "position": [8, 15]},
            {"type": "color", "value": "negro", "position": [16, 21]},
            {"type": "occasion", "value": "cena", "position": [31, 35]}
        ]
    }
}

# ai.action.executed
{
    "event_id": "evt_567890123",
    "event_type": "ai.action.executed",
    "timestamp": "2025-07-29T10:31:10Z",
    "data": {
        "conversation_id": "conv_abc123",
        "action": {
            "name": "search_products",
            "parameters": {
                "query": "vestido negro elegante",
                "filters": {
                    "category": "PRENDAS/MUJER/VESTIDOS",
                    "color": "negro",
                    "price_range": {"min": 100000, "max": 500000}
                }
            },
            "result": {
                "success": True,
                "products_found": 5,
                "execution_time": 245  # ms
            }
        }
    }
}
```

## 📥 Inbound Webhooks (External → Bird)

### Endpoint de Recepción

```python
# POST /bird/events/webhook
class BirdWebhookReceiver:
    def __init__(self):
        self.event_handlers = {
            'inventory.updated': self.handle_inventory_update,
            'price.changed': self.handle_price_change,
            'product.added': self.handle_new_product,
            'product.removed': self.handle_product_removal,
            'order.completed': self.handle_order_completion,
            'campaign.started': self.handle_campaign_start
        }
    
    async def receive_webhook(self, request):
        # Verificar firma
        if not self.verify_signature(request):
            return {'error': 'Invalid signature'}, 401
        
        # Parsear evento
        event = await request.json()
        
        # Validar estructura
        if not self.validate_event(event):
            return {'error': 'Invalid event format'}, 400
        
        # Procesar evento
        event_type = event['event_type']
        handler = self.event_handlers.get(event_type)
        
        if handler:
            try:
                result = await handler(event['data'])
                return {'success': True, 'processed': event_type}, 200
            except Exception as e:
                logger.error(f"Error processing {event_type}: {e}")
                return {'error': 'Processing failed'}, 500
        else:
            return {'error': 'Unknown event type'}, 400
```

### Handlers de Eventos Específicos

```python
class EventHandlers:
    async def handle_inventory_update(self, data):
        """
        Actualizar información de inventario en Bird.com
        """
        affected_products = data['products']
        
        for product in affected_products:
            # Actualizar cache de Bird
            await self.update_product_cache(product['sku'], {
                'stock': product['new_stock'],
                'availability': product['availability']
            })
            
            # Notificar conversaciones activas
            active_conversations = await self.get_conversations_viewing_product(
                product['sku']
            )
            
            for conv_id in active_conversations:
                if product['new_stock'] == 0:
                    await self.send_notification(conv_id, {
                        'type': 'stock_alert',
                        'message': 'El producto que estás viendo se agotó 😔'
                    })
                elif product['new_stock'] < 5:
                    await self.send_notification(conv_id, {
                        'type': 'urgency',
                        'message': f'¡Quedan solo {product["new_stock"]} unidades! ⚡'
                    })
    
    async def handle_price_change(self, data):
        """
        Manejar cambios de precio
        """
        product = data['product']
        old_price = data['old_price']
        new_price = data['new_price']
        
        # Si el precio bajó, notificar a usuarios interesados
        if new_price < old_price:
            discount_percentage = ((old_price - new_price) / old_price) * 100
            
            # Buscar usuarios que vieron este producto
            interested_users = await self.get_users_who_viewed(product['sku'])
            
            for user in interested_users:
                await self.send_proactive_message(user['id'], {
                    'type': 'price_drop',
                    'product': product,
                    'message': f'¡El {product["name"]} que viste bajó {discount_percentage:.0f}%! 🎉',
                    'cta': 'Ver oferta'
                })
```

## 🔄 Event Processing Pipeline

### Pipeline de Procesamiento

```python
class EventProcessingPipeline:
    def __init__(self):
        self.stages = [
            self.validate_event,
            self.enrich_event,
            self.route_event,
            self.process_event,
            self.store_event,
            self.trigger_actions
        ]
    
    async def process(self, event):
        """Procesar evento a través del pipeline"""
        
        context = {
            'event': event,
            'metadata': {},
            'actions': []
        }
        
        for stage in self.stages:
            try:
                context = await stage(context)
                if context.get('stop_processing'):
                    break
            except Exception as e:
                logger.error(f"Error in stage {stage.__name__}: {e}")
                context['error'] = str(e)
                break
        
        return context
    
    async def enrich_event(self, context):
        """Enriquecer evento con información adicional"""
        
        event = context['event']
        
        # Agregar información del usuario
        if 'user_id' in event['data']:
            user_data = await self.get_user_data(event['data']['user_id'])
            context['metadata']['user'] = user_data
        
        # Agregar contexto temporal
        context['metadata']['time_context'] = {
            'is_business_hours': self.is_business_hours(),
            'day_of_week': datetime.now().strftime('%A'),
            'is_holiday': self.is_holiday()
        }
        
        return context
```

### Event Store

```python
class EventStore:
    """Almacenamiento y consulta de eventos"""
    
    def __init__(self):
        self.storage = DynamoDBEventStorage()
        self.index = ElasticsearchEventIndex()
    
    async def store_event(self, event):
        """Almacenar evento con indexación"""
        
        # Agregar metadata
        event['stored_at'] = datetime.now().isoformat()
        event['ttl'] = int(time.time()) + (90 * 24 * 3600)  # 90 días
        
        # Almacenar en DynamoDB
        await self.storage.put_event(event)
        
        # Indexar en Elasticsearch para búsqueda
        await self.index.index_event(event)
        
        # Publicar a stream de eventos
        await self.publish_to_stream(event)
    
    async def query_events(self, filters):
        """Consultar eventos históricos"""
        
        query = self.build_query(filters)
        results = await self.index.search(query)
        
        # Enriquecer con datos completos
        events = []
        for result in results:
            full_event = await self.storage.get_event(result['event_id'])
            events.append(full_event)
        
        return events
```

## 📊 Analytics de Eventos

### Agregación en Tiempo Real

```python
class EventAnalytics:
    def __init__(self):
        self.metrics_store = RedisTimeSeries()
        self.aggregations = {
            'conversation_metrics': self.aggregate_conversations,
            'ai_performance': self.aggregate_ai_performance,
            'business_metrics': self.aggregate_business_metrics
        }
    
    async def process_event_for_analytics(self, event):
        """Procesar evento para analytics en tiempo real"""
        
        # Métricas instantáneas
        await self.update_instant_metrics(event)
        
        # Agregaciones por ventana de tiempo
        for window in ['1m', '5m', '1h', '1d']:
            await self.update_windowed_metrics(event, window)
        
        # Alertas en tiempo real
        await self.check_alert_conditions(event)
    
    async def update_instant_metrics(self, event):
        """Actualizar métricas instantáneas"""
        
        if event['event_type'] == 'conversation.started':
            await self.metrics_store.increment('conversations.active')
            await self.metrics_store.increment('conversations.total')
        
        elif event['event_type'] == 'conversation.ended':
            await self.metrics_store.decrement('conversations.active')
            
            # Calcular métricas de la conversación
            duration = event['data']['duration']
            await self.metrics_store.add_sample('conversation.duration', duration)
            
            if event['data']['resolution']['outcome'] == 'purchase_completed':
                await self.metrics_store.increment('conversions.total')
```

### Dashboard de Eventos

```python
class EventDashboard:
    async def get_real_time_stats(self):
        """Obtener estadísticas en tiempo real"""
        
        return {
            'current_time': datetime.now().isoformat(),
            'active_conversations': await self.get_metric('conversations.active'),
            'events_per_minute': await self.get_rate('events.total', '1m'),
            'ai_response_time': {
                'p50': await self.get_percentile('ai.response_time', 50),
                'p95': await self.get_percentile('ai.response_time', 95),
                'p99': await self.get_percentile('ai.response_time', 99)
            },
            'top_events': await self.get_top_events('5m'),
            'error_rate': await self.get_error_rate('5m'),
            'conversion_funnel': await self.get_funnel_metrics()
        }
```

## 🔐 Seguridad de Webhooks

### Firma y Verificación

```python
import hmac
import hashlib

class WebhookSecurity:
    def sign_webhook(self, payload, secret):
        """Firmar webhook saliente"""
        
        # Crear firma HMAC-SHA256
        signature = hmac.new(
            secret.encode('utf-8'),
            payload.encode('utf-8'),
            hashlib.sha256
        ).hexdigest()
        
        # Agregar timestamp para prevenir replay attacks
        timestamp = str(int(time.time()))
        
        return {
            'X-Bird-Signature': signature,
            'X-Bird-Timestamp': timestamp,
            'X-Bird-Signature-Version': '1.0'
        }
    
    def verify_webhook(self, request, secret):
        """Verificar webhook entrante"""
        
        # Extraer headers
        signature = request.headers.get('X-Webhook-Signature')
        timestamp = request.headers.get('X-Webhook-Timestamp')
        
        if not signature or not timestamp:
            return False
        
        # Verificar timestamp (máximo 5 minutos de antigüedad)
        current_time = int(time.time())
        webhook_time = int(timestamp)
        
        if abs(current_time - webhook_time) > 300:
            return False
        
        # Verificar firma
        expected_signature = self.calculate_signature(
            request.body + timestamp,
            secret
        )
        
        return hmac.compare_digest(signature, expected_signature)
```

### Rate Limiting para Webhooks

```python
class WebhookRateLimiter:
    def __init__(self):
        self.limits = {
            'per_endpoint': 100,    # por minuto
            'per_source_ip': 50,    # por minuto
            'burst': 10             # ráfaga máxima
        }
    
    async def check_rate_limit(self, request):
        """Verificar límites de rate para webhooks"""
        
        endpoint = request.path
        source_ip = request.remote_addr
        
        # Verificar límite por endpoint
        endpoint_key = f"webhook_rate:{endpoint}"
        endpoint_count = await self.increment_counter(endpoint_key)
        
        if endpoint_count > self.limits['per_endpoint']:
            raise RateLimitExceeded('Endpoint rate limit exceeded')
        
        # Verificar límite por IP
        ip_key = f"webhook_rate:ip:{source_ip}"
        ip_count = await self.increment_counter(ip_key)
        
        if ip_count > self.limits['per_source_ip']:
            raise RateLimitExceeded('IP rate limit exceeded')
        
        return True
```

## 🔄 Retry Logic y Resiliencia

### Implementación de Retry

```python
from tenacity import (
    retry, 
    stop_after_attempt,
    wait_exponential,
    retry_if_exception_type
)

class WebhookDelivery:
    @retry(
        stop=stop_after_attempt(3),
        wait=wait_exponential(multiplier=1, min=4, max=60),
        retry=retry_if_exception_type((ConnectionError, TimeoutError))
    )
    async def deliver_webhook(self, url, payload, headers):
        """Entregar webhook con reintentos"""
        
        try:
            async with aiohttp.ClientSession() as session:
                async with session.post(
                    url,
                    json=payload,
                    headers=headers,
                    timeout=aiohttp.ClientTimeout(total=30)
                ) as response:
                    if response.status >= 500:
                        # Error del servidor, reintentar
                        raise ConnectionError(f"Server error: {response.status}")
                    
                    elif response.status >= 400:
                        # Error del cliente, no reintentar
                        logger.error(f"Client error: {response.status}")
                        return False
                    
                    return True
                    
        except asyncio.TimeoutError:
            logger.error(f"Webhook timeout for {url}")
            raise TimeoutError("Webhook delivery timeout")
```

### Dead Letter Queue

```python
class DeadLetterQueue:
    """Cola para webhooks fallidos"""
    
    def __init__(self):
        self.storage = S3DeadLetterStorage()
        self.max_retries = 5
    
    async def add_failed_webhook(self, webhook_data, error):
        """Agregar webhook fallido a DLQ"""
        
        dlq_entry = {
            'webhook': webhook_data,
            'error': str(error),
            'failed_at': datetime.now().isoformat(),
            'retry_count': webhook_data.get('retry_count', 0) + 1,
            'next_retry': self.calculate_next_retry(
                webhook_data.get('retry_count', 0)
            )
        }
        
        await self.storage.store(dlq_entry)
        
        # Notificar si es crítico
        if self.is_critical_failure(webhook_data):
            await self.notify_operations_team(dlq_entry)
    
    async def process_dlq(self):
        """Procesar webhooks en DLQ"""
        
        entries = await self.storage.get_due_entries()
        
        for entry in entries:
            if entry['retry_count'] < self.max_retries:
                # Reintentar
                await self.retry_webhook(entry)
            else:
                # Mover a archivo permanente
                await self.archive_failed_webhook(entry)
```

## 📊 Monitoreo de Webhooks

### Métricas Clave

```yaml
Webhook Metrics:
  Delivery:
    - Total webhooks sent
    - Successful deliveries
    - Failed deliveries
    - Retry attempts
    - Average delivery time
  
  Reception:
    - Total webhooks received
    - Valid vs invalid signatures
    - Processing time
    - Error rate
  
  Performance:
    - P50/P95/P99 latency
    - Throughput (webhooks/second)
    - Queue depth
    - DLQ size
```

### Alertas y Notificaciones

```python
class WebhookMonitoring:
    def __init__(self):
        self.alert_thresholds = {
            'delivery_failure_rate': 0.05,    # 5%
            'processing_time_p95': 1000,      # 1 segundo
            'dlq_size': 100,                  # webhooks
            'signature_failure_rate': 0.01    # 1%
        }
    
    async def check_alerts(self):
        """Verificar condiciones de alerta"""
        
        metrics = await self.get_current_metrics()
        alerts = []
        
        # Verificar tasa de fallo
        failure_rate = metrics['failed'] / metrics['total']
        if failure_rate > self.alert_thresholds['delivery_failure_rate']:
            alerts.append({
                'severity': 'high',
                'type': 'delivery_failure',
                'message': f'Webhook delivery failure rate: {failure_rate:.2%}'
            })
        
        # Verificar latencia
        if metrics['p95_latency'] > self.alert_thresholds['processing_time_p95']:
            alerts.append({
                'severity': 'medium',
                'type': 'high_latency',
                'message': f'Webhook processing P95: {metrics["p95_latency"]}ms'
            })
        
        return alerts
```

## 🎯 Próximos Pasos

Con webhooks y eventos configurados:

1. **[11-TESTING-Y-VALIDACION.md](11-TESTING-Y-VALIDACION.md)** - Probar flujos de eventos
2. **[12-MONITOREO-Y-ANALYTICS.md](12-MONITOREO-Y-ANALYTICS.md)** - Analizar métricas de eventos
3. **[14-TROUBLESHOOTING.md](14-TROUBLESHOOTING.md)** - Resolver problemas de webhooks

---

**Recuerda**: Los webhooks son el sistema nervioso de tu integración. Diseña para fallos, monitorea constantemente y siempre ten un plan B (Dead Letter Queue) para eventos críticos.