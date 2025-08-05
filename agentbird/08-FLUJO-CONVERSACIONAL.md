# 08 - Flujo Conversacional

## 🌊 Diseño de Conversaciones Efectivas

El flujo conversacional es el corazón de la experiencia del usuario con el AI Employee. Un buen diseño garantiza conversaciones naturales, eficientes y que cumplan los objetivos del negocio.

### Principios del Diseño Conversacional

```yaml
Core Principles:
  1. Naturalidad:
     - Conversaciones que fluyen como humano-humano
     - Evitar respuestas robóticas
     - Usar lenguaje contextual
  
  2. Eficiencia:
     - Mínimo número de interacciones para resolver
     - Opciones claras y accionables
     - Atajos para usuarios frecuentes
  
  3. Claridad:
     - Una idea por mensaje
     - Instrucciones explícitas
     - Confirmaciones cuando sea necesario
  
  4. Flexibilidad:
     - Múltiples caminos al mismo objetivo
     - Manejo de desviaciones
     - Recuperación de errores
```

## 🎯 El Embudo de Ventas de 9 Pasos (Caso KOAJ)

### Visualización del Embudo

```
┌─────────────────────────────────┐
│  1. Bienvenida y Segmentación   │ ← Entry Point
└────────────┬────────────────────┘
             │
┌────────────▼────────────────────┐
│  2. Consentimiento de Datos     │ ← Solo nuevos usuarios
└────────────┬────────────────────┘
             │
┌────────────▼────────────────────┐
│  3. Guiar por Categorías        │ ← Navegación principal
└────────────┬────────────────────┘
             │
┌────────────▼────────────────────┐
│  4. Perfilar el Estilo          │ ← Personalización
└────────────┬────────────────────┘
             │
┌────────────▼────────────────────┐
│  5. Consultar el Catálogo       │ ← Búsqueda inteligente
└────────────┬────────────────────┘
             │
┌────────────▼────────────────────┐
│  6. Presentar Resultados        │ ← Productos curados
└────────────┬────────────────────┘
             │
┌────────────▼────────────────────┐
│  7. Mostrar Detalles Producto   │ ← Información completa
└────────────┬────────────────────┘
             │
┌────────────▼────────────────────┐
│  8. Asistir con la Talla        │ ← Guía personalizada
└────────────┬────────────────────┘
             │
┌────────────▼────────────────────┐
│  9. Iniciar la Compra           │ ← Conversión
└─────────────────────────────────┘
```

### Implementación Detallada de Cada Paso

#### Paso 1: Bienvenida y Segmentación

```python
class WelcomeFlow:
    def __init__(self):
        self.greetings = {
            'morning': '¡Buenos días! ☀️ ¿Lista para encontrar el outfit perfecto?',
            'afternoon': '¡Buenas tardes! 🌟 ¿Qué look buscamos hoy?',
            'evening': '¡Buenas noches! 🌙 ¿Shopping nocturno? ¡Me encanta!',
            'default': '¡Hola! 👋 Soy Jako, tu asistente de moda KOAJ'
        }
    
    def start(self, context):
        greeting = self.get_time_based_greeting()
        
        return {
            'message': greeting,
            'quick_replies': [
                {'title': '👗 Mujer', 'payload': 'category_mujer'},
                {'title': '👔 Hombre', 'payload': 'category_hombre'},
                {'title': '🎁 Ofertas', 'payload': 'category_ofertas'},
                {'title': '❓ Necesito ayuda', 'payload': 'help'}
            ],
            'next_step': 'handle_category_selection'
        }
```

#### Paso 2: Consentimiento de Datos

```python
class ConsentFlow:
    def check_and_request_consent(self, user_id):
        if self.has_consent(user_id):
            return None  # Skip this step
        
        return {
            'message': '''Para brindarte la mejor experiencia personalizada, 
necesito tu consentimiento para procesar tus datos según nuestra 
política de privacidad.

✅ Podrás:
• Recibir recomendaciones personalizadas
• Guardar tus favoritos
• Acceder a ofertas exclusivas

🔒 Tus datos están seguros y no los compartimos con terceros.''',
            
            'buttons': [
                {'title': 'Acepto ✅', 'payload': 'consent_yes'},
                {'title': 'Más información', 'payload': 'consent_info'},
                {'title': 'No acepto', 'payload': 'consent_no'}
            ],
            'required': True
        }
```

