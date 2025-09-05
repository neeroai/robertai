# Autenticación y Configuración - WhatsApp Business API

## Introducción

La autenticación en WhatsApp Business API utiliza un sistema de tokens de acceso y webhooks seguros. Esta guía cubre la configuración completa para integración con Bird.com AI Employees.

## Métodos de Autenticación

### 1. Token de Acceso (Access Token)

#### Obtención del Token
```bash
# Token temporal (24 horas) - Solo para testing
curl -X GET "https://graph.facebook.com/v18.0/me" \
  -H "Authorization: Bearer YOUR_TEMPORARY_TOKEN"

# Token permanente - Para producción
# Se obtiene a través de Facebook Business Manager
```

#### Estructura del Token
```json
{
  "access_token": "EAAG...", // Token de acceso
  "token_type": "Bearer",
  "expires_in": 86400,       // Segundos hasta expiración
  "scope": "whatsapp_business_management,whatsapp_business_messaging"
}
```

### 2. Configuración de Variables de Entorno

```bash
# .env file para desarrollo
WHATSAPP_ACCESS_TOKEN=your_access_token_here
WHATSAPP_PHONE_NUMBER_ID=your_phone_number_id
WHATSAPP_BUSINESS_ACCOUNT_ID=your_business_account_id
WHATSAPP_APP_ID=your_app_id
WHATSAPP_APP_SECRET=your_app_secret
WHATSAPP_WEBHOOK_VERIFY_TOKEN=your_custom_verify_token
WHATSAPP_WEBHOOK_SECRET=your_webhook_secret

# Bird.com Integration
BIRD_API_KEY=your_bird_api_key
BIRD_WORKSPACE_ID=your_workspace_id
BIRD_AI_EMPLOYEE_ID=your_ai_employee_id
```

### 3. Configuración en Bird.com Platform

```python
# bird_whatsapp_config.py
import os
from bird_ai import BirdClient

class WhatsAppBirdConfig:
    def __init__(self):
        self.bird_client = BirdClient(
            api_key=os.getenv('BIRD_API_KEY'),
            workspace_id=os.getenv('BIRD_WORKSPACE_ID')
        )
        
        self.whatsapp_config = {
            "channel": "whatsapp",
            "provider": "meta",
            "credentials": {
                "access_token": os.getenv('WHATSAPP_ACCESS_TOKEN'),
                "phone_number_id": os.getenv('WHATSAPP_PHONE_NUMBER_ID'),
                "business_account_id": os.getenv('WHATSAPP_BUSINESS_ACCOUNT_ID')
            },
            "webhook": {
                "url": f"{os.getenv('BASE_URL')}/webhooks/whatsapp",
                "verify_token": os.getenv('WHATSAPP_WEBHOOK_VERIFY_TOKEN'),
                "signature_secret": os.getenv('WHATSAPP_WEBHOOK_SECRET')
            }
        }
    
    async def setup_channel(self):
        """Configurar canal WhatsApp en Bird.com"""
        channel = await self.bird_client.channels.create(self.whatsapp_config)
        return channel
    
    async def setup_ai_employee(self):
        """Configurar AI Employee para WhatsApp"""
        ai_employee_config = {
            "name": "WhatsApp Assistant",
            "channels": ["whatsapp"],
            "capabilities": [
                "text_processing",
                "image_analysis",
                "audio_transcription",
                "document_parsing"
            ],
            "personality": {
                "tone": "professional_friendly",
                "language": "es",
                "response_style": "conversational"
            },
            "multimodal_settings": {
                "image_analysis": True,
                "audio_processing": True,
                "document_processing": True,
                "max_file_size": "100MB"
            }
        }
        
        ai_employee = await self.bird_client.ai_employees.create(ai_employee_config)
        return ai_employee
```

## Configuración de Webhooks

### 1. Endpoint de Verificación

```python
# webhook_verification.py
from flask import Flask, request, jsonify
import os
import hashlib
import hmac

app = Flask(__name__)

@app.route('/webhooks/whatsapp', methods=['GET'])
def verify_webhook():
    """Verificación inicial del webhook por Meta"""
    verify_token = request.args.get('hub.verify_token')
    challenge = request.args.get('hub.challenge')
    
    if verify_token == os.getenv('WHATSAPP_WEBHOOK_VERIFY_TOKEN'):
        return challenge
    else:
        return 'Error de verificación', 403

@app.route('/webhooks/whatsapp', methods=['POST'])
def receive_webhook():
    """Recibir eventos de WhatsApp"""
    # Verificar firma HMAC
    signature = request.headers.get('X-Hub-Signature-256')
    if not verify_signature(request.data, signature):
        return 'Firma inválida', 401
    
    # Procesar evento
    webhook_data = request.get_json()
    await process_whatsapp_event(webhook_data)
    
    return 'OK', 200

def verify_signature(payload, signature):
    """Verificar firma HMAC-SHA256"""
    if not signature:
        return False
    
    expected_signature = 'sha256=' + hmac.new(
        os.getenv('WHATSAPP_WEBHOOK_SECRET').encode(),
        payload,
        hashlib.sha256
    ).hexdigest()
    
    return hmac.compare_digest(signature, expected_signature)
```

