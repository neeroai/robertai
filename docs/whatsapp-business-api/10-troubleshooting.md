# Guía de Resolución de Problemas - WhatsApp Business API

## Introducción

Esta guía proporciona soluciones para problemas comunes al implementar WhatsApp Business API con Bird.com AI Employees. Incluye diagnósticos, soluciones paso a paso y herramientas de debugging.

## 1. Problemas de Autenticación

### Error: "Invalid access token"

**Síntomas:**
- Código de error: 401
- Mensaje: "Invalid access token" o "Access token has expired"
- Todas las llamadas a la API fallan

**Causas posibles:**
1. Token de acceso expirado
2. Token revocado por cambios en permisos
3. Token mal configurado en variables de entorno
4. Aplicación de Facebook eliminada o suspendida

**Solución:**

```python
# token_diagnostic.py
import aiohttp
import asyncio
import os
from datetime import datetime

async def diagnose_token_issue(access_token: str):
    """Diagnosticar problemas con el token de acceso"""
    
    print("=== DIAGNÓSTICO DE TOKEN ===")
    print(f"Token (primeros 20 caracteres): {access_token[:20]}...")
    
    # Test 1: Verificar formato del token
    if not access_token.startswith(('EAAG', 'EAA')):
        print("❌ Error: Formato de token inválido")
        print("Solución: Regenerar token en Facebook Business Manager")
        return False
    
    # Test 2: Verificar validez del token
    url = "https://graph.facebook.com/v18.0/me"
    headers = {"Authorization": f"Bearer {access_token}"}
    
    try:
        async with aiohttp.ClientSession() as session:
            async with session.get(url, headers=headers) as response:
                if response.status == 200:
                    data = await response.json()
                    print(f"✅ Token válido para aplicación: {data.get('name', 'N/A')}")
                    
                    # Test 3: Verificar permisos de WhatsApp
                    return await check_whatsapp_permissions(access_token)
                
                elif response.status == 401:
                    error_data = await response.json()
                    error_code = error_data.get('error', {}).get('code')
                    
                    if error_code == 190:
                        print("❌ Token expirado o inválido")
                        print("Solución: Regenerar token en Facebook Business Manager")
                    else:
                        print(f"❌ Error de autenticación: {error_data}")
                    
                    return False
                
                else:
                    print(f"❌ Error HTTP: {response.status}")
                    return False
    
    except Exception as e:
        print(f"❌ Error de conexión: {e}")
        return False

async def check_whatsapp_permissions(access_token: str):
    """Verificar permisos específicos de WhatsApp"""
    
    # Verificar acceso a Business Account
    business_account_id = os.getenv('WHATSAPP_BUSINESS_ACCOUNT_ID')
    if not business_account_id:
        print("⚠️ Warning: WHATSAPP_BUSINESS_ACCOUNT_ID no configurado")
        return True
    
    url = f"https://graph.facebook.com/v18.0/{business_account_id}"
    headers = {"Authorization": f"Bearer {access_token}"}
    
    try:
        async with aiohttp.ClientSession() as session:
            async with session.get(url, headers=headers) as response:
                if response.status == 200:
                    data = await response.json()
                    print(f"✅ Acceso a Business Account: {data.get('name', 'N/A')}")
                    
                    # Verificar números de teléfono disponibles
                    return await check_phone_numbers(access_token, business_account_id)
                else:
                    error_data = await response.json()
                    print(f"❌ No se puede acceder al Business Account: {error_data}")
                    return False
    
    except Exception as e:
        print(f"❌ Error verificando Business Account: {e}")
        return False

async def check_phone_numbers(access_token: str, business_account_id: str):
    """Verificar números de teléfono asociados"""
    
    url = f"https://graph.facebook.com/v18.0/{business_account_id}/phone_numbers"
    headers = {"Authorization": f"Bearer {access_token}"}
    
    try:
        async with aiohttp.ClientSession() as session:
            async with session.get(url, headers=headers) as response:
                if response.status == 200:
                    data = await response.json()
                    phone_numbers = data.get('data', [])
                    
                    if phone_numbers:
                        print(f"✅ Números disponibles: {len(phone_numbers)}")
                        for phone in phone_numbers:
                            status = phone.get('status', 'UNKNOWN')
                            number = phone.get('display_phone_number', 'N/A')
                            print(f"  - {number}: {status}")
                    else:
                        print("⚠️ No hay números de teléfono configurados")
                    
                    return True
                else:
                    print(f"❌ Error obteniendo números: {response.status}")
                    return False
    
    except Exception as e:
        print(f"❌ Error verificando números: {e}")
        return False

# Script de diagnóstico
async def run_token_diagnostic():
    access_token = os.getenv('WHATSAPP_ACCESS_TOKEN')
    
    if not access_token:
        print("❌ WHATSAPP_ACCESS_TOKEN no configurado")
        print("Configura la variable de entorno y vuelve a intentar")
        return
    
    is_valid = await diagnose_token_issue(access_token)
    
    if is_valid:
        print("\n✅ Diagnóstico completado: Token configurado correctamente")
    else:
        print("\n❌ Diagnóstico completado: Se encontraron problemas")
        print("\nPasos para solucionar:")
        print("1. Ir a Facebook Business Manager")
        print("2. Navegar a WhatsApp Business API > Configuración")
        print("3. Generar nuevo token de acceso")
        print("4. Actualizar variable de entorno WHATSAPP_ACCESS_TOKEN")

if __name__ == "__main__":
    asyncio.run(run_token_diagnostic())
```