#### Paso 3: Guiar por Categorías

```python
def guide_categories(category):
    category_trees = {
        'mujer': {
            'message': '¡Excelente elección! 💃 ¿Qué tipo de prenda buscas?',
            'options': [
                {'title': '👗 Vestidos', 'payload': 'cat_vestidos'},
                {'title': '👚 Blusas', 'payload': 'cat_blusas'},
                {'title': '👖 Jeans', 'payload': 'cat_jeans'},
                {'title': '👠 Calzado', 'payload': 'cat_calzado'},
                {'title': '💍 Accesorios', 'payload': 'cat_accesorios'},
                {'title': '🔍 Buscar algo específico', 'payload': 'free_search'}
            ]
        },
        'vestidos': {
            'message': '¡Los vestidos son mi especialidad! ✨ ¿Para qué ocasión?',
            'options': [
                {'title': '🌟 Casual día', 'payload': 'dress_casual'},
                {'title': '💼 Trabajo', 'payload': 'dress_work'},
                {'title': '🎉 Fiesta', 'payload': 'dress_party'},
                {'title': '🌹 Cena elegante', 'payload': 'dress_elegant'},
                {'title': '👰 Evento especial', 'payload': 'dress_special'}
            ]
        }
    }
    
    return category_trees.get(category)
```

#### Paso 4: Perfilar el Estilo

```python
class StyleProfiling:
    def profile_user_style(self, previous_selections):
        profiling_questions = {
            'dress_elegant': {
                'message': '¡Perfecto para una ocasión especial! 🌹 ¿Cómo describes tu estilo?',
                'options': [
                    {'title': '✨ Clásico elegante', 'style': 'classic'},
                    {'title': '🔥 Sexy y atrevido', 'style': 'bold'},
                    {'title': '🌸 Romántico', 'style': 'romantic'},
                    {'title': '💎 Minimalista chic', 'style': 'minimalist'},
                    {'title': '🎨 Único y original', 'style': 'unique'}
                ]
            }
        }
        
        return profiling_questions.get(previous_selections[-1])
    
    def ask_budget_subtly(self):
        return {
            'message': '¿Alguna preferencia especial? 🤔',
            'options': [
                {'title': '💰 Lo mejor calidad-precio', 'budget': 'value'},
                {'title': '✨ Calidad premium', 'budget': 'premium'},
                {'title': '🏷️ Ver ofertas primero', 'budget': 'budget'},
                {'title': '🎯 Mostrar todo', 'budget': 'all'}
            ]
        }
```

#### Paso 5: Consultar el Catálogo

```python
async def search_catalog(context):
    # Construir query inteligente
    search_params = {
        'query': build_smart_query(context),
        'filters': {
            'category': context['category_path'],
            'style': context['style_preference'],
            'price_range': get_price_range(context['budget_hint']),
            'occasion': context['occasion']
        },
        'limit': 5,
        'sort': 'relevance'
    }
    
    # Ejecutar búsqueda
    results = await execute_action('search_products', search_params)
    
    # Preparar para presentación
    return prepare_results_presentation(results)
```

#### Paso 6: Presentar Resultados

```python
def present_results(products):
    if not products:
        return {
            'message': '😔 No encontré exactamente lo que buscas, pero...',
            'actions': [
                {'title': '🔄 Ajustar búsqueda', 'action': 'refine'},
                {'title': '🎯 Ver similares', 'action': 'similar'},
                {'title': '💬 Hablar con asesor', 'action': 'human'}
            ]
        }
    
    intro_messages = [
        '¡WOW! Mira estas bellezas que encontré 😍',
        '¡Encontré opciones INCREÍBLES para ti! ✨',
        '¡Estos son perfectos para lo que buscas! 🎯'
    ]
    
    response = {
        'message': random.choice(intro_messages),
        'products': []
    }
    
    for idx, product in enumerate(products[:5], 1):
        response['products'].append({
            'number': idx,
            'title': f"{idx}. {product['title']} 💕",
            'price': format_price(product['price']),
            'highlight': get_product_highlight(product),
            'image': product['imageUrl']
        })
    
    response['prompt'] = '¿Cuál te gustó? Dime el número o "ver más" 🛍️'
    
    return response
```

#### Paso 7: Mostrar Detalles del Producto

