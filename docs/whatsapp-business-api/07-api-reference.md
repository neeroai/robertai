# Referencia de API - WhatsApp Business API

## Introducción

Referencia completa de la API de WhatsApp Business para integración con Bird.com AI Employees. Incluye todos los endpoints, parámetros, esquemas de respuesta y ejemplos de código.

## Base URL y Autenticación

```yaml
Base URL: https://graph.facebook.com/v18.0
Autenticación: Bearer Token
Formato: JSON
HTTPS: Obligatorio
```

### Headers Requeridos

```http
Authorization: Bearer YOUR_ACCESS_TOKEN
Content-Type: application/json
User-Agent: RobertAI-WhatsApp/1.0
```

## Endpoints Principales

### 1. Envío de Mensajes

#### `POST /{phone-number-id}/messages`

Enviar mensajes a través de WhatsApp Business API.

**Parámetros de Ruta:**
- `phone-number-id` (string, requerido): ID del número de teléfono de WhatsApp Business

**Body del Request:**

```json
{
  "messaging_product": "whatsapp",
  "recipient_type": "individual",
  "to": "573001234567",
  "type": "text|image|video|audio|document|interactive|template|location|contacts",
  "text": {
    "preview_url": true,
    "body": "Mensaje de texto"
  }
}
```

**Ejemplo completo - Mensaje de texto:**

```python
import aiohttp
import asyncio

async def send_text_message():
    url = "https://graph.facebook.com/v18.0/102290129340398/messages"
    
    headers = {
        "Authorization": "Bearer YOUR_ACCESS_TOKEN",
        "Content-Type": "application/json"
    }
    
    payload = {
        "messaging_product": "whatsapp",
        "recipient_type": "individual",
        "to": "573001234567",
        "type": "text",
        "text": {
            "preview_url": True,
            "body": "¡Hola! Soy tu asistente de RobertAI 🤖"
        }
    }
    
    async with aiohttp.ClientSession() as session:
        async with session.post(url, json=payload, headers=headers) as response:
            return await response.json()

# Ejecutar
result = asyncio.run(send_text_message())
print(result)
```

**Respuesta Exitosa (200):**

```json
{
  "messaging_product": "whatsapp",
  "contacts": [
    {
      "input": "573001234567",
      "wa_id": "573001234567"
    }
  ],
  "messages": [
    {
      "id": "wamid.HBgLNTczMDA5NzI4...",
      "message_status": "accepted"
    }
  ]
}
```

#### Tipos de Mensaje Soportados

##### 1. Mensaje de Texto con Formato

```python
async def send_formatted_text():
    payload = {
        "messaging_product": "whatsapp",
        "recipient_type": "individual",
        "to": "573001234567",
        "type": "text",
        "text": {
            "preview_url": True,
            "body": "¡Bienvenido a *RobertAI*! 🚀\n\n"
                   "Nuestros servicios:\n"
                   "• _Consultoría en IA_\n"
                   "• _Desarrollo personalizado_\n"
                   "• _Integración de sistemas_\n\n"
                   "Visita: https://robertai.com"
        }
    }
    return await send_whatsapp_message(payload)
```

##### 2. Mensaje con Imagen

```python
async def send_image_message():
    payload = {
        "messaging_product": "whatsapp",
        "recipient_type": "individual",
        "to": "573001234567",
        "type": "image",
        "image": {
            "link": "https://robertai.com/assets/demo-analysis.jpg",
            "caption": "Análisis visual completado por RobertAI 🔍"
        }
    }
    return await send_whatsapp_message(payload)
```

##### 3. Botones Interactivos