### Error: "Permission denied"

**Síntomas:**
- Código de error: 403
- No se pueden enviar mensajes
- Acceso limitado a endpoints

**Solución:**

```python
# permission_checker.py
async def check_app_permissions():
    """Verificar permisos de la aplicación"""
    
    required_permissions = [
        'whatsapp_business_messaging',
        'whatsapp_business_management',
        'business_management'
    ]
    
    access_token = os.getenv('WHATSAPP_ACCESS_TOKEN')
    app_id = os.getenv('WHATSAPP_APP_ID')
    
    url = f"https://graph.facebook.com/v18.0/{app_id}/permissions"
    headers = {"Authorization": f"Bearer {access_token}"}
    
    try:
        async with aiohttp.ClientSession() as session:
            async with session.get(url, headers=headers) as response:
                if response.status == 200:
                    data = await response.json()
                    granted_permissions = [
                        perm['permission'] for perm in data.get('data', [])
                        if perm.get('status') == 'granted'
                    ]
                    
                    print("=== VERIFICACIÓN DE PERMISOS ===")
                    
                    for permission in required_permissions:
                        if permission in granted_permissions:
                            print(f"✅ {permission}: Concedido")
                        else:
                            print(f"❌ {permission}: FALTANTE")
                    
                    missing = set(required_permissions) - set(granted_permissions)
                    if missing:
                        print(f"\n⚠️ Permisos faltantes: {', '.join(missing)}")
                        print("Solicitar permisos en Facebook Business Manager")
                        return False
                    else:
                        print("\n✅ Todos los permisos están configurados")
                        return True
                
                else:
                    error_data = await response.json()
                    print(f"❌ Error verificando permisos: {error_data}")
                    return False
    
    except Exception as e:
        print(f"❌ Error de conexión: {e}")
        return False
```

## 2. Problemas de Envío de Mensajes

### Error: "Message failed to send"

**Síntomas:**
- Mensajes no se entregan
- Estado "failed" en webhooks
- Error 131047: "Re-engagement message"

**Diagnóstico y Solución:**

