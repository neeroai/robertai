# 07 - AI Actions y API Integration

## 🎯 ¿Qué son las AI Actions?

Las AI Actions son capacidades ejecutables que permiten al AI Employee realizar tareas específicas más allá de responder preguntas. Conectan al agente con sistemas externos para ejecutar operaciones como búsquedas, consultas, actualizaciones y más.

### Tipos de Actions

```yaml
Action Categories:
  Query Actions:
    - Búsqueda de productos
    - Consulta de inventario
    - Verificación de precios
    - Estado de pedidos
  
  Compute Actions:
    - Cálculo de descuentos
    - Recomendaciones personalizadas
    - Estimación de envío
    - Conversión de unidades
  
  Integration Actions:
    - Consulta a CRM
    - Verificación en base de datos
    - Llamadas a APIs externas
    - Webhook triggers
  
  Transaction Actions:
    - Creación de leads
    - Registro de interacciones
    - Actualización de preferencias
    - Programación de seguimientos
```

## 🔧 Configuración de Actions en Bird.com

### Crear una Nueva Action

1. **Navegación**
   ```
   Settings > AI > Actions > Create New Action
   ```

2. **Configuración Básica**
   ```yaml
   Name: search_products
   Display Name: "Buscar Productos"
   Description: "Busca productos en el catálogo con filtros inteligentes"
   Type: REST_API
   Method: POST
   ```

### Anatomía de una Action

```json
{
  "action_config": {
    "name": "search_products",
    "description": "Búsqueda inteligente de productos",
    "triggers": {
      "keywords": ["busco", "quiero", "necesito", "muéstrame"],
      "intents": ["product_search", "browse_catalog"],
      "confidence_threshold": 0.7
    },
    "parameters": {
      "required": ["query"],
      "optional": ["category", "price_range", "specifications"],
      "extraction_rules": {
        "query": {
          "type": "string",
          "source": "user_message",
          "processing": "natural_language"
        },
        "price_range": {
          "type": "object",
          "pattern": "menos de (\\d+)|entre (\\d+) y (\\d+)",
          "default": {"min": 10000, "max": 1000000}
        }
      }
    },
    "execution": {
      "endpoint": "https://api.empresa.com/v1/search",
      "method": "POST",
      "headers": {
        "Content-Type": "application/json",
        "X-API-Key": "${API_KEY}"
      },
      "timeout": 5000,
      "retry": {
        "attempts": 3,
        "backoff": "exponential"
      }
    },
    "response_handling": {
      "success_path": "$.products",
      "error_path": "$.error",
      "transformation": "format_product_cards"
    }
  }
}
```

## 📡 Webhook Configuration

### Webhook URL Setup

```yaml
Webhook Configuration:
  URL: https://api.empresa.com/v1/search
  
  Authentication:
    Type: API_KEY
    Header: X-API-Key
    Value: ${API_KEY}
  
  Additional Headers:
    Content-Type: application/json
    X-Bird-Signature: ${REQUEST_SIGNATURE}
    X-Timestamp: ${TIMESTAMP}
```

### Request Body Template

```json
{
  "query": "{{user_input}}",
  "context": {
    "user_id": "{{contact.id}}",
    "conversation_id": "{{conversation.id}}",
    "channel": "{{channel.type}}",
    "timestamp": "{{timestamp}}",
    "preferences": {
      "language": "{{contact.language | default: 'es'}}",
      "currency": "{{contact.currency | default: 'COP'}}",
      "location": "{{contact.location | default: 'Colombia'}}"
    },
    "conversation_history": [
      {% for message in conversation.recent_messages limit:5 %}
      {
        "role": "{{message.role}}",
        "content": "{{message.content}}",
        "timestamp": "{{message.timestamp}}"
      }{% unless forloop.last %},{% endunless %}
      {% endfor %}
    ]
  },
  "filters": {
    "category": "{{extracted.category | default: ''}}",
    "price_range": {
      "min": {{extracted.price_min | default: 10000}},
      "max": {{extracted.price_max | default: 1000000}}
    },
    "specifications": "{{extracted.specifications | default: ''}}",
    "brand": "{{brand_name}}"
  },
  "options": {
    "limit": {{limit | default: 5}},
    "sort": "{{sort | default: 'relevance'}}",
    "include_images": true,
    "include_inventory": true
  }
}
```