```python
async def send_interactive_buttons():
    payload = {
        "messaging_product": "whatsapp",
        "recipient_type": "individual",
        "to": "573001234567",
        "type": "interactive",
        "interactive": {
            "type": "button",
            "body": {
                "text": "¿En qué puedo ayudarte hoy?"
            },
            "footer": {
                "text": "Powered by RobertAI"
            },
            "action": {
                "buttons": [
                    {
                        "type": "reply",
                        "reply": {
                            "id": "info_servicios",
                            "title": "🔍 Ver Servicios"
                        }
                    },
                    {
                        "type": "reply",
                        "reply": {
                            "id": "solicitar_demo",
                            "title": "🚀 Solicitar Demo"
                        }
                    },
                    {
                        "type": "reply",
                        "reply": {
                            "id": "hablar_agente",
                            "title": "👨‍💻 Hablar con Agente"
                        }
                    }
                ]
            }
        }
    }
    return await send_whatsapp_message(payload)
```

##### 4. Lista Interactiva

```python
async def send_interactive_list():
    payload = {
        "messaging_product": "whatsapp",
        "recipient_type": "individual",
        "to": "573001234567",
        "type": "interactive",
        "interactive": {
            "type": "list",
            "header": {
                "type": "text",
                "text": "🤖 RobertAI - Servicios Disponibles"
            },
            "body": {
                "text": "Selecciona el servicio que te interesa:"
            },
            "footer": {
                "text": "Powered by RobertAI"
            },
            "action": {
                "button": "Ver Servicios",
                "sections": [
                    {
                        "title": "🚀 Servicios Principales",
                        "rows": [
                            {
                                "id": "consultoria_ai",
                                "title": "Consultoría en IA",
                                "description": "Estrategia e implementación de IA"
                            },
                            {
                                "id": "desarrollo_custom",
                                "title": "Desarrollo Personalizado",
                                "description": "Soluciones de software a medida"
                            }
                        ]
                    },
                    {
                        "title": "🛠️ Soporte y Mantenimiento",
                        "rows": [
                            {
                                "id": "soporte_tecnico",
                                "title": "Soporte Técnico",
                                "description": "Asistencia especializada 24/7"
                            }
                        ]
                    }
                ]
            }
        }
    }
    return await send_whatsapp_message(payload)
```

##### 5. Plantilla de Mensaje

```python
async def send_template_message():
    payload = {
        "messaging_product": "whatsapp",
        "recipient_type": "individual",
        "to": "573001234567",
        "type": "template",
        "template": {
            "name": "bienvenida_robertai",
            "language": {
                "code": "es"
            },
            "components": [
                {
                    "type": "header",
                    "parameters": [
                        {
                            "type": "text",
                            "text": "Juan Pérez"
                        }
                    ]
                },
                {
                    "type": "body",
                    "parameters": [
                        {
                            "type": "text",
                            "text": "RobertAI"
                        },
                        {
                            "type": "text",
                            "text": "15 de Enero, 2025"
                        }
                    ]
                }
            ]
        }
    }
    return await send_whatsapp_message(payload)
```

### 2. Gestión de Archivos Multimedia

#### `POST /{phone-number-id}/media`

Subir archivos multimedia para usar en mensajes.

**Parámetros de Ruta:**
- `phone-number-id` (string, requerido): ID del número de teléfono

**Body del Request (multipart/form-data):**
- `file` (binary, requerido): Archivo a subir
- `type` (string, requerido): Tipo de archivo (`image`, `video`, `audio`, `document`)

**Ejemplo de subida:**

```python
import aiofiles

async def upload_media_file(file_path: str, media_type: str):
    url = f"https://graph.facebook.com/v18.0/{PHONE_NUMBER_ID}/media"
    
    headers = {
        "Authorization": f"Bearer {ACCESS_TOKEN}"
    }
    
    # Preparar FormData
    data = aiohttp.FormData()
    data.add_field('type', media_type)
    
    async with aiofiles.open(file_path, 'rb') as file:
        file_content = await file.read()
        filename = os.path.basename(file_path)
        
        data.add_field(
            'file', 
            file_content, 
            filename=filename,
            content_type=f"{media_type}/*"
        )
    
    async with aiohttp.ClientSession() as session:
        async with session.post(url, headers=headers, data=data) as response:
            result = await response.json()
            if response.status == 200:
                return result['id']  # Media ID
            else:
                raise Exception(f"Error subiendo archivo: {result}")

# Usar el media_id en un mensaje
media_id = await upload_media_file("demo-image.jpg", "image")

payload = {
    "messaging_product": "whatsapp",
    "recipient_type": "individual",
    "to": "573001234567",
    "type": "image",
    "image": {
        "id": media_id,
        "caption": "Imagen subida desde RobertAI"
    }
}
```

