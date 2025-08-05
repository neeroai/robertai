# 09 - Integraciones API

## 🔌 Arquitectura de Integración

### Visión General

```
┌─────────────────────────────────────────────────────────────┐
│                     Bird.com Platform                         │
│  ┌─────────────────────────────────────────────────────┐   │
│  │              AI Agent (Jako)                          │   │
│  │  • NLP Processing  • Context Management              │   │
│  │  • Action Execution • Response Generation            │   │
│  └──────────────────┬──────────────────────────────────┘   │
│                     │                                        │
│  ┌──────────────────▼──────────────────────────────────┐   │
│  │            Integration Layer                         │   │
│  │  • Authentication  • Rate Limiting                   │   │
│  │  • Request Routing • Response Transformation        │   │
│  └──────────────────┬──────────────────────────────────┘   │
└─────────────────────┼────────────────────────────────────┘
                      │
                      │ HTTPS/REST
                      │
┌─────────────────────▼────────────────────────────────────┐
│                 KOAJ Catalog API                          │
│           https://api.neero.link/v1                       │
│                                                          │
│  ┌────────────┐  ┌────────────┐  ┌─────────────┐      │
│  │  Products  │  │ Inventory  │  │ Bird Endpoints│      │
│  │  /products │  │ /inventory │  │ /bird/*      │      │
│  └────────────┘  └────────────┘  └─────────────┘      │
└──────────────────────────────────────────────────────────┘
```

## 🔐 Autenticación y Seguridad

### Configuración de API Keys

```python
# Configuración segura de credenciales
class APIConfiguration:
    def __init__(self):
        self.config = {
            'koaj_api': {
                'base_url': 'https://api.neero.link/v1',
                'api_key': os.environ.get('KOAJ_API_KEY'),
                'headers': {
                    'X-API-Key': os.environ.get('KOAJ_API_KEY'),
                    'Content-Type': 'application/json',
                    'Accept': 'application/json',
                    'User-Agent': 'Bird.com-AI-Agent/1.0'
                }
            },
            'bird_webhook': {
                'signing_secret': os.environ.get('BIRD_WEBHOOK_SECRET'),
                'verify_signature': True
            }
        }
    
    def get_headers(self, api_name='koaj_api'):
        headers = self.config[api_name]['headers'].copy()
        headers['X-Request-ID'] = self.generate_request_id()
        headers['X-Timestamp'] = str(int(time.time()))
        return headers
```

### Verificación de Firmas

```python
import hmac
import hashlib

def verify_bird_signature(request_body, signature, secret):
    """Verificar que el request viene de Bird.com"""
    
    # Calcular firma esperada
    expected_signature = hmac.new(
        secret.encode('utf-8'),
        request_body.encode('utf-8'),
        hashlib.sha256
    ).hexdigest()
    
    # Comparación segura
    return hmac.compare_digest(signature, expected_signature)

# Middleware para verificación
def signature_verification_middleware(request):
    signature = request.headers.get('X-Bird-Signature')
    
    if not signature:
        raise SecurityError('Missing signature')
    
    if not verify_bird_signature(
        request.body,
        signature,
        BIRD_WEBHOOK_SECRET
    ):
        raise SecurityError('Invalid signature')
    
    return True
```

## 📡 Endpoints Especializados KOAJ

### 1. Búsqueda Inteligente con AI

```python
class KOAJSearchEndpoint:
    """
    POST /bird/ai-search
    Búsqueda optimizada para AI con contexto conversacional
    """
    
    def __init__(self):
        self.endpoint = '/bird/ai-search'
        self.method = 'POST'
    
    def build_request(self, query, context):
        return {
            'url': f"{BASE_URL}{self.endpoint}",
            'method': self.method,
            'headers': self.get_auth_headers(),
            'json': {
                'query': query,
                'context': {
                    'user_id': context.get('user_id'),
                    'conversation_id': context.get('conversation_id'),
                    'preferences': self.extract_preferences(context),
                    'conversation_history': self.get_recent_messages(context)
                },
                'filters': self.build_smart_filters(query, context),
                'options': {
                    'limit': 5,
                    'include_images': True,
                    'include_inventory': True,
                    'language': context.get('language', 'es')
                }
            }
        }
    
    def build_smart_filters(self, query, context):
        filters = {
            'brand': 'KOAJ',
            'availability': 'in_stock'
        }
        
        # Extraer filtros del query
        price_range = self.extract_price_range(query)
        if price_range:
            filters['price_range'] = price_range
        
        # Aplicar preferencias del usuario
        if context.get('preferred_categories'):
            filters['categories'] = context['preferred_categories']
        
        return filters
```

