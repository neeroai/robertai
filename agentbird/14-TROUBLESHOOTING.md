# 14 - Troubleshooting

## 🔍 Guía de Solución de Problemas

### Framework de Diagnóstico

```
┌─────────────────────────────────────────────────────────────┐
│                  1. Identificar Síntomas                      │
│         ¿Qué está pasando? ¿Cuándo comenzó?                 │
└──────────────────────────┬──────────────────────────────────┘
                           │
┌──────────────────────────▼──────────────────────────────────┐
│                  2. Recopilar Información                    │
│      Logs, métricas, estado del sistema, contexto           │
└──────────────────────────┬──────────────────────────────────┘
                           │
┌──────────────────────────▼──────────────────────────────────┐
│                    3. Aislar el Problema                     │
│        ¿Componente específico? ¿Reproducible?               │
└──────────────────────────┬──────────────────────────────────┘
                           │
┌──────────────────────────▼──────────────────────────────────┐
│                    4. Formular Hipótesis                     │
│         Posibles causas basadas en evidencia                 │
└──────────────────────────┬──────────────────────────────────┘
                           │
┌──────────────────────────▼──────────────────────────────────┐
│                    5. Probar Soluciones                      │
│      Implementar fixes, verificar resultados                 │
└──────────────────────────┬──────────────────────────────────┘
                           │
┌──────────────────────────▼──────────────────────────────────┐
│                    6. Documentar y Prevenir                  │
│        Registro de solución, mejoras preventivas             │
└─────────────────────────────────────────────────────────────┘
```

## 🚨 Problemas Comunes y Soluciones

### 1. El AI Agent no responde

#### Síntomas
- No hay respuesta después de enviar mensaje
- Timeout en la conversación
- Indicador de "escribiendo" permanente

#### Diagnóstico
```bash
# 1. Verificar estado del servicio
curl -X GET https://api.bird.com/v1/health

# 2. Verificar logs del AI Agent
bird-cli logs --agent-id jako --tail 100

# 3. Verificar conectividad API
curl -X GET https://api.neero.link/v1/health \
  -H "X-API-Key: $API_KEY"

# 4. Verificar métricas
bird-cli metrics --agent-id jako --period 1h
```

#### Soluciones
```python
# Solución 1: Reiniciar el agente
def restart_ai_agent(agent_id):
    """Reinicio suave del AI Agent"""
    
    # Verificar conversaciones activas
    active_conversations = get_active_conversations(agent_id)
    
    if active_conversations:
        # Guardar estado
        save_conversation_state(active_conversations)
    
    # Reiniciar agente
    bird_client.agents.restart(agent_id)
    
    # Esperar a que esté listo
    wait_for_agent_ready(agent_id, timeout=30)
    
    # Restaurar conversaciones
    if active_conversations:
        restore_conversations(active_conversations)

# Solución 2: Verificar y reparar integraciones
def check_and_repair_integrations():
    integrations = [
        {'name': 'koaj_api', 'url': 'https://api.neero.link/v1/health'},
        {'name': 'knowledge_base', 'check': check_knowledge_base},
        {'name': 'webhooks', 'check': check_webhook_connectivity}
    ]
    
    for integration in integrations:
        if not integration['check']():
            repair_integration(integration['name'])
```

### 2. Respuestas incorrectas o incoherentes

#### Síntomas
- Respuestas que no tienen sentido
- Información desactualizada
- Comportamiento errático

#### Diagnóstico
```python
class ResponseDiagnostics:
    def diagnose_response_issues(self, conversation_id):
        """Diagnosticar problemas de respuesta"""
        
        # Obtener conversación completa
        conversation = self.get_conversation(conversation_id)
        
        diagnostics = {
            'conversation_id': conversation_id,
            'issues_found': []
        }
        
        # Verificar coherencia de intents
        intent_flow = self.analyze_intent_flow(conversation)
        if intent_flow['inconsistent']:
            diagnostics['issues_found'].append({
                'type': 'intent_inconsistency',
                'details': intent_flow['inconsistencies']
            })
        
        # Verificar knowledge base
        kb_check = self.verify_knowledge_base_responses(conversation)
        if kb_check['outdated']:
            diagnostics['issues_found'].append({
                'type': 'outdated_knowledge',
                'documents': kb_check['outdated_docs']
            })
        
        # Verificar contexto
        context_check = self.verify_context_handling(conversation)
        if context_check['lost_context']:
            diagnostics['issues_found'].append({
                'type': 'context_loss',
                'at_message': context_check['lost_at']
            })
        
        return diagnostics
```