```python
def show_product_details(product, user_context):
    # Crear descripción persuasiva
    description = f"""
🎯 *{product['title']}*

{generate_persuasive_description(product, user_context)}

💰 *Precio*: {format_price(product['price'])}
{get_discount_info(product)}

✨ *Por qué te encantará*:
{get_selling_points(product, user_context)}

📏 *Tallas disponibles*: {get_available_sizes(product)}

{get_urgency_trigger(product)}
"""
    
    return {
        'message': description,
        'image': product['imageUrl'],
        'buttons': [
            {'title': '📏 Guía de tallas', 'action': 'size_guide'},
            {'title': '🛒 Comprar ahora', 'action': 'add_to_cart'},
            {'title': '❤️ Guardar', 'action': 'save_favorite'},
            {'title': '🔄 Ver más opciones', 'action': 'back_to_results'}
        ]
    }

def generate_persuasive_description(product, context):
    templates = {
        'elegant_dress': 'Este vestido es la definición de elegancia. '
                        'Su corte {fit} realza tu figura mientras que el '
                        '{material} de primera calidad garantiza comodidad '
                        'toda la noche.',
        'casual_top': 'Una pieza versátil que se convertirá en tu favorita. '
                     'Perfecta para {occasion} y combina con todo.'
    }
    
    return templates.get(product['type'], product['description'])

def get_urgency_trigger(product):
    if product['stock'] < 5:
        return '⚡ ¡ÚLTIMAS UNIDADES! Solo quedan {stock} ⚡'
    elif product['is_new']:
        return '🆕 ¡RECIÉN LLEGADO! Sé de las primeras en tenerlo'
    elif product['is_trending']:
        return '🔥 ¡TRENDING! Lo más buscado esta semana'
    return ''
```

#### Paso 8: Asistir con la Talla

```python
class SizeAssistant:
    def provide_size_guidance(self, product_type, user_data=None):
        return {
            'message': '''📏 ¡Te ayudo a encontrar tu talla perfecta!
            
¿Cuáles son tus medidas? No te preocupes, es súper fácil:''',
            
            'interactive_guide': {
                'type': 'size_calculator',
                'fields': [
                    {'label': 'Busto/Pecho (cm)', 'name': 'bust', 'required': True},
                    {'label': 'Cintura (cm)', 'name': 'waist', 'required': True},
                    {'label': 'Cadera (cm)', 'name': 'hip', 'required': False}
                ],
                'help_image': 'how_to_measure.jpg'
            },
            
            'quick_options': [
                {'title': 'Soy talla S usual', 'size': 'S'},
                {'title': 'Soy talla M usual', 'size': 'M'},
                {'title': 'Soy talla L usual', 'size': 'L'},
                {'title': '📊 Ver tabla completa', 'action': 'show_size_chart'}
            ]
        }
    
    def calculate_recommended_size(self, measurements, product):
        # Lógica de cálculo basada en medidas y tipo de producto
        size_matrix = self.get_size_matrix(product['category'])
        recommended = self.match_measurements(measurements, size_matrix)
        
        return {
            'primary': recommended['size'],
            'confidence': recommended['confidence'],
            'message': self.get_size_recommendation_message(recommended),
            'alternative': recommended.get('alternative_size')
        }
```

#### Paso 9: Iniciar la Compra

```python
def initiate_purchase(product, size, context):
    # Crear resumen de compra
    summary = f"""
🛍️ *¡Excelente elección!*

📦 *Producto*: {product['title']}
📏 *Talla*: {size}
💰 *Precio*: {format_price(product['price'])}

✅ *Siguiente paso*: Agregar al carrito y proceder al pago
"""
    
    return {
        'message': summary,
        'call_to_action': {
            'primary': {
                'text': '🛒 AGREGAR AL CARRITO',
                'action': 'add_to_cart',
                'style': 'primary_large'
            },
            'secondary': [
                {'text': '💳 Compra rápida', 'action': 'quick_buy'},
                {'text': '🏪 Ver en tienda', 'action': 'store_locator'},
                {'text': '💬 Consultar asesor', 'action': 'human_agent'}
            ]
        },
        'urgency': generate_urgency_message(product),
        'trust_signals': [
            '🔒 Compra 100% segura',
            '📦 Envío gratis >$150.000',
            '↩️ 30 días para cambios'
        ]
    }
```

## 🔀 Manejo de Flujos Alternativos

### Detección de Intención y Redirección