```python
# message_diagnostic.py
async def diagnose_message_failure(phone_number: str, message_data: dict):
    """Diagnosticar fallos en envío de mensajes"""
    
    print(f"=== DIAGNÓSTICO DE MENSAJE ===")
    print(f"Destinatario: {phone_number}")
    print(f"Tipo: {message_data.get('type', 'N/A')}")
    
    # Test 1: Validar formato de número
    if not validate_phone_number_format(phone_number):
        print("❌ Formato de número inválido")
        return False
    
    # Test 2: Verificar ventana de 24 horas
    last_user_message = await get_last_user_message_time(phone_number)
    if last_user_message:
        hours_since = (datetime.now() - last_user_message).total_seconds() / 3600
        if hours_since > 24:
            print(f"⚠️ Usuario fuera de ventana de 24h ({hours_since:.1f}h)")
            print("Solución: Usar mensaje de plantilla aprobada")
            return await suggest_template_message(phone_number, message_data)
    
    # Test 3: Validar contenido del mensaje
    content_issues = validate_message_content(message_data)
    if content_issues:
        print(f"❌ Problemas de contenido: {', '.join(content_issues)}")
        return False
    
    # Test 4: Verificar rate limits
    if await check_rate_limits(phone_number):
        print("⚠️ Rate limit excedido, reintentando más tarde")
        return False
    
    print("✅ Diagnóstico completado: No se encontraron problemas")
    return True

def validate_phone_number_format(phone_number: str) -> bool:
    """Validar formato de número de teléfono"""
    import re
    
    # Remover caracteres no numéricos excepto +
    clean_number = re.sub(r'[^0-9+]', '', phone_number)
    
    # Remover + inicial si existe
    if clean_number.startswith('+'):
        clean_number = clean_number[1:]
    
    # Verificar longitud y que no empiece con 0
    if len(clean_number) < 8 or len(clean_number) > 15:
        print(f"  - Longitud inválida: {len(clean_number)} dígitos")
        return False
    
    if clean_number.startswith('0'):
        print("  - No debe empezar con 0")
        return False
    
    return True

def validate_message_content(message_data: dict) -> list:
    """Validar contenido del mensaje"""
    issues = []
    message_type = message_data.get('type')
    
    if message_type == 'text':
        body = message_data.get('text', {}).get('body', '')
        if len(body) > 4096:
            issues.append("Texto excede 4096 caracteres")
        if not body.strip():
            issues.append("Mensaje vacío")
    
    elif message_type == 'interactive':
        interactive = message_data.get('interactive', {})
        
        if interactive.get('type') == 'button':
            buttons = interactive.get('action', {}).get('buttons', [])
            if len(buttons) > 3:
                issues.append("Máximo 3 botones permitidos")
            
            for i, button in enumerate(buttons):
                title = button.get('reply', {}).get('title', '')
                if len(title) > 20:
                    issues.append(f"Título de botón {i+1} excede 20 caracteres")
        
        elif interactive.get('type') == 'list':
            sections = interactive.get('action', {}).get('sections', [])
            total_rows = sum(len(section.get('rows', [])) for section in sections)
            if total_rows > 10:
                issues.append("Máximo 10 opciones en listas")
    
    return issues

async def suggest_template_message(phone_number: str, original_message: dict):
    """Sugerir mensaje de plantilla alternativo"""
    
    print("\n=== SUGERENCIA DE PLANTILLA ===")
    print("Para contactar usuarios fuera de la ventana de 24h:")
    print("1. Usar plantilla pre-aprobada por Meta")
    print("2. Ejemplos de plantillas comunes:")
    
    # Sugerir plantillas basadas en el contenido original
    message_type = original_message.get('type')
    
    if message_type == 'text':
        body = original_message.get('text', {}).get('body', '').lower()
        
        if any(word in body for word in ['bienvenido', 'hola', 'saludos']):
            print("   - Plantilla de bienvenida")
        elif any(word in body for word in ['oferta', 'promocion', 'descuento']):
            print("   - Plantilla promocional")
        elif any(word in body for word in ['recordatorio', 'cita', 'reserva']):
            print("   - Plantilla de recordatorio")
        else:
            print("   - Plantilla de seguimiento general")
    
    print("\n3. Código de ejemplo:")
    print(f'''
await send_template_message(
    phone_number="{phone_number}",
    template_name="nombre_plantilla",
    language_code="es",
    components=[
        {{
            "type": "body",
            "parameters": [
                {{"type": "text", "text": "valor_parametro"}}
            ]
        }}
    ]
)
''')
    
    return False
```

### Error: Rate Limit Exceeded

**Síntomas:**
- Código de error: 429 o 131026
- Mensajes rechazados temporalmente
- Header "Retry-After" en respuesta

**Solución con Rate Limiter Inteligente:**