**Respuesta Exitosa:**

```json
{
  "id": "1234567890123456"
}
```

#### `GET /{media-id}`

Obtener información sobre un archivo multimedia.

**Parámetros de Ruta:**
- `media-id` (string, requerido): ID del archivo multimedia

**Ejemplo:**

```python
async def get_media_info(media_id: str):
    url = f"https://graph.facebook.com/v18.0/{media_id}"
    
    headers = {
        "Authorization": f"Bearer {ACCESS_TOKEN}"
    }
    
    async with aiohttp.ClientSession() as session:
        async with session.get(url, headers=headers) as response:
            return await response.json()

# Obtener información
media_info = await get_media_info("1234567890123456")
print(f"URL de descarga: {media_info['url']}")
print(f"Tipo MIME: {media_info['mime_type']}")
print(f"Tamaño: {media_info['file_size']} bytes")
```

**Respuesta:**

```json
{
  "url": "https://lookaside.fbsbx.com/whatsapp_business/attachments/...",
  "mime_type": "image/jpeg",
  "sha256": "abc123...",
  "file_size": 123456,
  "id": "1234567890123456",
  "messaging_product": "whatsapp"
}
```

### 3. Configuración de Webhooks

#### `GET /webhooks/whatsapp`

Endpoint de verificación del webhook.

**Parámetros de Query:**
- `hub.mode` (string): Debe ser "subscribe"
- `hub.verify_token` (string): Token de verificación configurado
- `hub.challenge` (string): Challenge enviado por Meta

**Implementación:**

```python
from fastapi import FastAPI, Request, HTTPException
from fastapi.responses import PlainTextResponse

app = FastAPI()

@app.get("/webhooks/whatsapp")
async def verify_webhook(
    request: Request,
    hub_mode: str = None,
    hub_verify_token: str = None, 
    hub_challenge: str = None
):
    """Verificación del webhook por Meta"""
    
    if (
        hub_mode == "subscribe" and 
        hub_verify_token == os.getenv('WHATSAPP_WEBHOOK_VERIFY_TOKEN')
    ):
        logging.info("Webhook verificado exitosamente")
        return PlainTextResponse(content=hub_challenge)
    else:
        logging.warning("Fallo en verificación de webhook")
        raise HTTPException(status_code=403, detail="Token inválido")
```

#### `POST /webhooks/whatsapp`

Recibir eventos del webhook.

**Body del Request:**

```json
{
  "object": "whatsapp_business_account",
  "entry": [
    {
      "id": "WHATSAPP_BUSINESS_ACCOUNT_ID",
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
                "id": "wamid.ABCDEfghijk",
                "timestamp": "1234567890",
                "text": {
                  "body": "Hola, necesito ayuda"
                },
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
```

**Implementación:**