## 🧠 Parameter Extraction

### Extracción Inteligente de Parámetros

```python
class ParameterExtractor:
    def __init__(self):
        self.extractors = {
            'price': self.extract_price,
            'specifications': self.extract_specifications,
            'category': self.extract_category,
            'intent': self.extract_intent
        }
    
    def extract_price(self, text):
        patterns = {
            'max_price': [
                r'menos de (\d+)',
                r'máximo (\d+)',
                r'hasta (\d+)',
                r'no más de (\d+)'
            ],
            'range': [
                r'entre (\d+) y (\d+)',
                r'de (\d+) a (\d+)',
                r'desde (\d+) hasta (\d+)'
            ],
            'budget_hints': {
                'económico': {'min': 10000, 'max': 50000},
                'barato': {'min': 10000, 'max': 30000},
                'premium': {'min': 200000, 'max': 1000000},
                'exclusivo': {'min': 500000, 'max': 1000000}
            }
        }
        
        # Buscar patrones numéricos
        for pattern_list in patterns['max_price']:
            match = re.search(pattern_list, text, re.IGNORECASE)
            if match:
                return {'min': 10000, 'max': int(match.group(1)) * 1000}
        
        # Buscar rangos
        for pattern in patterns['range']:
            match = re.search(pattern, text, re.IGNORECASE)
            if match:
                return {
                    'min': int(match.group(1)) * 1000,
                    'max': int(match.group(2)) * 1000
                }
        
        # Buscar hints de presupuesto
        for hint, range_val in patterns['budget_hints'].items():
            if hint in text.lower():
                return range_val
        
        # Default
        return {'min': 10000, 'max': 1000000}
```

### Mapeo de Intenciones

```yaml
Intent Mapping:
  user_says: "Busco un producto específico para una necesidad"
  
  extracted:
    intent: "product_search"
    category: "categoria_principal"
    specifications: "especificaciones"
    context: "necesidad"
    formality: "especifico"
  
  action_parameters:
    query: "producto específico para necesidad"
    filters:
      category: "CATEGORIA/SUBCATEGORIA"
      specifications: "especificaciones"
      tags: ["especifico", "necesidad", "contexto"]
```

## 🔄 Response Handling

### Procesamiento de Respuestas

```python
class ResponseProcessor:
    def process_action_response(self, action_name, response):
        processors = {
            'search_products': self.process_search_results,
            'check_inventory': self.process_inventory,
            'get_recommendations': self.process_recommendations
        }
        
        processor = processors.get(action_name)
        if processor:
            return processor(response)
        
        return self.default_processor(response)
    
    def process_search_results(self, response):
        if not response.get('products'):
            return {
                'type': 'text',
                'content': 'No encontré productos con esos criterios. ¿Probamos con otros filtros?'
            }
        
        products = response['products'][:5]  # Max 5 productos
        
        return {
            'type': 'product_carousel',
            'content': {
                'intro': f"¡Encontré {len(products)} opciones perfectas para ti! 🛍️",
                'products': [
                    self.format_product_card(product) 
                    for product in products
                ],
                'actions': [
                    {'type': 'button', 'text': 'Ver más', 'action': 'show_more'},
                    {'type': 'button', 'text': 'Filtrar', 'action': 'refine_search'}
                ]
            }
        }
    
    def format_product_card(self, product):
        return {
            'id': product['externalProductId'],
            'title': product['title'],
            'description': self.truncate(product['description'], 100),
            'price': self.format_price(product['price']),
            'image': product['imageUrl'],
            'actions': [
                {'text': 'Ver detalles', 'action': f'view_product_{product["id"]}'},
                {'text': 'Agregar a favoritos', 'action': f'favorite_{product["id"]}'}
            ],
            'badges': self.get_product_badges(product)
        }
```

### Formateo de Respuestas para WhatsApp

```python
def format_for_whatsapp(response):
    if response['type'] == 'product_carousel':
        # WhatsApp no soporta carousels nativos
        # Convertir a lista con imágenes
        
        message = response['content']['intro'] + '\n\n'
        
        for idx, product in enumerate(response['content']['products'], 1):
            message += f"*{idx}. {product['title']}*\n"
            message += f"💰 {product['price']}\n"
            message += f"📝 {product['description']}\n"
            message += f"🔗 Ver más: {product['link']}\n\n"
        
        # Agregar opciones interactivas
        message += "¿Cuál te interesa? Responde con el número."
        
        return {
            'text': message,
            'quick_replies': [
                f"Opción {i}" for i in range(1, len(products) + 1)
            ]
        }
```