```python
# intelligent_rate_limiter.py
import asyncio
from collections import defaultdict, deque
from datetime import datetime, timedelta
import logging

class IntelligentRateLimiter:
    """Rate limiter inteligente con predicción y adaptación"""
    
    def __init__(self):
        self.request_history = defaultdict(deque)
        self.rate_limits = {
            'messages': {'limit': 1000, 'window': 60, 'current': 0},
            'media': {'limit': 100, 'window': 60, 'current': 0}
        }
        self.adaptive_delays = defaultdict(float)
        self.last_rate_limit_hit = {}
        
    async def check_and_wait(self, endpoint_type: str = 'messages', 
                           phone_number: str = None) -> bool:
        """Verificar rate limit y esperar si es necesario"""
        
        key = f"{endpoint_type}_{phone_number or 'global'}"
        now = datetime.now()
        
        # Limpiar historial antiguo
        self._cleanup_old_requests(key, now)
        
        # Verificar si necesitamos esperar
        current_requests = len(self.request_history[key])
        limit_config = self.rate_limits[endpoint_type]
        
        if current_requests >= limit_config['limit']:
            # Calcular tiempo de espera
            wait_time = self._calculate_wait_time(key, now, limit_config)
            
            logging.warning(f"Rate limit alcanzado para {key}. Esperando {wait_time:.2f}s")
            
            # Esperar con backoff adaptativo
            adaptive_delay = self.adaptive_delays.get(key, 0)
            total_wait = wait_time + adaptive_delay
            
            await asyncio.sleep(total_wait)
            
            # Aumentar delay adaptativo si hay muchos rate limits
            self.adaptive_delays[key] = min(adaptive_delay + 0.5, 10.0)
            self.last_rate_limit_hit[key] = now
            
            return False  # Indica que hubo que esperar
        
        # Registrar request
        self.request_history[key].append(now)
        
        # Reducir delay adaptativo si no hay problemas
        if key in self.adaptive_delays:
            last_hit = self.last_rate_limit_hit.get(key)
            if last_hit and (now - last_hit).total_seconds() > 300:  # 5 minutos sin problemas
                self.adaptive_delays[key] = max(self.adaptive_delays[key] - 0.1, 0)
        
        return True  # Request puede proceder
    
    def _cleanup_old_requests(self, key: str, now: datetime):
        """Limpiar requests antiguos del historial"""
        cutoff_time = now - timedelta(seconds=60)
        
        while self.request_history[key] and self.request_history[key][0] < cutoff_time:
            self.request_history[key].popleft()
    
    def _calculate_wait_time(self, key: str, now: datetime, limit_config: dict) -> float:
        """Calcular tiempo de espera óptimo"""
        if not self.request_history[key]:
            return 0
        
        oldest_request = self.request_history[key][0]
        time_until_reset = (oldest_request + timedelta(seconds=limit_config['window']) - now).total_seconds()
        
        # Añadir buffer de seguridad
        return max(time_until_reset + 1, 0)
    
    def get_current_usage(self, endpoint_type: str = 'messages') -> dict:
        """Obtener uso actual de rate limit"""
        now = datetime.now()
        usage_by_key = {}
        
        for key in self.request_history:
            if key.startswith(endpoint_type):
                self._cleanup_old_requests(key, now)
                current_count = len(self.request_history[key])
                limit = self.rate_limits[endpoint_type]['limit']
                
                usage_by_key[key] = {
                    'current': current_count,
                    'limit': limit,
                    'percentage': (current_count / limit) * 100,
                    'adaptive_delay': self.adaptive_delays.get(key, 0)
                }
        
        return usage_by_key

# Uso del rate limiter inteligente
rate_limiter = IntelligentRateLimiter()

@measure_processing_time('text')
async def send_message_with_intelligent_rate_limiting(message_data: dict):
    """Enviar mensaje con rate limiting inteligente"""
    
    phone_number = message_data.get('to')
    
    # Verificar y esperar si es necesario
    await rate_limiter.check_and_wait('messages', phone_number)
    
    try:
        # Enviar mensaje
        result = await send_whatsapp_message(message_data)
        return result
    
    except WhatsAppAPIError as e:
        if e.code == 429 or e.subcode == 131026:  # Rate limit hit
            # Esperar según header Retry-After si está disponible
            retry_after = getattr(e, 'retry_after', 60)
            logging.warning(f"Rate limit hit, esperando {retry_after}s")
            await asyncio.sleep(retry_after)
            
            # Reintentar una vez
            return await send_whatsapp_message(message_data)
        else:
            raise
```

## 3. Problemas de Webhooks

### Webhook no recibe eventos

**Lista de verificación:**