```python
import hmac
import hashlib
import json

@app.post("/webhooks/whatsapp")
async def receive_webhook(
    request: Request,
    background_tasks: BackgroundTasks
):
    """Recibir y procesar eventos de WhatsApp"""
    
    # Verificar firma HMAC
    signature = request.headers.get('X-Hub-Signature-256')
    body = await request.body()
    
    if not verify_webhook_signature(body, signature):
        raise HTTPException(status_code=401, detail="Firma inválida")
    
    # Parsear datos
    try:
        webhook_data = json.loads(body)
    except json.JSONDecodeError:
        raise HTTPException(status_code=400, detail="JSON inválido")
    
    # Procesar en background
    background_tasks.add_task(process_webhook_data, webhook_data)
    
    return PlainTextResponse(content="OK")

def verify_webhook_signature(payload: bytes, signature: str) -> bool:
    """Verificar firma HMAC-SHA256"""
    if not signature or not signature.startswith('sha256='):
        return False
    
    expected_signature = 'sha256=' + hmac.new(
        os.getenv('WHATSAPP_WEBHOOK_SECRET').encode(),
        payload,
        hashlib.sha256
    ).hexdigest()
    
    return hmac.compare_digest(signature, expected_signature)

async def process_webhook_data(webhook_data: dict):
    """Procesar datos del webhook"""
    try:
        for entry in webhook_data.get('entry', []):
            for change in entry.get('changes', []):
                if change.get('field') == 'messages':
                    value = change.get('value', {})
                    
                    # Procesar mensajes entrantes
                    for message in value.get('messages', []):
                        await handle_incoming_message(message, value.get('metadata', {}))
                    
                    # Procesar estados de mensaje
                    for status in value.get('statuses', []):
                        await handle_message_status(status)
    
    except Exception as e:
        logging.error(f"Error procesando webhook: {e}")
```

## Códigos de Error

### Errores Comunes de la API

| Código | Descripción | Solución |
|---------|-------------|----------|
| 400 | Solicitud mal formada | Verificar formato JSON y parámetros |
| 401 | Token de acceso inválido | Renovar access token |
| 403 | Acceso denegado | Verificar permisos de la aplicación |
| 429 | Rate limit excedido | Implementar backoff exponencial |
| 500 | Error interno del servidor | Reintentar después de un delay |

### Errores Específicos de WhatsApp

```json
{
  "error": {
    "message": "Invalid parameter",
    "type": "OAuthException", 
    "code": 100,
    "error_subcode": 2388028,
    "error_user_title": "Número de teléfono no válido",
    "error_user_msg": "El número de teléfono debe estar en formato internacional",
    "fbtrace_id": "ABC123def456"
  }
}
```

### Manejo de Errores

```python
class WhatsAppAPIError(Exception):
    def __init__(self, error_data: dict):
        self.code = error_data.get('code')
        self.subcode = error_data.get('error_subcode')
        self.message = error_data.get('message')
        self.user_message = error_data.get('error_user_msg')
        self.trace_id = error_data.get('fbtrace_id')
        
        super().__init__(self.message)

async def send_whatsapp_message_with_error_handling(payload: dict):
    """Enviar mensaje con manejo completo de errores"""
    
    max_retries = 3
    base_delay = 1.0
    
    for attempt in range(max_retries):
        try:
            async with aiohttp.ClientSession() as session:
                async with session.post(url, json=payload, headers=headers) as response:
                    result = await response.json()
                    
                    if response.status == 200:
                        return result
                    
                    # Manejar errores específicos
                    error_data = result.get('error', {})
                    error_code = error_data.get('code')
                    error_subcode = error_data.get('error_subcode')
                    
                    if response.status == 429:  # Rate limit
                        retry_after = int(response.headers.get('Retry-After', 60))
                        await asyncio.sleep(retry_after)
                        continue
                    
                    elif error_code == 131026:  # Rate limit error
                        delay = base_delay * (2 ** attempt)
                        await asyncio.sleep(delay)
                        continue
                    
                    elif error_subcode == 131047:  # Re-engagement window
                        # Usuario fuera de ventana de 24 horas
                        raise WhatsAppAPIError({
                            **error_data,
                            'requires_template': True
                        })
                    
                    else:
                        # Error no recuperable
                        raise WhatsAppAPIError(error_data)
        
        except aiohttp.ClientError as e:
            if attempt == max_retries - 1:
                raise
            
            delay = base_delay * (2 ** attempt)
            await asyncio.sleep(delay)
    
    raise Exception("Máximo de reintentos alcanzado")
```