## 🎨 Actions Complejas

### Orquestación de Múltiples APIs

```python
class ComplexActionOrchestrator:
    async def execute_complex_search(self, query, user_context):
        # Paso 1: Búsqueda de productos
        search_task = self.search_products(query)
        
        # Paso 2: Obtener recomendaciones basadas en historial
        recommendations_task = self.get_user_recommendations(
            user_context['user_id']
        )
        
        # Paso 3: Verificar inventario en paralelo
        search_results = await search_task
        inventory_tasks = [
            self.check_inventory(product['sku'])
            for product in search_results['products'][:10]
        ]
        
        # Esperar todos los resultados
        recommendations = await recommendations_task
        inventory_results = await asyncio.gather(*inventory_tasks)
        
        # Combinar y rankear resultados
        final_results = self.merge_and_rank(
            search_results,
            recommendations,
            inventory_results
        )
        
        return final_results
```

### Actions con Estado

```python
class StatefulAction:
    def __init__(self):
        self.conversation_state = {}
    
    def multi_step_action(self, step, params, conversation_id):
        state = self.conversation_state.get(conversation_id, {})
        
        if step == 'init':
            state['filters'] = {}
            state['step'] = 'category_selection'
            return {
                'message': '¿Qué tipo de producto buscas?',
                'options': ['Categoría 1', 'Categoría 2', 'Categoría 3', 'Ofertas']
            }
        
        elif step == 'category_selected':
            state['filters']['category'] = params['selection']
            state['step'] = 'specification_selection'
            return {
                'message': '¿Qué especificaciones necesitas?',
                'options': ['Especificación A', 'Especificación B', 'Especificación C']
            }
        
        elif step == 'specification_selected':
            state['filters']['specifications'] = params['selection']
            state['step'] = 'search'
            
            # Ejecutar búsqueda con todos los filtros
            results = self.search_with_filters(state['filters'])
            
            # Limpiar estado
            del self.conversation_state[conversation_id]
            
            return results
```

## 📊 Error Handling

### Manejo Robusto de Errores

```python
class ActionErrorHandler:
    def handle_action_error(self, error, action_name, params):
        error_responses = {
            'timeout': {
                'message': 'La búsqueda está tardando más de lo normal. ¿Intentamos de nuevo?',
                'retry': True,
                'fallback': 'show_categories'
            },
            'api_error': {
                'message': 'Hay un problema temporal con el sistema. Mientras tanto, puedo mostrarte nuestras categorías principales.',
                'retry': False,
                'fallback': 'show_static_content'
            },
            'invalid_parameters': {
                'message': 'No entendí bien tu búsqueda. ¿Podrías ser más específico?',
                'retry': False,
                'fallback': 'clarify_search'
            },
            'no_results': {
                'message': 'No encontré exactamente lo que buscas, pero tengo estas alternativas:',
                'retry': False,
                'fallback': 'show_alternatives'
            }
        }
        
        error_type = self.classify_error(error)
        response = error_responses.get(error_type, {
            'message': 'Ocurrió un error inesperado. ¿Puedo ayudarte de otra forma?',
            'retry': False,
            'fallback': 'escalate_to_human'
        })
        
        # Log para análisis
        self.log_error(action_name, error, params)
        
        return response
```

### Fallback Strategies

```yaml
Fallback Hierarchy:
  Level 1 - Retry:
    - Retry with relaxed parameters
    - Remove optional filters
    - Broaden search terms
  
  Level 2 - Alternative:
    - Show popular products
    - Suggest categories
    - Offer guided search
  
  Level 3 - Static:
    - Display FAQ
    - Show contact options
    - Present store locations
  
  Level 4 - Escalate:
    - Transfer to human agent
    - Create support ticket
    - Schedule callback
```

## 🚀 Optimización de Performance

### Caching de Actions