### 2. Configuración de Webhook en Meta

```bash
# Configurar webhook usando Graph API
curl -X POST "https://graph.facebook.com/v18.0/YOUR_APP_ID/webhooks" \
  -H "Authorization: Bearer YOUR_ACCESS_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "object": "whatsapp_business_account",
    "callback_url": "https://your-domain.com/webhooks/whatsapp",
    "verify_token": "your_verify_token",
    "fields": [
      "messages",
      "message_deliveries", 
      "message_reads",
      "message_reactions",
      "messaging_handovers"
    ]
  }'
```

### 3. Configuración de Suscripciones

```python
# webhook_subscriptions.py
import aiohttp
import os

class WhatsAppWebhookManager:
    def __init__(self):
        self.access_token = os.getenv('WHATSAPP_ACCESS_TOKEN')
        self.business_account_id = os.getenv('WHATSAPP_BUSINESS_ACCOUNT_ID')
        
    async def subscribe_to_webhooks(self):
        """Suscribirse a eventos de webhook"""
        url = f"https://graph.facebook.com/v18.0/{self.business_account_id}/subscribed_apps"
        
        data = {
            'subscribed_fields': [
                'messages',           # Mensajes entrantes
                'message_deliveries', # Estados de entrega
                'message_reads',      # Confirmaciones de lectura
                'message_reactions',  # Reacciones a mensajes
                'messaging_handovers' # Transferencias a agentes
            ]
        }
        
        headers = {
            'Authorization': f'Bearer {self.access_token}',
            'Content-Type': 'application/json'
        }
        
        async with aiohttp.ClientSession() as session:
            async with session.post(url, json=data, headers=headers) as response:
                result = await response.json()
                return result
    
    async def configure_webhook_fields(self):
        """Configurar campos específicos del webhook"""
        webhook_config = {
            "messaging_product": "whatsapp",
            "webhook_url": f"{os.getenv('BASE_URL')}/webhooks/whatsapp",
            "webhook_fields": {
                "messages": {
                    "text": True,
                    "image": True,
                    "audio": True,
                    "video": True,
                    "document": True,
                    "location": True,
                    "contacts": True,
                    "interactive": True
                },
                "statuses": {
                    "sent": True,
                    "delivered": True,
                    "read": True,
                    "failed": True
                }
            }
        }
        
        return webhook_config
```

## Gestión de Tokens

### 1. Renovación Automática de Tokens

```python
# token_manager.py
import asyncio
import aiohttp
from datetime import datetime, timedelta
import logging

class WhatsAppTokenManager:
    def __init__(self, app_id, app_secret, long_lived_token):
        self.app_id = app_id
        self.app_secret = app_secret
        self.current_token = long_lived_token
        self.token_expires_at = None
        self.refresh_interval = timedelta(days=30)  # Renovar cada 30 días
        
    async def get_long_lived_token(self, short_lived_token):
        """Convertir token temporal a permanente"""
        url = "https://graph.facebook.com/v18.0/oauth/access_token"
        
        params = {
            'grant_type': 'fb_exchange_token',
            'client_id': self.app_id,
            'client_secret': self.app_secret,
            'fb_exchange_token': short_lived_token
        }
        
        async with aiohttp.ClientSession() as session:
            async with session.get(url, params=params) as response:
                data = await response.json()
                
                if 'access_token' in data:
                    self.current_token = data['access_token']
                    self.token_expires_at = datetime.now() + timedelta(seconds=data.get('expires_in', 5184000))
                    logging.info(f"Token renovado exitosamente. Expira: {self.token_expires_at}")
                    return data
                else:
                    logging.error(f"Error renovando token: {data}")
                    return None
    
    async def validate_token(self):
        """Validar token actual"""
        url = f"https://graph.facebook.com/v18.0/me"
        headers = {'Authorization': f'Bearer {self.current_token}'}
        
        async with aiohttp.ClientSession() as session:
            async with session.get(url, headers=headers) as response:
                if response.status == 200:
                    return True
                else:
                    logging.warning(f"Token inválido: {response.status}")
                    return False
    
    async def start_token_refresh_scheduler(self):
        """Programar renovación automática de tokens"""
        while True:
            try:
                if self.token_expires_at:
                    time_until_expiry = self.token_expires_at - datetime.now()
                    if time_until_expiry < timedelta(days=7):  # Renovar 7 días antes
                        await self.refresh_token()
                
                # Verificar cada 24 horas
                await asyncio.sleep(86400)
                
            except Exception as e:
                logging.error(f"Error en scheduler de tokens: {e}")
                await asyncio.sleep(3600)  # Retry en 1 hora
```