## Rate Limiting y Mejores Prácticas

### Límites de API

```python
class RateLimiter:
    def __init__(self):
        self.limits = {
            'messages': 1000,  # por minuto
            'media': 100,      # por minuto
            'general': 200     # por minuto
        }
        self.requests = defaultdict(list)
    
    async def check_rate_limit(self, endpoint_type: str = 'general'):
        """Verificar rate limit antes de hacer request"""
        now = time.time()
        minute_ago = now - 60
        
        # Limpiar requests antiguos
        self.requests[endpoint_type] = [
            req_time for req_time in self.requests[endpoint_type]
            if req_time > minute_ago
        ]
        
        # Verificar límite
        if len(self.requests[endpoint_type]) >= self.limits[endpoint_type]:
            sleep_time = self.requests[endpoint_type][0] + 60 - now
            await asyncio.sleep(sleep_time)
        
        # Registrar request
        self.requests[endpoint_type].append(now)

# Uso del rate limiter
rate_limiter = RateLimiter()

async def send_message_with_rate_limit(payload: dict):
    await rate_limiter.check_rate_limit('messages')
    return await send_whatsapp_message(payload)
```

### Mejores Prácticas para Desarrollo

1. **Siempre validar números de teléfono:**

```python
import re

def validate_whatsapp_number(phone_number: str) -> bool:
    """Validar formato de número WhatsApp"""
    # Formato: código país + número (sin +)
    pattern = r'^[1-9]\d{7,14}$'
    return bool(re.match(pattern, phone_number.replace('+', '')))
```

2. **Implementar retry con backoff exponencial:**

```python
async def exponential_backoff_retry(func, max_retries=3):
    for attempt in range(max_retries):
        try:
            return await func()
        except Exception as e:
            if attempt == max_retries - 1:
                raise
            
            delay = 2 ** attempt + random.uniform(0, 1)
            await asyncio.sleep(delay)
```

3. **Logging detallado:**

```python
import structlog

logger = structlog.get_logger()

async def send_message_with_logging(payload: dict):
    logger.info(
        "Enviando mensaje WhatsApp",
        to=payload['to'],
        type=payload['type'],
        message_length=len(payload.get('text', {}).get('body', ''))
    )
    
    try:
        result = await send_whatsapp_message(payload)
        
        logger.info(
            "Mensaje enviado exitosamente",
            message_id=result['messages'][0]['id'],
            status=result['messages'][0]['message_status']
        )
        
        return result
    
    except Exception as e:
        logger.error(
            "Error enviando mensaje",
            error=str(e),
            payload=payload
        )
        raise
```

## SDK y Bibliotecas

### Cliente Python Personalizado