### 2. Gestión de Inventario

```python
class InventoryEndpoint:
    """
    GET /inventory/{sku}
    POST /inventory/bulk-check
    """
    
    async def check_single_item(self, sku, store_id=None):
        endpoint = f"/inventory/{sku}"
        params = {}
        
        if store_id:
            params['store_id'] = store_id
        
        response = await self.make_request('GET', endpoint, params=params)
        
        return {
            'sku': sku,
            'available': response['available'],
            'quantity': response['quantity'],
            'stores': response.get('store_availability', []),
            'online_stock': response.get('online_stock', 0)
        }
    
    async def check_multiple_items(self, sku_list, store_id=None):
        endpoint = "/inventory/bulk-check"
        
        payload = {
            'skus': sku_list,
            'include_stores': True,
            'store_id': store_id
        }
        
        response = await self.make_request('POST', endpoint, json=payload)
        
        return self.format_inventory_response(response)
```

### 3. Recomendaciones Personalizadas

```python
class RecommendationEndpoint:
    """
    POST /bird/recommendations/smart
    """
    
    def get_recommendations(self, user_context, product_context=None):
        endpoint = "/bird/recommendations/smart"
        
        payload = {
            'user_context': {
                'user_id': user_context.get('user_id'),
                'preferences': user_context.get('preferences', {}),
                'purchase_history': self.get_purchase_summary(user_context),
                'browsing_behavior': user_context.get('browsing_behavior', {})
            },
            'recommendation_type': self.determine_recommendation_type(user_context),
            'options': {
                'limit': 4,
                'diversity_factor': 0.7,
                'include_trending': True,
                'personalization_weight': 0.8
            }
        }
        
        if product_context:
            payload['seed_products'] = product_context['viewed_products']
            payload['context_type'] = 'complementary'
        
        return self.make_request('POST', endpoint, json=payload)
    
    def determine_recommendation_type(self, context):
        if context.get('looking_for_similar'):
            return 'similar'
        elif context.get('in_cart'):
            return 'complementary'
        elif context.get('browsing_category'):
            return 'category_based'
        else:
            return 'personalized'
```

### 4. Knowledge Base Access

```python
class KnowledgeBaseEndpoint:
    """
    GET /bird/knowledge-base/{category}
    POST /bird/knowledge-base/search
    """
    
    def get_category_content(self, category):
        valid_categories = ['faq', 'policies', 'sizing', 'brand', 'care']
        
        if category not in valid_categories:
            raise ValueError(f"Invalid category. Must be one of: {valid_categories}")
        
        endpoint = f"/bird/knowledge-base/{category}"
        
        response = self.make_request('GET', endpoint)
        
        return {
            'category': category,
            'content': response['content'],
            'last_updated': response['last_updated'],
            'format': response.get('format', 'markdown')
        }
    
    def search_knowledge(self, query, categories=None):
        endpoint = "/bird/knowledge-base/search"
        
        payload = {
            'query': query,
            'categories': categories or ['all'],
            'limit': 5,
            'include_relevance_score': True
        }
        
        results = self.make_request('POST', endpoint, json=payload)
        
        return self.format_search_results(results)
```

## 🔄 Manejo de Requests y Responses

### Request Manager Robusto