#### Soluciones
```python
# Solución 1: Actualizar Knowledge Base
def update_knowledge_base():
    outdated_docs = find_outdated_documents()
    
    for doc in outdated_docs:
        # Obtener versión actualizada
        updated_content = get_updated_content(doc['id'])
        
        # Actualizar en Bird.com
        bird_client.knowledge_base.update(
            document_id=doc['id'],
            content=updated_content
        )
    
    # Forzar re-indexación
    bird_client.knowledge_base.reindex()

# Solución 2: Ajustar modelo y parámetros
def tune_ai_parameters():
    new_config = {
        'temperature': 0.7,  # Reducir para más consistencia
        'top_p': 0.9,
        'frequency_penalty': 0.3,  # Evitar repetición
        'presence_penalty': 0.3,
        'max_tokens': 500
    }
    
    bird_client.agents.update_config(
        agent_id='jako',
        model_config=new_config
    )

# Solución 3: Mejorar prompts
def enhance_system_prompt():
    improved_prompt = """
    Eres Jako, asistente de KOAJ. IMPORTANTE:
    1. SIEMPRE verifica la información antes de responder
    2. Si no estás seguro, di "Déjame verificar eso"
    3. Mantén coherencia con mensajes anteriores
    4. Usa el contexto de la conversación completa
    """
    
    bird_client.agents.update_prompt(
        agent_id='jako',
        system_prompt=improved_prompt
    )
```

### 3. Problemas de integración con API

#### Síntomas
- Error al buscar productos
- Timeout en acciones
- Datos no actualizados

#### Diagnóstico
```bash
# Test de conectividad
curl -X POST https://api.neero.link/v1/bird/ai-search \
  -H "X-API-Key: $API_KEY" \
  -H "Content-Type: application/json" \
  -d '{"query": "vestido", "limit": 1}'

# Verificar rate limits
curl -I https://api.neero.link/v1/bird/ai-search \
  -H "X-API-Key: $API_KEY"
# Buscar headers: X-RateLimit-Remaining, X-RateLimit-Reset

# Verificar certificados SSL
openssl s_client -connect api.neero.link:443 -servername api.neero.link
```

#### Soluciones
```python
# Solución 1: Implementar circuit breaker
class APICircuitBreaker:
    def __init__(self):
        self.failure_threshold = 5
        self.timeout_duration = 60
        self.failure_count = 0
        self.last_failure_time = None
        self.state = 'closed'
    
    def call_api(self, func, *args, **kwargs):
        if self.state == 'open':
            if time.time() - self.last_failure_time > self.timeout_duration:
                self.state = 'half-open'
            else:
                return self.fallback_response()
        
        try:
            result = func(*args, **kwargs)
            if self.state == 'half-open':
                self.state = 'closed'
                self.failure_count = 0
            return result
        except Exception as e:
            self.failure_count += 1
            self.last_failure_time = time.time()
            
            if self.failure_count >= self.failure_threshold:
                self.state = 'open'
                self.alert_team("API Circuit Breaker OPEN")
            
            return self.fallback_response()

# Solución 2: Implementar caché local
class LocalAPICache:
    def __init__(self):
        self.cache = TTLCache(maxsize=1000, ttl=300)  # 5 min cache
    
    def get_or_fetch(self, key, fetch_func):
        # Intentar obtener de cache
        if key in self.cache:
            return self.cache[key]
        
        try:
            # Fetch desde API
            data = fetch_func()
            self.cache[key] = data
            return data
        except APIError:
            # Si falla, buscar en cache expirado
            expired_data = self.get_expired(key)
            if expired_data:
                return expired_data
            raise

# Solución 3: Configurar retry con backoff
@retry(
    stop=stop_after_attempt(3),
    wait=wait_exponential(multiplier=1, min=4, max=10),
    retry=retry_if_exception_type(APIError)
)
def call_api_with_retry(endpoint, data):
    response = requests.post(endpoint, json=data, timeout=10)
    response.raise_for_status()
    return response.json()
```