```python
# webhook_diagnostic.py
import aiohttp
import asyncio
import json
from urllib.parse import urlparse

async def diagnose_webhook_issues(webhook_url: str, verify_token: str):
    """Diagnosticar problemas de webhook"""
    
    print("=== DIAGNÓSTICO DE WEBHOOK ===")
    print(f"URL: {webhook_url}")
    
    # Test 1: Verificar URL accesible
    if not await test_webhook_accessibility(webhook_url):
        return False
    
    # Test 2: Probar verificación
    if not await test_webhook_verification(webhook_url, verify_token):
        return False
    
    # Test 3: Verificar configuración SSL
    if not await test_ssl_configuration(webhook_url):
        return False
    
    # Test 4: Probar recepción de eventos de prueba
    await test_webhook_event_reception(webhook_url)
    
    print("\n✅ Diagnóstico completado")
    return True

async def test_webhook_accessibility(webhook_url: str) -> bool:
    """Test 1: Verificar accesibilidad de URL"""
    
    print("\n--- Test 1: Accesibilidad de URL ---")
    
    try:
        # Verificar formato de URL
        parsed_url = urlparse(webhook_url)
        if not parsed_url.scheme or not parsed_url.netloc:
            print("❌ URL mal formada")
            return False
        
        if parsed_url.scheme != 'https':
            print("❌ URL debe usar HTTPS")
            return False
        
        # Test de conectividad
        timeout = aiohttp.ClientTimeout(total=10)
        async with aiohttp.ClientSession(timeout=timeout) as session:
            async with session.get(webhook_url) as response:
                if response.status < 500:
                    print(f"✅ URL accesible (status: {response.status})")
                    return True
                else:
                    print(f"❌ URL retorna error de servidor: {response.status}")
                    return False
    
    except asyncio.TimeoutError:
        print("❌ Timeout conectando a webhook URL")
        print("Verificar:
        - Firewall/security groups
        - DNS resolution
        - Servidor funcionando")
        return False
    except Exception as e:
        print(f"❌ Error conectando: {e}")
        return False

async def test_webhook_verification(webhook_url: str, verify_token: str) -> bool:
    """Test 2: Probar verificación de webhook"""
    
    print("\n--- Test 2: Verificación de Webhook ---")
    
    challenge = "test_challenge_123456"
    params = {
        'hub.mode': 'subscribe',
        'hub.verify_token': verify_token,
        'hub.challenge': challenge
    }
    
    try:
        async with aiohttp.ClientSession() as session:
            async with session.get(webhook_url, params=params) as response:
                if response.status == 200:
                    response_text = await response.text()
                    if response_text == challenge:
                        print("✅ Verificación de webhook exitosa")
                        return True
                    else:
                        print(f"❌ Challenge incorrecto. Esperado: {challenge}, Recibido: {response_text}")
                        return False
                else:
                    error_text = await response.text()
                    print(f"❌ Verificación fallida (status: {response.status})")
                    print(f"Response: {error_text}")
                    return False
    
    except Exception as e:
        print(f"❌ Error en verificación: {e}")
        return False

async def test_ssl_configuration(webhook_url: str) -> bool:
    """Test 3: Verificar configuración SSL"""
    
    print("\n--- Test 3: Configuración SSL ---")
    
    try:
        import ssl
        import socket
        from urllib.parse import urlparse
        
        parsed_url = urlparse(webhook_url)
        hostname = parsed_url.hostname
        port = parsed_url.port or 443
        
        # Crear contexto SSL
        context = ssl.create_default_context()
        
        # Conectar y verificar certificado
        with socket.create_connection((hostname, port), timeout=10) as sock:
            with context.wrap_socket(sock, server_hostname=hostname) as ssock:
                cert = ssock.getpeercert()
                
                print(f"✅ Certificado SSL válido")
                print(f"  - Emisor: {cert.get('issuer', [[('O', 'Desconocido')]])[0][0][1]}")
                print(f"  - Sujeto: {cert.get('subject', [[('CN', 'Desconocido')]])[0][0][1]}")
                print(f"  - Expira: {cert.get('notAfter', 'Desconocido')}")
                
                return True
    
    except ssl.SSLError as e:
        print(f"❌ Error SSL: {e}")
        print("Verificar certificado SSL del servidor")
        return False
    except Exception as e:
        print(f"❌ Error verificando SSL: {e}")
        return False

async def test_webhook_event_reception(webhook_url: str):
    """Test 4: Probar recepción de eventos"""
    
    print("\n--- Test 4: Recepción de Eventos ---")
    print("Para probar la recepción de eventos reales:")
    print("1. Enviar mensaje de prueba desde el número configurado")
    print("2. Verificar logs del servidor webhook")
    print("3. Usar herramientas como ngrok para testing local")
    
    # Ejemplo de evento simulado
    sample_event = {
        "object": "whatsapp_business_account",
        "entry": [
            {
                "id": "BUSINESS_ACCOUNT_ID",
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
                                    "id": "wamid.TEST123",
                                    "timestamp": "1234567890",
                                    "text": {"body": "Test message"},
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
    
    print(f"\nEjemplo de evento de prueba:")
    print(json.dumps(sample_event, indent=2))

# Herramienta de diagnóstico completo
async def run_full_webhook_diagnostic():
    webhook_url = os.getenv('WEBHOOK_URL')
    verify_token = os.getenv('WHATSAPP_WEBHOOK_VERIFY_TOKEN')
    
    if not webhook_url:
        print("❌ WEBHOOK_URL no configurado")
        return
    
    if not verify_token:
        print("❌ WHATSAPP_WEBHOOK_VERIFY_TOKEN no configurado")
        return
    
    await diagnose_webhook_issues(webhook_url, verify_token)
```

### Verificación de Firma HMAC Fallando

**Herramienta de Debug:**