```python
import asyncio
import aiohttp
from tenacity import retry, stop_after_attempt, wait_exponential

class APIRequestManager:
    def __init__(self):
        self.session = None
        self.timeout = aiohttp.ClientTimeout(total=30)
        self.max_retries = 3
        
    async def __aenter__(self):
        self.session = aiohttp.ClientSession(timeout=self.timeout)
        return self
    
    async def __aexit__(self, exc_type, exc_val, exc_tb):
        await self.session.close()
    
    @retry(
        stop=stop_after_attempt(3),
        wait=wait_exponential(multiplier=1, min=4, max=10)
    )
    async def make_request(self, method, url, **kwargs):
        """Hacer request con retry automático"""
        
        # Agregar tracking headers
        if 'headers' not in kwargs:
            kwargs['headers'] = {}
        
        kwargs['headers'].update({
            'X-Request-ID': self.generate_request_id(),
            'X-Timestamp': str(int(time.time()))
        })
        
        try:
            async with self.session.request(method, url, **kwargs) as response:
                # Log request
                self.log_request(method, url, kwargs)
                
                # Verificar status
                response.raise_for_status()
                
                # Parse response
                data = await response.json()
                
                # Log response
                self.log_response(response.status, data)
                
                return data
                
        except aiohttp.ClientError as e:
            self.handle_client_error(e)
            raise
        except Exception as e:
            self.handle_unexpected_error(e)
            raise
```

### Response Transformation

```python
class ResponseTransformer:
    """Transforma respuestas de API al formato esperado por Bird.com"""
    
    def transform_product_search(self, api_response):
        """Transforma respuesta de búsqueda de productos"""
        
        if not api_response.get('products'):
            return {
                'found': False,
                'message': 'No se encontraron productos',
                'suggestions': self.get_search_suggestions()
            }
        
        products = []
        for item in api_response['products'][:5]:  # Máximo 5 productos
            products.append({
                'id': item['externalProductId'],
                'title': self.format_title(item['title']),
                'description': self.truncate_description(item['description']),
                'price': self.format_price_for_display(item['price']),
                'image': self.ensure_image_url(item.get('imageUrl')),
                'availability': self.format_availability(item.get('inventory')),
                'badges': self.generate_badges(item),
                'score': item.get('relevance_score', 0)
            })
        
        return {
            'found': True,
            'count': len(products),
            'products': products,
            'filters_applied': api_response.get('filters_applied', {}),
            'total_available': api_response.get('total_count', len(products))
        }
    
    def format_price_for_display(self, price_obj):
        """Formatea precio para mostrar en chat"""
        
        if isinstance(price_obj, dict):
            amount = price_obj.get('amount', 0)
            currency = price_obj.get('currencyCode', 'COP')
            
            # Formatear según moneda
            if currency == 'COP':
                return f"${amount:,.0f}"
            else:
                return f"{currency} {amount:,.2f}"
        
        return str(price_obj)
```

## 🚦 Rate Limiting y Throttling

### Implementación de Rate Limiter

```python
from collections import defaultdict
import time

class RateLimiter:
    def __init__(self):
        self.limits = {
            'koaj_api': {
                'requests_per_second': 10,
                'requests_per_minute': 100,
                'requests_per_hour': 1000
            },
            'per_user': {
                'requests_per_minute': 20,
                'requests_per_hour': 200
            }
        }
        
        self.request_history = defaultdict(list)
    
    async def check_rate_limit(self, api_name, user_id=None):
        """Verificar si se puede hacer el request"""
        
        current_time = time.time()
        
        # Limpiar historial antiguo
        self.clean_old_requests(current_time)
        
        # Verificar límite de API
        api_key = f"api_{api_name}"
        if not self.is_within_limit(api_key, self.limits[api_name]):
            raise RateLimitError(f"Rate limit exceeded for {api_name}")
        
        # Verificar límite por usuario
        if user_id:
            user_key = f"user_{user_id}"
            if not self.is_within_limit(user_key, self.limits['per_user']):
                raise RateLimitError(f"Rate limit exceeded for user {user_id}")
        
        # Registrar request
        self.request_history[api_key].append(current_time)
        if user_id:
            self.request_history[user_key].append(current_time)
        
        return True
    
    def is_within_limit(self, key, limits):
        current_time = time.time()
        history = self.request_history[key]
        
        # Verificar cada límite
        for period, limit in limits.items():
            if 'second' in period:
                window = 1
            elif 'minute' in period:
                window = 60
            elif 'hour' in period:
                window = 3600
            
            recent_requests = [
                t for t in history 
                if current_time - t < window
            ]
            
            if len(recent_requests) >= limit:
                return False
        
        return True
```