### 4. Alto consumo de recursos

#### Síntomas
- Respuestas lentas
- Timeouts frecuentes
- Costos elevados de API

#### Diagnóstico
```python
def diagnose_resource_usage():
    """Diagnosticar uso de recursos"""
    
    metrics = {
        'api_calls': get_api_call_count(period='24h'),
        'tokens_used': get_token_usage(period='24h'),
        'cache_hit_rate': calculate_cache_hit_rate(),
        'avg_response_time': get_avg_response_time(),
        'concurrent_conversations': get_concurrent_conversations()
    }
    
    issues = []
    
    # Verificar uso excesivo de API
    if metrics['api_calls'] > 10000:
        issues.append('Excessive API calls')
    
    # Verificar cache hit rate bajo
    if metrics['cache_hit_rate'] < 0.6:
        issues.append('Low cache hit rate')
    
    # Verificar tokens por conversación
    avg_tokens = metrics['tokens_used'] / metrics['api_calls']
    if avg_tokens > 1000:
        issues.append('High token usage per request')
    
    return {
        'metrics': metrics,
        'issues': issues,
        'recommendations': generate_optimization_recommendations(metrics)
    }
```

#### Soluciones
```python
# Solución 1: Optimizar uso de tokens
def optimize_token_usage():
    optimizations = {
        'max_tokens': 500,  # Reducir de 800
        'system_prompt': compress_prompt(current_prompt),
        'conversation_history': 5,  # Limitar historial
        'summarize_long_conversations': True
    }
    
    apply_optimizations(optimizations)

# Solución 2: Implementar respuestas pre-calculadas
class PrecomputedResponses:
    def __init__(self):
        self.common_queries = self.analyze_common_queries()
        self.precomputed = {}
        
    def precompute_responses(self):
        for query in self.common_queries:
            response = self.generate_optimal_response(query)
            self.precomputed[self.normalize_query(query)] = response
    
    def get_response(self, query):
        normalized = self.normalize_query(query)
        if normalized in self.precomputed:
            return self.precomputed[normalized]
        return None

# Solución 3: Implementar batching
class RequestBatcher:
    def __init__(self):
        self.batch = []
        self.batch_size = 10
        self.batch_timeout = 100  # ms
        
    async def add_request(self, request):
        self.batch.append(request)
        
        if len(self.batch) >= self.batch_size:
            return await self.process_batch()
        
        # Esperar más requests o timeout
        await asyncio.sleep(self.batch_timeout / 1000)
        return await self.process_batch()
    
    async def process_batch(self):
        if not self.batch:
            return []
        
        # Procesar todo el batch en una sola llamada
        results = await batch_api_call(self.batch)
        self.batch = []
        return results
```

### 5. Problemas de escalamiento

#### Síntomas
- Sistema lento en horas pico
- Conversaciones en cola
- Timeouts durante alta demanda

#### Diagnóstico
```python
def analyze_scaling_issues():
    """Analizar problemas de escalamiento"""
    
    # Obtener métricas de carga
    load_metrics = {
        'current_load': get_current_load(),
        'peak_load_today': get_peak_load(period='24h'),
        'queue_depth': get_queue_depth(),
        'response_time_p95': get_response_time_percentile(95),
        'error_rate': get_error_rate()
    }
    
    # Identificar bottlenecks
    bottlenecks = []
    
    if load_metrics['queue_depth'] > 50:
        bottlenecks.append({
            'component': 'message_queue',
            'severity': 'high',
            'metric': f"Queue depth: {load_metrics['queue_depth']}"
        })
    
    if load_metrics['response_time_p95'] > 3000:
        bottlenecks.append({
            'component': 'api_response',
            'severity': 'medium',
            'metric': f"P95 response time: {load_metrics['response_time_p95']}ms"
        })
    
    return {
        'metrics': load_metrics,
        'bottlenecks': bottlenecks,
        'scaling_recommendations': calculate_scaling_needs(load_metrics)
    }
```