```python
class ActionCache:
    def __init__(self):
        self.cache = {}
        self.ttl = {
            'search_products': 300,      # 5 minutos
            'check_inventory': 60,       # 1 minuto
            'get_recommendations': 3600  # 1 hora
        }
    
    def get_cached_result(self, action_name, params):
        cache_key = self.generate_cache_key(action_name, params)
        cached = self.cache.get(cache_key)
        
        if cached and not self.is_expired(cached):
            return cached['result']
        
        return None
    
    def cache_result(self, action_name, params, result):
        cache_key = self.generate_cache_key(action_name, params)
        self.cache[cache_key] = {
            'result': result,
            'timestamp': time.time(),
            'ttl': self.ttl.get(action_name, 300)
        }
```

### Paralelización de Actions

```python
async def execute_parallel_actions(actions):
    """Ejecutar múltiples actions en paralelo"""
    
    tasks = []
    for action in actions:
        task = asyncio.create_task(
            execute_action(
                action['name'],
                action['params']
            )
        )
        tasks.append(task)
    
    # Esperar todas las respuestas
    results = await asyncio.gather(*tasks, return_exceptions=True)
    
    # Procesar resultados
    processed_results = []
    for idx, result in enumerate(results):
        if isinstance(result, Exception):
            # Manejar error
            processed_results.append(
                handle_action_error(result, actions[idx])
            )
        else:
            processed_results.append(result)
    
    return processed_results
```

## 📈 Métricas y Monitoreo

### KPIs de Actions

```yaml
Action Metrics:
  Success Rate:
    formula: successful_executions / total_executions
    target: > 95%
    alert: < 90%
  
  Response Time:
    p50: < 200ms
    p95: < 500ms
    p99: < 1000ms
  
  Error Rate:
    formula: errors / total_executions
    target: < 2%
    alert: > 5%
  
  Cache Hit Rate:
    formula: cache_hits / (cache_hits + cache_misses)
    target: > 60%
  
  Usage Distribution:
    track: executions per action type
    insight: identify most/least used actions
```

### Logging y Debugging

```python
class ActionLogger:
    def log_action_execution(self, action_name, params, result, duration):
        log_entry = {
            'timestamp': datetime.now().isoformat(),
            'action': action_name,
            'parameters': self.sanitize_params(params),
            'success': result.get('success', False),
            'duration_ms': duration,
            'error': result.get('error'),
            'conversation_id': params.get('conversation_id'),
            'user_id': self.hash_user_id(params.get('user_id'))
        }
        
        # Enviar a sistema de logging
        self.send_to_logging_system(log_entry)
        
        # Análisis en tiempo real
        if duration > 1000:  # Más de 1 segundo
            self.alert_slow_action(action_name, duration)
        
        if not result.get('success'):
            self.analyze_failure_pattern(action_name, result.get('error'))
```

## 🛡️ Seguridad en Actions

### Validación de Parámetros

```python
class ActionSecurityValidator:
    def validate_parameters(self, action_name, params):
        # Validación de tipos
        schema = self.get_action_schema(action_name)
        self.validate_against_schema(params, schema)
        
        # Sanitización de inputs
        sanitized_params = {}
        for key, value in params.items():
            sanitized_params[key] = self.sanitize_input(value)
        
        # Validación de permisos
        if not self.check_permissions(action_name, params.get('user_id')):
            raise PermissionError(f"Usuario no autorizado para {action_name}")
        
        # Rate limiting
        if not self.check_rate_limit(action_name, params.get('user_id')):
            raise RateLimitError(f"Rate limit excedido para {action_name}")
        
        return sanitized_params
    
    def sanitize_input(self, value):
        if isinstance(value, str):
            # Remover caracteres peligrosos
            value = re.sub(r'[<>\"\';&]', '', value)
            # Limitar longitud
            value = value[:500]
        
        return value
```

## 🎯 Próximos Pasos

Con las AI Actions configuradas:

1. **[Flujos Conversacionales](conversation-flows.md)** - Diseñar flujos que usen actions
2. **[Integraciones API](api-integrations.md)** - Profundizar en integraciones
3. **[Testing y Validación](../operations/testing.md)** - Probar las actions

---

**Recuerda**: Las AI Actions son el puente entre la conversación y la acción real. Una buena configuración de actions puede transformar un simple chatbot en un asistente verdaderamente útil y eficiente.