```python
# hmac_debug.py
import hmac
import hashlib
import json

def debug_hmac_verification(payload: bytes, received_signature: str, webhook_secret: str):
    """Debug detallado de verificación HMAC"""
    
    print("=== DEBUG VERIFICACIÓN HMAC ===")
    print(f"Payload length: {len(payload)} bytes")
    print(f"Payload preview: {payload[:100]}...")
    print(f"Received signature: {received_signature}")
    print(f"Webhook secret length: {len(webhook_secret)}")
    
    # Calcular firma esperada
    expected_signature = 'sha256=' + hmac.new(
        webhook_secret.encode(),
        payload,
        hashlib.sha256
    ).hexdigest()
    
    print(f"Expected signature: {expected_signature}")
    
    # Comparación detallada
    if received_signature == expected_signature:
        print("✅ Firmas coinciden")
        return True
    else:
        print("❌ Firmas NO coinciden")
        
        # Debug adicional
        print("\n--- DEBUGGING ADICIONAL ---")
        
        # Verificar formato
        if not received_signature.startswith('sha256='):
            print("❌ Firma no tiene prefijo 'sha256='")
        
        # Verificar longitud
        expected_len = len('sha256=') + 64  # 64 caracteres hex
        if len(received_signature) != expected_len:
            print(f"❌ Longitud incorrecta: {len(received_signature)} vs {expected_len}")
        
        # Probar con diferentes encodings
        print("\nProbando con diferentes encodings:")
        
        # UTF-8 (default)
        sig_utf8 = 'sha256=' + hmac.new(
            webhook_secret.encode('utf-8'),
            payload,
            hashlib.sha256
        ).hexdigest()
        print(f"UTF-8: {sig_utf8 == received_signature}")
        
        # ASCII
        try:
            sig_ascii = 'sha256=' + hmac.new(
                webhook_secret.encode('ascii'),
                payload,
                hashlib.sha256
            ).hexdigest()
            print(f"ASCII: {sig_ascii == received_signature}")
        except UnicodeEncodeError:
            print("ASCII: No compatible")
        
        return False

# Middleware de debug para FastAPI
from fastapi import Request

async def debug_webhook_middleware(request: Request):
    """Middleware para debug de webhooks"""
    
    # Leer body y headers
    body = await request.body()
    signature = request.headers.get('X-Hub-Signature-256', '')
    content_type = request.headers.get('Content-Type', '')
    
    print(f"\n=== WEBHOOK DEBUG INFO ===")
    print(f"Method: {request.method}")
    print(f"URL: {request.url}")
    print(f"Content-Type: {content_type}")
    print(f"Content-Length: {len(body)}")
    print(f"Signature Header: {signature}")
    
    # Verificar si es JSON válido
    try:
        json_data = json.loads(body)
        print(f"Valid JSON: ✅")
        print(f"Object type: {json_data.get('object', 'N/A')}")
        
        # Mostrar estructura del webhook
        if 'entry' in json_data:
            entries = json_data['entry']
            print(f"Entries: {len(entries)}")
            
            for i, entry in enumerate(entries):
                changes = entry.get('changes', [])
                print(f"  Entry {i}: {len(changes)} changes")
                
                for j, change in enumerate(changes):
                    field = change.get('field', 'N/A')
                    value = change.get('value', {})
                    messages = value.get('messages', [])
                    statuses = value.get('statuses', [])
                    
                    print(f"    Change {j}: field={field}, messages={len(messages)}, statuses={len(statuses)}")
    
    except json.JSONDecodeError as e:
        print(f"Invalid JSON: ❌ ({e})")
    
    # Debug HMAC
    webhook_secret = os.getenv('WHATSAPP_WEBHOOK_SECRET')
    if webhook_secret and signature:
        debug_hmac_verification(body, signature, webhook_secret)
    elif not webhook_secret:
        print("⚠️ WHATSAPP_WEBHOOK_SECRET no configurado")
    elif not signature:
        print("⚠️ Signature header faltante")
```

## 4. Problemas de Performance

### Tiempos de Respuesta Lentos

**Herramienta de Profiling:**