#### Soluciones
```python
# Solución 1: Auto-scaling configuration
def configure_auto_scaling():
    scaling_policy = {
        'metric': 'queue_depth',
        'target_value': 20,
        'scale_up_threshold': 50,
        'scale_down_threshold': 10,
        'cooldown_period': 300,  # 5 minutes
        'min_instances': 2,
        'max_instances': 20
    }
    
    implement_scaling_policy(scaling_policy)

# Solución 2: Implementar load balancing
def setup_load_balancing():
    lb_config = {
        'algorithm': 'least_connections',
        'health_check': {
            'endpoint': '/health',
            'interval': 30,
            'timeout': 5,
            'unhealthy_threshold': 2
        },
        'sticky_sessions': {
            'enabled': True,
            'duration': 3600  # 1 hour
        }
    }
    
    configure_load_balancer(lb_config)

# Solución 3: Optimizar queries y caching
def optimize_for_scale():
    # Implementar caching agresivo
    cache_config = {
        'product_search': {'ttl': 300, 'max_size': 10000},
        'inventory_check': {'ttl': 60, 'max_size': 5000},
        'user_preferences': {'ttl': 3600, 'max_size': 50000}
    }
    
    # Pre-warm cache con queries comunes
    common_queries = get_most_common_queries(limit=100)
    for query in common_queries:
        cache_warmup(query)
    
    # Implementar read replicas para distribución de carga
    configure_read_replicas(count=3)
```

## 🔧 Herramientas de Diagnóstico

### Debug Toolkit

```python
class DebugToolkit:
    """Kit de herramientas para debugging"""
    
    def __init__(self):
        self.tools = {
            'conversation_analyzer': ConversationAnalyzer(),
            'api_tracer': APITracer(),
            'performance_profiler': PerformanceProfiler(),
            'log_aggregator': LogAggregator()
        }
    
    def debug_conversation(self, conversation_id):
        """Debug completo de una conversación"""
        
        print(f"🔍 Debugging conversation: {conversation_id}")
        
        # 1. Timeline de eventos
        timeline = self.build_conversation_timeline(conversation_id)
        self.print_timeline(timeline)
        
        # 2. Análisis de intents
        intents = self.analyze_intents(conversation_id)
        print(f"\n📊 Intent Analysis:")
        for intent in intents:
            print(f"  - {intent['name']}: {intent['confidence']:.2f}")
        
        # 3. API calls realizadas
        api_calls = self.trace_api_calls(conversation_id)
        print(f"\n🔌 API Calls ({len(api_calls)}):")
        for call in api_calls:
            print(f"  - {call['endpoint']}: {call['duration']}ms - {call['status']}")
        
        # 4. Errores encontrados
        errors = self.find_errors(conversation_id)
        if errors:
            print(f"\n❌ Errors Found ({len(errors)}):")
            for error in errors:
                print(f"  - {error['timestamp']}: {error['message']}")
        
        # 5. Recomendaciones
        recommendations = self.generate_debug_recommendations(
            timeline, intents, api_calls, errors
        )
        
        print(f"\n💡 Recommendations:")
        for rec in recommendations:
            print(f"  - {rec}")
```

### Log Analysis

```python
class LogAnalyzer:
    """Analizador avanzado de logs"""
    
    def analyze_error_patterns(self, timeframe='1h'):
        """Analizar patrones de errores"""
        
        logs = self.fetch_logs(timeframe)
        
        # Agrupar por tipo de error
        error_groups = defaultdict(list)
        for log in logs:
            if log['level'] == 'ERROR':
                error_type = self.classify_error(log['message'])
                error_groups[error_type].append(log)
        
        # Analizar cada grupo
        analysis = {}
        for error_type, errors in error_groups.items():
            analysis[error_type] = {
                'count': len(errors),
                'first_seen': min(e['timestamp'] for e in errors),
                'last_seen': max(e['timestamp'] for e in errors),
                'pattern': self.find_pattern(errors),
                'likely_cause': self.determine_cause(error_type, errors)
            }
        
        return analysis
```

## 📊 Monitoreo Proactivo

### Health Checks