```python
class FlowManager:
    def __init__(self):
        self.intent_patterns = {
            'search_specific': {
                'patterns': ['busco', 'necesito', 'quiero un', 'donde está'],
                'action': 'redirect_to_search'
            },
            'browse_catalog': {
                'patterns': ['ver todo', 'mostrar', 'qué tienen'],
                'action': 'show_categories'
            },
            'need_help': {
                'patterns': ['ayuda', 'no entiendo', 'problema', 'error'],
                'action': 'provide_assistance'
            },
            'talk_human': {
                'patterns': ['hablar con alguien', 'asesor', 'humano', 'persona'],
                'action': 'escalate_to_human'
            }
        }
    
    def detect_flow_change(self, user_input, current_step):
        for intent, config in self.intent_patterns.items():
            if any(pattern in user_input.lower() for pattern in config['patterns']):
                return self.handle_flow_change(intent, current_step)
        
        return None  # Continue current flow
```

### Recuperación de Contexto

```python
class ContextRecovery:
    def handle_unclear_response(self, user_input, expected_type):
        strategies = {
            'number_expected': {
                'message': 'No entendí qué número. ¿Puedes decirme el número de la opción que te gustó? (1, 2, 3...)',
                'show_options_again': True
            },
            'size_expected': {
                'message': '¿Qué talla necesitas? Por ejemplo: S, M, L, o dime tus medidas',
                'show_size_guide': True
            },
            'yes_no_expected': {
                'message': 'Disculpa, ¿es un sí o un no? 😊',
                'simplify_options': ['Sí ✅', 'No ❌']
            }
        }
        
        return strategies.get(expected_type, {
            'message': 'No entendí bien. ¿Podrías decirlo de otra forma?',
            'offer_help': True
        })
```

## 🎭 Estados Conversacionales

### Máquina de Estados

```python
class ConversationStateMachine:
    def __init__(self):
        self.states = {
            'greeting': {
                'entry': self.enter_greeting,
                'transitions': {
                    'category_selected': 'browsing',
                    'search_query': 'searching',
                    'help_requested': 'assistance'
                }
            },
            'browsing': {
                'entry': self.enter_browsing,
                'transitions': {
                    'subcategory_selected': 'filtering',
                    'product_selected': 'product_detail',
                    'back': 'greeting'
                }
            },
            'searching': {
                'entry': self.enter_searching,
                'transitions': {
                    'results_found': 'results_display',
                    'no_results': 'alternatives',
                    'refine': 'search_refinement'
                }
            },
            'product_detail': {
                'entry': self.enter_product_detail,
                'transitions': {
                    'size_help': 'size_assistance',
                    'add_to_cart': 'cart',
                    'back': 'results_display'
                }
            }
        }
        
        self.current_state = 'greeting'
        self.state_history = []
```

### Transiciones Inteligentes

```python
def handle_state_transition(self, trigger, context):
    current = self.states[self.current_state]
    
    if trigger in current['transitions']:
        # Guardar estado anterior
        self.state_history.append({
            'state': self.current_state,
            'context': context.copy(),
            'timestamp': datetime.now()
        })
        
        # Transición al nuevo estado
        new_state = current['transitions'][trigger]
        self.current_state = new_state
        
        # Ejecutar entrada del nuevo estado
        return self.states[new_state]['entry'](context)
    
    else:
        # Trigger no válido para el estado actual
        return self.handle_unexpected_transition(trigger, context)
```

## 📊 Optimización del Flujo

### A/B Testing de Flujos

```yaml
Flow Variants:
  Control:
    name: "9-step-funnel"
    steps: [greeting, consent, category, style, search, results, detail, size, purchase]
    
  Variant_A:
    name: "quick-search"
    steps: [greeting, search, results, detail, purchase]
    changes: "Skip category browsing for users who search directly"
    
  Variant_B:
    name: "visual-first"
    steps: [greeting, trending_products, select, customize, purchase]
    changes: "Show trending products immediately"

Metrics to Track:
  - Completion rate
  - Time to conversion
  - Drop-off points
  - User satisfaction
  - Revenue per conversation
```

### Análisis de Drop-off

```python
class DropOffAnalysis:
    def analyze_conversation_flow(self, conversations):
        drop_off_points = {}
        
        for conv in conversations:
            last_step = conv['steps'][-1]
            if not conv['completed']:
                drop_off_points[last_step] = drop_off_points.get(last_step, 0) + 1
        
        # Identificar puntos críticos
        critical_points = sorted(
            drop_off_points.items(), 
            key=lambda x: x[1], 
            reverse=True
        )[:5]
        
        return {
            'critical_drop_offs': critical_points,
            'recommendations': self.generate_improvement_recommendations(critical_points)
        }
```