```python
# performance_profiler.py
import asyncio
import time
from contextlib import asynccontextmanager
from typing import Dict, List
import statistics
from datetime import datetime, timedelta

class PerformanceProfiler:
    """Profiler para medir performance de operaciones"""
    
    def __init__(self):
        self.measurements = defaultdict(list)
        self.active_operations = {}
    
    @asynccontextmanager
    async def measure(self, operation_name: str, metadata: dict = None):
        """Context manager para medir tiempo de operación"""
        
        operation_id = f"{operation_name}_{time.time()}"
        start_time = time.perf_counter()
        
        self.active_operations[operation_id] = {
            'name': operation_name,
            'start_time': start_time,
            'metadata': metadata or {}
        }
        
        try:
            yield operation_id
        finally:
            end_time = time.perf_counter()
            duration = end_time - start_time
            
            self.measurements[operation_name].append({
                'duration': duration,
                'timestamp': datetime.now(),
                'metadata': metadata or {}
            })
            
            del self.active_operations[operation_id]
            
            # Log si es lento
            if duration > 5.0:  # Más de 5 segundos
                logging.warning(f"Operación lenta: {operation_name} tomó {duration:.2f}s")
    
    def get_stats(self, operation_name: str = None) -> Dict:
        """Obtener estadísticas de performance"""
        
        if operation_name:
            measurements = self.measurements.get(operation_name, [])
            if not measurements:
                return {'error': f'No hay mediciones para {operation_name}'}
            
            durations = [m['duration'] for m in measurements[-100:]]  # Últimas 100
            
            return {
                'operation': operation_name,
                'count': len(durations),
                'avg_duration': statistics.mean(durations),
                'median_duration': statistics.median(durations),
                'min_duration': min(durations),
                'max_duration': max(durations),
                'p95_duration': statistics.quantiles(durations, n=20)[18] if len(durations) > 20 else max(durations),
                'recent_measurements': measurements[-10:]  # Últimas 10
            }
        else:
            # Stats globales
            all_stats = {}
            for op_name in self.measurements:
                all_stats[op_name] = self.get_stats(op_name)
            return all_stats
    
    def get_slow_operations(self, threshold: float = 2.0) -> List[Dict]:
        """Obtener operaciones lentas"""
        slow_ops = []
        
        for op_name, measurements in self.measurements.items():
            recent = measurements[-10:]  # Últimas 10
            avg_duration = statistics.mean([m['duration'] for m in recent])
            
            if avg_duration > threshold:
                slow_ops.append({
                    'operation': op_name,
                    'avg_duration': avg_duration,
                    'measurement_count': len(recent),
                    'slowest': max(m['duration'] for m in recent)
                })
        
        return sorted(slow_ops, key=lambda x: x['avg_duration'], reverse=True)

# Singleton profiler
profiler = PerformanceProfiler()

# Decorador para medir funciones
def profile_async(operation_name: str = None):
    def decorator(func):
        async def wrapper(*args, **kwargs):
            op_name = operation_name or f"{func.__module__}.{func.__name__}"
            async with profiler.measure(op_name):
                return await func(*args, **kwargs)
        return wrapper
    return decorator

# Ejemplo de uso
@profile_async("whatsapp_send_message")
async def send_whatsapp_message_profiled(message_data: dict):
    async with profiler.measure("message_validation"):
        # Validar mensaje
        await validate_message(message_data)
    
    async with profiler.measure("api_request"):
        # Llamada a API
        result = await make_api_request(message_data)
    
    async with profiler.measure("response_processing"):
        # Procesar respuesta
        processed_result = await process_response(result)
    
    return processed_result

# Endpoint para obtener stats de performance
@app.get("/debug/performance")
async def get_performance_stats():
    """Endpoint para obtener estadísticas de performance"""
    return {
        'stats': profiler.get_stats(),
        'slow_operations': profiler.get_slow_operations(threshold=1.0),
        'active_operations': len(profiler.active_operations)
    }
```

## 5. Herramientas de Monitoring

### Dashboard de Salud del Sistema