### 2. Sistema de Fallback y Recovery

```python
# auth_recovery.py
class AuthRecoverySystem:
    def __init__(self):
        self.backup_tokens = []
        self.auth_status = "healthy"
        
    async def add_backup_token(self, token, priority=1):
        """Agregar token de respaldo"""
        self.backup_tokens.append({
            "token": token,
            "priority": priority,
            "added_at": datetime.now(),
            "validated": False
        })
        
        # Validar token
        if await self.validate_backup_token(token):
            self.backup_tokens[-1]["validated"] = True
    
    async def attempt_auth_recovery(self):
        """Intentar recuperación automática de autenticación"""
        logging.warning("Iniciando recuperación de autenticación...")
        
        # Ordenar tokens por prioridad
        sorted_tokens = sorted(
            [t for t in self.backup_tokens if t["validated"]], 
            key=lambda x: x["priority"]
        )
        
        for token_info in sorted_tokens:
            try:
                if await self.validate_backup_token(token_info["token"]):
                    self.current_token = token_info["token"]
                    self.auth_status = "recovered"
                    logging.info("Recuperación de autenticación exitosa")
                    return True
            except Exception as e:
                logging.error(f"Fallo en token de respaldo: {e}")
                continue
        
        self.auth_status = "failed"
        await self.trigger_emergency_notification()
        return False
    
    async def trigger_emergency_notification(self):
        """Notificación de emergencia por falla de autenticación"""
        notification = {
            "type": "auth_failure",
            "severity": "critical",
            "timestamp": datetime.now().isoformat(),
            "message": "Falla crítica en autenticación de WhatsApp Business API",
            "required_action": "Renovación manual de tokens requerida"
        }
        
        # Enviar notificación a sistemas de monitoreo
        await self.send_emergency_notification(notification)
```

## Rate Limiting y Cuotas

### 1. Límites de API

```yaml
Rate Limits:
  Messages API:
    - 1000 requests/minute por número de teléfono
    - 20,000 requests/day (tier básico)
    - 100,000 requests/day (tier premium)
  
  Media API:
    - 100 uploads/minute
    - 10GB/day de transferencia
    - Archivos hasta 100MB
  
  Webhooks:
    - Sin límite de eventos entrantes
    - Timeout de 20 segundos por request
    - 3 reintentos automáticos
```

### 2. Gestión de Rate Limiting

```python
# rate_limiter.py
import asyncio
from collections import defaultdict
from datetime import datetime, timedelta
import logging

class WhatsAppRateLimiter:
    def __init__(self):
        self.request_counts = defaultdict(list)
        self.rate_limits = {
            'messages': {'requests': 1000, 'window': 60},  # 1000 req/min
            'media': {'requests': 100, 'window': 60},       # 100 req/min
            'general': {'requests': 200, 'window': 60}      # 200 req/min default
        }
        
    async def check_rate_limit(self, endpoint_type='general', phone_number=None):
        """Verificar si se puede hacer la petición"""
        key = f"{endpoint_type}_{phone_number or 'global'}"
        now = datetime.now()
        
        # Limpiar requests antiguos
        cutoff_time = now - timedelta(seconds=self.rate_limits[endpoint_type]['window'])
        self.request_counts[key] = [
            req_time for req_time in self.request_counts[key] 
            if req_time > cutoff_time
        ]
        
        # Verificar límite
        current_requests = len(self.request_counts[key])
        limit = self.rate_limits[endpoint_type]['requests']
        
        if current_requests >= limit:
            wait_time = (self.request_counts[key][0] + timedelta(seconds=self.rate_limits[endpoint_type]['window']) - now).total_seconds()
            logging.warning(f"Rate limit alcanzado para {key}. Esperar {wait_time} segundos")
            return False, wait_time
        
        # Registrar petición
        self.request_counts[key].append(now)
        return True, 0
    
    async def wait_for_rate_limit(self, endpoint_type='general', phone_number=None):
        """Esperar hasta que se pueda hacer la petición"""
        can_proceed, wait_time = await self.check_rate_limit(endpoint_type, phone_number)
        
        if not can_proceed:
            await asyncio.sleep(wait_time + 1)  # +1 segundo de buffer
            return await self.check_rate_limit(endpoint_type, phone_number)
        
        return True, 0

# Decorador para aplicar rate limiting
def rate_limited(endpoint_type='general'):
    def decorator(func):
        async def wrapper(*args, **kwargs):
            limiter = WhatsAppRateLimiter()
            phone_number = kwargs.get('to') or kwargs.get('phone_number')
            
            can_proceed, wait_time = await limiter.wait_for_rate_limit(endpoint_type, phone_number)
            
            if can_proceed:
                return await func(*args, **kwargs)
            else:
                raise Exception(f"Rate limit excedido para {endpoint_type}")
        
        return wrapper
    return decorator
```