```python
# whatsapp_business_client.py
import aiohttp
import asyncio
from typing import Dict, List, Optional
import logging
from datetime import datetime

class WhatsAppBusinessClient:
    """Cliente completo para WhatsApp Business API"""
    
    def __init__(self, access_token: str, phone_number_id: str, 
                 api_version: str = "v18.0"):
        self.access_token = access_token
        self.phone_number_id = phone_number_id
        self.base_url = f"https://graph.facebook.com/{api_version}"
        self.session = None
        self.rate_limiter = RateLimiter()
    
    async def __aenter__(self):
        self.session = aiohttp.ClientSession(
            timeout=aiohttp.ClientTimeout(total=30),
            headers={
                "Authorization": f"Bearer {self.access_token}",
                "User-Agent": "RobertAI-WhatsApp/1.0"
            }
        )
        return self
    
    async def __aexit__(self, exc_type, exc_val, exc_tb):
        if self.session:
            await self.session.close()
    
    async def send_text(self, to: str, text: str, 
                       preview_url: bool = True) -> Dict:
        """Enviar mensaje de texto"""
        return await self.send_message({
            "to": to,
            "type": "text",
            "text": {
                "preview_url": preview_url,
                "body": text
            }
        })
    
    async def send_image(self, to: str, image_data: Dict, 
                        caption: Optional[str] = None) -> Dict:
        """Enviar imagen"""
        payload = {
            "to": to,
            "type": "image",
            "image": image_data
        }
        
        if caption:
            payload["image"]["caption"] = caption
        
        return await self.send_message(payload)
    
    async def send_buttons(self, to: str, text: str, 
                          buttons: List[Dict]) -> Dict:
        """Enviar botones interactivos"""
        if len(buttons) > 3:
            raise ValueError("Máximo 3 botones permitidos")
        
        return await self.send_message({
            "to": to,
            "type": "interactive",
            "interactive": {
                "type": "button",
                "body": {"text": text},
                "action": {
                    "buttons": [
                        {
                            "type": "reply",
                            "reply": {
                                "id": btn["id"],
                                "title": btn["title"][:20]
                            }
                        }
                        for btn in buttons
                    ]
                }
            }
        })
    
    async def send_message(self, message_data: Dict) -> Dict:
        """Método base para envío de mensajes"""
        await self.rate_limiter.check_rate_limit('messages')
        
        payload = {
            "messaging_product": "whatsapp",
            "recipient_type": "individual",
            **message_data
        }
        
        url = f"{self.base_url}/{self.phone_number_id}/messages"
        
        async with self.session.post(url, json=payload) as response:
            result = await response.json()
            
            if response.status == 200:
                logging.info(f"Mensaje enviado: {result['messages'][0]['id']}")
                return result
            else:
                raise WhatsAppAPIError(result.get('error', {}))
    
    async def upload_media(self, file_path: str, media_type: str) -> str:
        """Subir archivo multimedia"""
        await self.rate_limiter.check_rate_limit('media')
        
        url = f"{self.base_url}/{self.phone_number_id}/media"
        
        data = aiohttp.FormData()
        data.add_field('type', media_type)
        
        with open(file_path, 'rb') as file:
            data.add_field(
                'file', 
                file, 
                filename=os.path.basename(file_path)
            )
        
        # Usar sesión sin Content-Type header para FormData
        headers = {"Authorization": f"Bearer {self.access_token}"}
        
        async with aiohttp.ClientSession() as session:
            async with session.post(url, data=data, headers=headers) as response:
                result = await response.json()
                
                if response.status == 200:
                    return result['id']
                else:
                    raise WhatsAppAPIError(result.get('error', {}))

# Uso del cliente
async def example_usage():
    async with WhatsAppBusinessClient(ACCESS_TOKEN, PHONE_NUMBER_ID) as client:
        # Enviar texto
        await client.send_text(
            "573001234567", 
            "¡Hola desde RobertAI! 🤖"
        )
        
        # Enviar botones
        await client.send_buttons(
            "573001234567",
            "¿En qué puedo ayudarte?",
            [
                {"id": "help", "title": "🆘 Ayuda"},
                {"id": "info", "title": "ℹ️ Info"},
                {"id": "contact", "title": "📞 Contacto"}
            ]
        )
        
        # Subir y enviar imagen
        media_id = await client.upload_media("demo.jpg", "image")
        await client.send_image(
            "573001234567",
            {"id": media_id},
            "Imagen subida desde RobertAI"
        )
```

## Próximos Pasos

1. **Aplicar mejores prácticas**: Continuar con [Mejores Prácticas](08-best-practices.md)
2. **Configurar troubleshooting**: Implementar [Guía de Resolución de Problemas](10-troubleshooting.md)
3. **Revisar especificación OpenAPI**: Ver [Especificación OpenAPI](09-openapi-spec.yaml)

---

**Nota**: Esta referencia incluye ejemplos completos y manejo de errores optimizado para uso en producción con Bird.com AI Employees.