### Circuit Breaker Pattern

```python
class CircuitBreaker:
    """Previene cascada de fallos en APIs"""
    
    def __init__(self, failure_threshold=5, recovery_timeout=60):
        self.failure_threshold = failure_threshold
        self.recovery_timeout = recovery_timeout
        self.failure_count = 0
        self.last_failure_time = None
        self.state = 'closed'  # closed, open, half-open
    
    def call(self, func, *args, **kwargs):
        if self.state == 'open':
            if self._should_attempt_reset():
                self.state = 'half-open'
            else:
                raise CircuitOpenError('Circuit breaker is open')
        
        try:
            result = func(*args, **kwargs)
            self._on_success()
            return result
        except Exception as e:
            self._on_failure()
            raise
    
    def _on_success(self):
        self.failure_count = 0
        self.state = 'closed'
    
    def _on_failure(self):
        self.failure_count += 1
        self.last_failure_time = time.time()
        
        if self.failure_count >= self.failure_threshold:
            self.state = 'open'
    
    def _should_attempt_reset(self):
        return (
            self.last_failure_time and 
            time.time() - self.last_failure_time >= self.recovery_timeout
        )
```

## 📊 Monitoreo de Integraciones

### Métricas de API

```python
class APIMetricsCollector:
    def __init__(self):
        self.metrics = {
            'request_count': 0,
            'success_count': 0,
            'error_count': 0,
            'response_times': [],
            'error_types': defaultdict(int)
        }
    
    def record_request(self, endpoint, method, response_time, status, error=None):
        self.metrics['request_count'] += 1
        self.metrics['response_times'].append(response_time)
        
        if 200 <= status < 300:
            self.metrics['success_count'] += 1
        else:
            self.metrics['error_count'] += 1
            if error:
                self.metrics['error_types'][type(error).__name__] += 1
        
        # Calcular percentiles
        if len(self.metrics['response_times']) > 100:
            self.calculate_percentiles()
    
    def get_summary(self):
        total = self.metrics['request_count']
        if total == 0:
            return {'status': 'no_data'}
        
        return {
            'total_requests': total,
            'success_rate': self.metrics['success_count'] / total,
            'error_rate': self.metrics['error_count'] / total,
            'avg_response_time': sum(self.metrics['response_times']) / len(self.metrics['response_times']),
            'p95_response_time': self.calculate_percentile(95),
            'p99_response_time': self.calculate_percentile(99),
            'top_errors': dict(self.metrics['error_types'].most_common(5))
        }
```

### Health Check Endpoints

```python
class IntegrationHealthCheck:
    async def check_all_integrations(self):
        """Verificar salud de todas las integraciones"""
        
        health_status = {
            'timestamp': datetime.now().isoformat(),
            'overall_status': 'healthy',
            'integrations': {}
        }
        
        # Check KOAJ API
        koaj_health = await self.check_koaj_api()
        health_status['integrations']['koaj_api'] = koaj_health
        
        # Check Database connections
        db_health = await self.check_database()
        health_status['integrations']['database'] = db_health
        
        # Check Cache
        cache_health = await self.check_cache()
        health_status['integrations']['cache'] = cache_health
        
        # Determinar estado general
        if any(
            integration['status'] == 'unhealthy' 
            for integration in health_status['integrations'].values()
        ):
            health_status['overall_status'] = 'degraded'
        
        return health_status
    
    async def check_koaj_api(self):
        try:
            start_time = time.time()
            response = await self.make_request('GET', '/health')
            response_time = (time.time() - start_time) * 1000
            
            return {
                'status': 'healthy' if response.status == 200 else 'unhealthy',
                'response_time_ms': response_time,
                'last_check': datetime.now().isoformat()
            }
        except Exception as e:
            return {
                'status': 'unhealthy',
                'error': str(e),
                'last_check': datetime.now().isoformat()
            }
```

## 🔄 Sincronización de Datos

### Sync Manager