```python
class ProactiveMonitoring:
    """Sistema de monitoreo proactivo"""
    
    def __init__(self):
        self.health_checks = [
            self.check_response_time,
            self.check_error_rate,
            self.check_api_availability,
            self.check_knowledge_base_sync,
            self.check_conversation_flow
        ]
        
        self.thresholds = {
            'response_time': 2000,  # ms
            'error_rate': 0.02,     # 2%
            'api_availability': 0.99, # 99%
            'kb_sync_lag': 300,     # 5 minutes
            'conversation_completion': 0.7  # 70%
        }
    
    async def run_health_checks(self):
        """Ejecutar todos los health checks"""
        
        results = {
            'timestamp': datetime.now(),
            'overall_health': 'healthy',
            'checks': []
        }
        
        for check in self.health_checks:
            try:
                result = await check()
                results['checks'].append(result)
                
                if result['status'] != 'healthy':
                    results['overall_health'] = 'degraded'
                    
                    # Acción automática si es crítico
                    if result['severity'] == 'critical':
                        await self.auto_remediate(result)
                        
            except Exception as e:
                results['checks'].append({
                    'name': check.__name__,
                    'status': 'error',
                    'error': str(e)
                })
                results['overall_health'] = 'unhealthy'
        
        return results
```

## 🚑 Recuperación de Desastres

### Disaster Recovery Plan

```python
class DisasterRecovery:
    """Plan de recuperación ante desastres"""
    
    def __init__(self):
        self.recovery_procedures = {
            'complete_outage': self.recover_from_outage,
            'data_corruption': self.recover_from_corruption,
            'security_breach': self.recover_from_breach,
            'api_failure': self.recover_from_api_failure
        }
    
    async def execute_recovery(self, disaster_type):
        """Ejecutar procedimiento de recuperación"""
        
        print(f"🚨 Iniciando recuperación de: {disaster_type}")
        
        # 1. Activar modo mantenimiento
        await self.enable_maintenance_mode()
        
        # 2. Notificar stakeholders
        await self.notify_stakeholders(disaster_type)
        
        # 3. Ejecutar procedimiento específico
        recovery_proc = self.recovery_procedures.get(disaster_type)
        if recovery_proc:
            recovery_result = await recovery_proc()
        else:
            recovery_result = await self.generic_recovery()
        
        # 4. Verificar recuperación
        verification = await self.verify_recovery()
        
        # 5. Restaurar servicio gradualmente
        if verification['success']:
            await self.gradual_service_restoration()
        
        # 6. Post-mortem
        await self.schedule_postmortem(disaster_type, recovery_result)
        
        return recovery_result
```

## 📋 Checklist de Troubleshooting

### Quick Reference

```yaml
Problema: AI no responde
  ✓ Verificar estado del servicio
  ✓ Revisar logs recientes
  ✓ Verificar conectividad API
  ✓ Revisar límites de rate
  ✓ Verificar configuración del agente

Problema: Respuestas incorrectas
  ✓ Verificar Knowledge Base actualizado
  ✓ Revisar configuración del modelo
  ✓ Analizar flujo de intents
  ✓ Verificar contexto de conversación
  ✓ Revisar system prompt

Problema: Lentitud del sistema
  ✓ Verificar métricas de carga
  ✓ Revisar uso de recursos
  ✓ Verificar cache hit rate
  ✓ Analizar queries lentas
  ✓ Verificar configuración de escalamiento

Problema: Errores de integración
  ✓ Verificar conectividad de red
  ✓ Revisar autenticación/API keys
  ✓ Verificar rate limits
  ✓ Revisar logs de API
  ✓ Verificar formato de requests/responses

Problema: Seguridad
  ✓ Revisar logs de seguridad
  ✓ Verificar intentos de acceso fallidos
  ✓ Revisar configuración de firewall
  ✓ Verificar certificados SSL
  ✓ Analizar patrones anómalos
```

## 🎯 Próximos Pasos

Con las herramientas de troubleshooting:

1. **[15-CASOS-DE-USO.md](15-CASOS-DE-USO.md)** - Ver casos reales resueltos
2. **[templates/](templates/)** - Templates de debugging
3. **[scripts/](scripts/)** - Scripts de diagnóstico automatizado

---

**Recuerda**: El mejor troubleshooting es el que no necesitas hacer. Invierte en monitoreo proactivo, alertas inteligentes y documentación clara. Cuando algo falla, mantén la calma, sigue el proceso y documenta todo para futuras referencias.