## Configuración de Producción

### 1. Configuración de Infraestructura

```yaml
# docker-compose.yml para producción
version: '3.8'
services:
  whatsapp-webhook:
    image: robertai/whatsapp-webhook:latest
    environment:
      - WHATSAPP_ACCESS_TOKEN=${WHATSAPP_ACCESS_TOKEN}
      - WHATSAPP_WEBHOOK_SECRET=${WHATSAPP_WEBHOOK_SECRET}
      - BIRD_API_KEY=${BIRD_API_KEY}
      - REDIS_URL=${REDIS_URL}
    ports:
      - "443:8443"
    volumes:
      - ./ssl:/app/ssl
    restart: always
    
  redis:
    image: redis:alpine
    ports:
      - "6379:6379"
    restart: always
    
  nginx:
    image: nginx:alpine
    ports:
      - "80:80"
      - "443:443"
    volumes:
      - ./nginx.conf:/etc/nginx/nginx.conf
      - ./ssl:/etc/ssl
    restart: always
```

### 2. Configuración SSL/TLS

```nginx
# nginx.conf
server {
    listen 443 ssl http2;
    server_name your-domain.com;
    
    ssl_certificate /etc/ssl/cert.pem;
    ssl_certificate_key /etc/ssl/key.pem;
    ssl_protocols TLSv1.2 TLSv1.3;
    ssl_ciphers HIGH:!aNULL:!MD5;
    
    location /webhooks/whatsapp {
        proxy_pass http://whatsapp-webhook:8443;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
        
        # Timeouts para webhooks
        proxy_connect_timeout 30s;
        proxy_send_timeout 30s;
        proxy_read_timeout 30s;
    }
}
```

## Monitoreo y Logs

### 1. Sistema de Monitoreo

```python
# monitoring.py
import logging
import asyncio
from datetime import datetime
import aiohttp

class WhatsAppAuthMonitor:
    def __init__(self):
        self.last_health_check = None
        self.consecutive_failures = 0
        self.alert_threshold = 3
        
    async def health_check(self):
        """Verificación de salud del sistema de autenticación"""
        try:
            # Verificar token
            token_valid = await self.validate_current_token()
            
            # Verificar webhook
            webhook_responding = await self.test_webhook_connectivity()
            
            # Verificar Bird.com integration
            bird_healthy = await self.check_bird_integration()
            
            health_status = {
                "timestamp": datetime.now().isoformat(),
                "token_valid": token_valid,
                "webhook_responding": webhook_responding,
                "bird_integration": bird_healthy,
                "overall_health": all([token_valid, webhook_responding, bird_healthy])
            }
            
            if health_status["overall_health"]:
                self.consecutive_failures = 0
            else:
                self.consecutive_failures += 1
                
            await self.log_health_status(health_status)
            
            if self.consecutive_failures >= self.alert_threshold:
                await self.trigger_health_alert(health_status)
            
            return health_status
            
        except Exception as e:
            logging.error(f"Error en health check: {e}")
            self.consecutive_failures += 1
            return {"overall_health": False, "error": str(e)}
    
    async def start_health_monitoring(self):
        """Iniciar monitoreo continuo"""
        while True:
            await self.health_check()
            await asyncio.sleep(300)  # Verificar cada 5 minutos
```

## Próximos Pasos

1. **Configurar tipos de mensaje**: Continuar con [Tipos de Mensajes](03-message-types.md)
2. **Implementar webhooks**: Seguir [Eventos de Webhook](04-webhook-events.md)  
3. **Integrar multimedia**: Configurar [Manejo de Contenido Multimedia](05-multimedia-handling.md)
4. **Conectar con Bird.com**: Implementar [Integración con Bird.com](06-bird-integration.md)

---

**Nota de Seguridad**: Mantener todos los tokens y secretos en variables de entorno seguras. Nunca commitear credenciales en el código fuente.