```python
# health_dashboard.py
from fastapi import FastAPI
from fastapi.responses import HTMLResponse
import asyncio
from datetime import datetime, timedelta

@app.get("/debug/health", response_class=HTMLResponse)
async def health_dashboard():
    """Dashboard web de salud del sistema"""
    
    # Recopilar datos de salud
    health_data = await collect_health_data()
    
    html_content = f"""
    <!DOCTYPE html>
    <html>
    <head>
        <title>WhatsApp API Health Dashboard</title>
        <style>
            body {{ font-family: Arial, sans-serif; margin: 20px; }}
            .status-ok {{ color: green; }}
            .status-warning {{ color: orange; }}
            .status-error {{ color: red; }}
            .metric {{ margin: 10px 0; padding: 10px; border: 1px solid #ccc; }}
            .grid {{ display: grid; grid-template-columns: 1fr 1fr; gap: 20px; }}
        </style>
        <script>
            // Auto-refresh cada 30 segundos
            setTimeout(() => location.reload(), 30000);
        </script>
    </head>
    <body>
        <h1>WhatsApp Business API - Health Dashboard</h1>
        <p>Last updated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}</p>
        
        <div class="grid">
            <div>
                <h2>System Status</h2>
                <div class="metric">
                    <strong>Overall Health:</strong> 
                    <span class="status-{health_data['overall_status'].lower()}">
                        {health_data['overall_status']}
                    </span>
                </div>
                <div class="metric">
                    <strong>API Connectivity:</strong> 
                    <span class="status-{health_data['api_status'].lower()}">
                        {health_data['api_status']}
                    </span>
                </div>
                <div class="metric">
                    <strong>Webhook Health:</strong> 
                    <span class="status-{health_data['webhook_status'].lower()}">
                        {health_data['webhook_status']}
                    </span>
                </div>
            </div>
            
            <div>
                <h2>Performance Metrics</h2>
                <div class="metric">
                    <strong>Messages Sent (24h):</strong> {health_data['messages_sent_24h']}
                </div>
                <div class="metric">
                    <strong>Success Rate:</strong> {health_data['success_rate']:.1f}%
                </div>
                <div class="metric">
                    <strong>Avg Response Time:</strong> {health_data['avg_response_time']:.2f}s
                </div>
                <div class="metric">
                    <strong>Queue Size:</strong> {health_data['queue_size']}
                </div>
            </div>
        </div>
        
        <h2>Recent Errors</h2>
        <div style="max-height: 300px; overflow-y: auto; border: 1px solid #ccc; padding: 10px;">
    """
    
    for error in health_data.get('recent_errors', []):
        html_content += f"""
            <div style="margin: 5px 0; font-family: monospace; font-size: 12px;">
                <strong>{error['timestamp']}</strong>: {error['message']}
            </div>
        """
    
    html_content += """
        </div>
        
        <h2>Rate Limit Status</h2>
        <div class="grid">
    """
    
    for endpoint, usage in health_data.get('rate_limit_usage', {}).items():
        status_class = "ok" if usage['percentage'] < 80 else "warning" if usage['percentage'] < 95 else "error"
        html_content += f"""
            <div class="metric">
                <strong>{endpoint}:</strong> {usage['current']}/{usage['limit']} 
                (<span class="status-{status_class}">{usage['percentage']:.1f}%</span>)
            </div>
        """
    
    html_content += """
        </div>
    </body>
    </html>
    """
    
    return html_content

async def collect_health_data() -> dict:
    """Recopilar datos de salud del sistema"""
    
    try:
        # Test conectividad API
        api_status = await test_api_connectivity()
        
        # Obtener métricas
        queue_stats = queue_manager.get_queue_stats() if 'queue_manager' in globals() else {}
        rate_limit_usage = rate_limiter.get_current_usage() if 'rate_limiter' in globals() else {}
        
        # Calcular métricas de 24h
        messages_24h = await get_messages_sent_24h()
        success_rate = await calculate_success_rate()
        avg_response_time = await get_average_response_time()
        
        # Errores recientes
        recent_errors = await get_recent_errors(limit=20)
        
        # Determinar estado general
        overall_status = "OK"
        if success_rate < 95:
            overall_status = "WARNING"
        if success_rate < 85 or api_status == "ERROR":
            overall_status = "ERROR"
        
        return {
            'overall_status': overall_status,
            'api_status': api_status,
            'webhook_status': "OK",  # Implementar verificación real
            'messages_sent_24h': messages_24h,
            'success_rate': success_rate,
            'avg_response_time': avg_response_time,
            'queue_size': queue_stats.get('queue_size', 0),
            'recent_errors': recent_errors,
            'rate_limit_usage': rate_limit_usage
        }
    
    except Exception as e:
        logging.error(f"Error recopilando datos de salud: {e}")
        return {
            'overall_status': 'ERROR',
            'error': str(e)
        }

async def test_api_connectivity() -> str:
    """Probar conectividad con WhatsApp API"""
    try:
        access_token = os.getenv('WHATSAPP_ACCESS_TOKEN')
        url = "https://graph.facebook.com/v18.0/me"
        headers = {"Authorization": f"Bearer {access_token}"}
        
        async with aiohttp.ClientSession() as session:
            async with session.get(url, headers=headers) as response:
                if response.status == 200:
                    return "OK"
                else:
                    return "WARNING"
    except Exception:
        return "ERROR"
```

## Próximos Pasos para Diagnóstico

1. **Ejecutar scripts de diagnóstico**:
   ```bash
   python token_diagnostic.py
   python webhook_diagnostic.py
   python performance_profiler.py
   ```

2. **Configurar monitoreo continuo**:
   - Implementar health checks automáticos
   - Configurar alertas proactivas
   - Dashboard de métricas en tiempo real

3. **Logs estructurados**:
   ```python
   import structlog
   
   logger = structlog.get_logger()
   logger.info(
       "message_sent",
       to=phone_number,
       message_id=result['messages'][0]['id'],
       processing_time=duration,
       success=True
   )
   ```

4. **Testing en producción**:
   - Tests de humo automáticos
   - Monitoreo de métricas clave
   - Alertas por degradación de performance

---

**Nota**: Esta guía cubre los problemas más comunes. Para issues específicos, usar las herramientas de diagnóstico y revisar logs detallados del sistema.