## 🌍 Personalización por Contexto

### Adaptación Cultural

```python
def adapt_flow_to_culture(user_location, user_language):
    cultural_adaptations = {
        'colombia': {
            'greeting_style': 'warm_and_friendly',
            'formality': 'informal',
            'emoji_usage': 'high',
            'bargaining_expected': True,
            'payment_preferences': ['cash_on_delivery', 'installments']
        },
        'mexico': {
            'greeting_style': 'respectful_friendly',
            'formality': 'semi_formal',
            'emoji_usage': 'medium',
            'bargaining_expected': False,
            'payment_preferences': ['credit_card', 'oxxo']
        }
    }
    
    return cultural_adaptations.get(user_location, 'default')
```

### Flujos por Tipo de Usuario

```yaml
User Type Flows:
  New User:
    - Extended onboarding
    - More guidance
    - Educational content
    - Trust building emphasis
    
  Returning Customer:
    - Quick access to favorites
    - Based on purchase history
    - Personalized recommendations
    - Loyalty rewards mentioned
    
  VIP Customer:
    - Priority responses
    - Exclusive products shown
    - Personal shopper experience
    - Direct human access option
    
  Researcher:
    - Detailed product information
    - Comparison tools
    - Save for later prominent
    - No pressure tactics
```

## 🔧 Herramientas de Diseño

### Flow Builder Visual

```python
class VisualFlowBuilder:
    def export_flow_diagram(self, flow_definition):
        """Exporta el flujo como diagrama visual"""
        
        mermaid_diagram = "graph TD\n"
        
        for step in flow_definition['steps']:
            # Nodo principal
            mermaid_diagram += f"    {step['id']}[{step['name']}]\n"
            
            # Conexiones
            for transition in step['transitions']:
                mermaid_diagram += f"    {step['id']} -->|{transition['label']}| {transition['target']}\n"
        
        return mermaid_diagram
```

### Simulador de Conversaciones

```python
class ConversationSimulator:
    def simulate_flow(self, flow, user_persona):
        """Simula una conversación completa con un persona específico"""
        
        simulation_result = {
            'steps': [],
            'total_time': 0,
            'successful': False
        }
        
        current_step = flow['entry_point']
        
        while current_step != 'end':
            # Simular respuesta del usuario
            user_response = self.generate_user_response(
                current_step, 
                user_persona
            )
            
            # Procesar y avanzar
            next_step = self.process_response(
                current_step, 
                user_response
            )
            
            simulation_result['steps'].append({
                'step': current_step,
                'response': user_response,
                'time': self.calculate_response_time(user_persona)
            })
            
            current_step = next_step
        
        return simulation_result
```

## 📈 Métricas del Flujo

### KPIs Principales

```yaml
Flow Performance Metrics:
  Completion Rate:
    formula: completed_flows / total_started_flows
    target: > 70%
    benchmark: industry avg 45-60%
    
  Average Steps to Conversion:
    formula: sum(steps_per_conversion) / total_conversions
    target: < 12 steps
    insight: Fewer is generally better
    
  Time to Conversion:
    formula: avg(conversation_duration) for completed
    target: < 5 minutes
    benchmark: 3-7 minutes optimal
    
  Drop-off Rate by Step:
    formula: exits_at_step / entries_to_step
    alert: > 20% for any step
    action: Investigate and optimize
    
  Message Efficiency:
    formula: total_messages / conversations
    target: < 20 messages per conversation
    insight: Balance between clarity and brevity
```

## 🎯 Próximos Pasos

Con el flujo conversacional diseñado:

1. **[09-INTEGRACIONES-API.md](09-INTEGRACIONES-API.md)** - Conectar el flujo con APIs
2. **[11-TESTING-Y-VALIDACION.md](11-TESTING-Y-VALIDACION.md)** - Probar los flujos
3. **[12-MONITOREO-Y-ANALYTICS.md](12-MONITOREO-Y-ANALYTICS.md)** - Medir performance

---

**Recuerda**: Un buen flujo conversacional es invisible para el usuario. Debe sentirse natural, intuitivo y llevarlo exactamente donde quiere ir sin fricción.