```python
class DataSyncManager:
    def __init__(self):
        self.sync_intervals = {
            'products': 3600,      # 1 hora
            'inventory': 300,      # 5 minutos
            'prices': 1800,        # 30 minutos
            'knowledge_base': 86400 # 24 horas
        }
        
        self.last_sync = {}
    
    async def sync_if_needed(self, data_type):
        """Sincronizar si ha pasado el intervalo"""
        
        current_time = time.time()
        last_sync_time = self.last_sync.get(data_type, 0)
        interval = self.sync_intervals.get(data_type, 3600)
        
        if current_time - last_sync_time > interval:
            await self.sync_data(data_type)
            self.last_sync[data_type] = current_time
    
    async def sync_data(self, data_type):
        """Ejecutar sincronización específica"""
        
        sync_methods = {
            'products': self.sync_products,
            'inventory': self.sync_inventory,
            'prices': self.sync_prices,
            'knowledge_base': self.sync_knowledge_base
        }
        
        method = sync_methods.get(data_type)
        if method:
            await method()
```

## 🔧 SDK de Integración

### Cliente Python para KOAJ API

```python
class KOAJClient:
    """SDK oficial para integración con KOAJ API"""
    
    def __init__(self, api_key, base_url='https://api.neero.link/v1'):
        self.api_key = api_key
        self.base_url = base_url
        self.session = None
    
    async def __aenter__(self):
        self.session = aiohttp.ClientSession()
        return self
    
    async def __aexit__(self, exc_type, exc_val, exc_tb):
        await self.session.close()
    
    # Productos
    async def search_products(self, query, **filters):
        """Buscar productos con filtros"""
        return await self._make_request(
            'POST',
            '/bird/ai-search',
            json={'query': query, 'filters': filters}
        )
    
    async def get_product(self, product_id):
        """Obtener detalles de un producto"""
        return await self._make_request(
            'GET',
            f'/products/{product_id}'
        )
    
    # Inventario
    async def check_inventory(self, sku, store_id=None):
        """Verificar inventario de un SKU"""
        params = {'store_id': store_id} if store_id else {}
        return await self._make_request(
            'GET',
            f'/inventory/{sku}',
            params=params
        )
    
    # Recomendaciones
    async def get_recommendations(self, user_context, **options):
        """Obtener recomendaciones personalizadas"""
        return await self._make_request(
            'POST',
            '/bird/recommendations/smart',
            json={'user_context': user_context, 'options': options}
        )
    
    # Knowledge Base
    async def get_knowledge(self, category):
        """Obtener contenido del knowledge base"""
        return await self._make_request(
            'GET',
            f'/bird/knowledge-base/{category}'
        )
    
    # Método interno para requests
    async def _make_request(self, method, endpoint, **kwargs):
        url = f"{self.base_url}{endpoint}"
        
        headers = kwargs.get('headers', {})
        headers.update({
            'X-API-Key': self.api_key,
            'Content-Type': 'application/json'
        })
        kwargs['headers'] = headers
        
        async with self.session.request(method, url, **kwargs) as response:
            response.raise_for_status()
            return await response.json()
```

### Ejemplos de Uso

```python
# Ejemplo de uso del SDK
async def example_integration():
    async with KOAJClient(api_key='your-api-key') as client:
        # Buscar productos
        results = await client.search_products(
            'vestido negro',
            price_range={'min': 100000, 'max': 300000},
            size='M'
        )
        
        # Verificar inventario
        for product in results['products']:
            inventory = await client.check_inventory(product['sku'])
            print(f"{product['title']}: {inventory['quantity']} disponibles")
        
        # Obtener recomendaciones
        recommendations = await client.get_recommendations(
            user_context={'user_id': '12345', 'preferences': {'style': 'elegant'}},
            limit=3
        )
```

## 🎯 Próximos Pasos

Con las integraciones configuradas:

1. **[Webhooks y Eventos](webhooks.md)** - Configurar eventos bidireccionales
2. **[Testing y Validación](../operations/testing.md)** - Probar integraciones
3. **[Monitoreo y Analytics](../operations/monitoring.md)** - Monitorear performance

---

**Tip Pro**: Las integraciones son el sistema nervioso de tu AI Employee. Una integración bien hecha es invisible pero poderosa. Invierte tiempo en hacerlas robustas, rápidas y confiables.