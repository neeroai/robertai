# Tipos de Mensajes - WhatsApp Business API

## Introducción

WhatsApp Business API soporta múltiples tipos de mensajes que permiten crear experiencias conversacionales ricas e interactivas. Esta guía cubre todos los tipos de mensaje disponibles con ejemplos de implementación para Bird.com AI Employees.

## 1. Mensajes de Texto

### Mensaje Simple

```python
# text_message.py
async def send_text_message(phone_number: str, message: str):
    """Enviar mensaje de texto simple"""
    url = f"https://graph.facebook.com/v18.0/{PHONE_NUMBER_ID}/messages"
    
    payload = {
        "messaging_product": "whatsapp",
        "recipient_type": "individual",
        "to": phone_number,
        "type": "text",
        "text": {
            "preview_url": True,  # Habilitar preview de URLs
            "body": message
        }
    }
    
    headers = {
        "Authorization": f"Bearer {ACCESS_TOKEN}",
        "Content-Type": "application/json"
    }
    
    async with aiohttp.ClientSession() as session:
        async with session.post(url, json=payload, headers=headers) as response:
            result = await response.json()
            return result

# Ejemplo de uso
await send_text_message(
    phone_number="573001234567",
    message="¡Hola! Soy tu asistente de RobertAI. ¿En qué puedo ayudarte hoy? 🤖"
)
```

### Mensaje con Formato

```python
# formatted_text_message.py
async def send_formatted_text(phone_number: str, message: str):
    """Enviar texto con formato (markdown limitado)"""
    # WhatsApp soporta formato limitado:
    # *texto* = negrita
    # _texto_ = cursiva
    # ~texto~ = tachado
    # ```código``` = monospace
    
    formatted_message = """
¡Bienvenido a *RobertAI*! 🚀

Nuestros servicios incluyen:
• _Consultoría en IA_
• _Desarrollo personalizado_
• _Integración de sistemas_

Para más información, visita:
https://robertai.com

¿Tienes alguna pregunta específica?
    """.strip()
    
    return await send_text_message(phone_number, formatted_message)
```

## 2. Mensajes Multimedia

### Imágenes

```python
# image_message.py
async def send_image_message(phone_number: str, image_data: dict):
    """
    Enviar mensaje con imagen
    
    image_data puede ser:
    - {"id": "media_id"} para media ya subido
    - {"link": "https://..."} para URL externa
    - {"media_file": file_path} para subir archivo
    """
    
    url = f"https://graph.facebook.com/v18.0/{PHONE_NUMBER_ID}/messages"
    
    payload = {
        "messaging_product": "whatsapp",
        "recipient_type": "individual", 
        "to": phone_number,
        "type": "image",
        "image": {
            **image_data,
            "caption": "Análisis visual completado por RobertAI 🔍"
        }
    }
    
    headers = {
        "Authorization": f"Bearer {ACCESS_TOKEN}",
        "Content-Type": "application/json"
    }
    
    async with aiohttp.ClientSession() as session:
        async with session.post(url, json=payload, headers=headers) as response:
            return await response.json()

# Ejemplo con URL externa
await send_image_message(
    phone_number="573001234567",
    image_data={"link": "https://robertai.com/assets/demo-analysis.jpg"}
)

# Ejemplo con archivo local (requiere subida previa)
media_id = await upload_media_file("path/to/image.jpg", "image")
await send_image_message(
    phone_number="573001234567", 
    image_data={"id": media_id}
)
```

### Videos

```python
# video_message.py
async def send_video_message(phone_number: str, video_data: dict, caption: str = None):
    """Enviar mensaje con video (hasta 16MB)"""
    
    payload = {
        "messaging_product": "whatsapp",
        "recipient_type": "individual",
        "to": phone_number, 
        "type": "video",
        "video": {
            **video_data,
            "caption": caption or "Video procesado por RobertAI 🎥"
        }
    }
    
    return await send_whatsapp_message(payload)

# Ejemplo con video tutorial
await send_video_message(
    phone_number="573001234567",
    video_data={"link": "https://robertai.com/tutorials/getting-started.mp4"},
    caption="Tutorial: Primeros pasos con RobertAI 🎯"
)
```

### Audio

```python
# audio_message.py
async def send_audio_message(phone_number: str, audio_data: dict):
    """Enviar mensaje de audio (hasta 16MB)"""
    
    payload = {
        "messaging_product": "whatsapp",
        "recipient_type": "individual",
        "to": phone_number,
        "type": "audio", 
        "audio": audio_data
    }
    
    return await send_whatsapp_message(payload)

# Ejemplo con grabación de voz
await send_audio_message(
    phone_number="573001234567",
    audio_data={"id": await upload_media_file("response.mp3", "audio")}
)
```

### Documentos

```python
# document_message.py
async def send_document_message(phone_number: str, document_data: dict, filename: str):
    """Enviar documento (hasta 100MB)"""
    
    payload = {
        "messaging_product": "whatsapp", 
        "recipient_type": "individual",
        "to": phone_number,
        "type": "document",
        "document": {
            **document_data,
            "filename": filename,
            "caption": f"Documento generado por RobertAI: {filename} 📄"
        }
    }
    
    return await send_whatsapp_message(payload)

# Ejemplo con reporte PDF
await send_document_message(
    phone_number="573001234567",
    document_data={"link": "https://robertai.com/reports/analysis-report.pdf"},
    filename="Reporte_Analisis_AI.pdf"
)
```

## 3. Mensajes Interactivos

### Botones de Acción Rápida

```python
# interactive_buttons.py
async def send_button_message(phone_number: str, body_text: str, buttons: list):
    """
    Enviar mensaje con botones interactivos (máximo 3 botones)
    
    buttons: [{"id": "button_id", "title": "Button Text"}]
    """
    
    if len(buttons) > 3:
        raise ValueError("Máximo 3 botones permitidos")
    
    button_components = []
    for button in buttons:
        button_components.append({
            "type": "reply",
            "reply": {
                "id": button["id"],
                "title": button["title"][:20]  # Máximo 20 caracteres
            }
        })
    
    payload = {
        "messaging_product": "whatsapp",
        "recipient_type": "individual",
        "to": phone_number,
        "type": "interactive",
        "interactive": {
            "type": "button",
            "body": {
                "text": body_text
            },
            "action": {
                "buttons": button_components
            }
        }
    }
    
    return await send_whatsapp_message(payload)

# Ejemplo de menú principal
await send_button_message(
    phone_number="573001234567",
    body_text="¡Hola! Soy tu asistente de RobertAI 🤖\n\n¿En qué puedo ayudarte hoy?",
    buttons=[
        {"id": "info_servicios", "title": "🔍 Ver Servicios"},
        {"id": "solicitar_demo", "title": "🚀 Solicitar Demo"},
        {"id": "hablar_agente", "title": "👨‍💻 Hablar con Agente"}
    ]
)
```

### Listas Interactivas

```python
# interactive_lists.py
async def send_list_message(phone_number: str, body_text: str, button_text: str, sections: list):
    """
    Enviar lista interactiva (hasta 10 opciones por sección)
    
    sections: [
        {
            "title": "Section Title",
            "rows": [
                {"id": "row_id", "title": "Row Title", "description": "Row Description"}
            ]
        }
    ]
    """
    
    payload = {
        "messaging_product": "whatsapp",
        "recipient_type": "individual", 
        "to": phone_number,
        "type": "interactive",
        "interactive": {
            "type": "list",
            "header": {
                "type": "text",
                "text": "🤖 RobertAI - Servicios Disponibles"
            },
            "body": {
                "text": body_text
            },
            "footer": {
                "text": "Powered by RobertAI"
            },
            "action": {
                "button": button_text,
                "sections": sections
            }
        }
    }
    
    return await send_whatsapp_message(payload)

# Ejemplo de catálogo de servicios
await send_list_message(
    phone_number="573001234567",
    body_text="Selecciona el servicio que te interesa para obtener más información:",
    button_text="Ver Servicios",
    sections=[
        {
            "title": "🚀 Servicios Principales",
            "rows": [
                {
                    "id": "consultoria_ai",
                    "title": "Consultoría en IA",
                    "description": "Estrategia y implementación de IA para tu empresa"
                },
                {
                    "id": "desarrollo_custom", 
                    "title": "Desarrollo Personalizado",
                    "description": "Soluciones de software a medida con IA"
                },
                {
                    "id": "integracion_sistemas",
                    "title": "Integración de Sistemas", 
                    "description": "Conecta tus sistemas existentes con IA"
                }
            ]
        },
        {
            "title": "🛠️ Soporte y Mantenimiento",
            "rows": [
                {
                    "id": "soporte_tecnico",
                    "title": "Soporte Técnico",
                    "description": "Asistencia técnica especializada 24/7"
                },
                {
                    "id": "capacitacion",
                    "title": "Capacitación",
                    "description": "Training para tu equipo en tecnologías IA"
                }
            ]
        }
    ]
)
```

## 4. Plantillas de Mensaje

### Plantillas Pre-aprobadas

```python
# template_messages.py
async def send_template_message(phone_number: str, template_name: str, language_code: str, components: list = None):
    """
    Enviar plantilla pre-aprobada por Meta
    
    Las plantillas deben estar aprobadas previamente en Business Manager
    """
    
    payload = {
        "messaging_product": "whatsapp",
        "recipient_type": "individual",
        "to": phone_number,
        "type": "template",
        "template": {
            "name": template_name,
            "language": {
                "code": language_code
            }
        }
    }
    
    if components:
        payload["template"]["components"] = components
    
    return await send_whatsapp_message(payload)

# Ejemplo de plantilla de bienvenida
await send_template_message(
    phone_number="573001234567",
    template_name="bienvenida_robertai",
    language_code="es",
    components=[
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
)
```

## 5. Cliente Unificado de Mensajes

```python
# whatsapp_client.py
import aiohttp
import asyncio
from typing import Dict, List, Optional, Union
import logging

class WhatsAppBusinessClient:
    def __init__(self, access_token: str, phone_number_id: str):
        self.access_token = access_token
        self.phone_number_id = phone_number_id
        self.base_url = f"https://graph.facebook.com/v18.0/{phone_number_id}"
        self.rate_limiter = WhatsAppRateLimiter()
        
    async def send_message(self, payload: Dict) -> Dict:
        """Método base para envío de mensajes"""
        await self.rate_limiter.wait_for_rate_limit('messages', payload.get('to'))
        
        url = f"{self.base_url}/messages"
        headers = {
            "Authorization": f"Bearer {self.access_token}",
            "Content-Type": "application/json"
        }
        
        try:
            async with aiohttp.ClientSession() as session:
                async with session.post(url, json=payload, headers=headers) as response:
                    result = await response.json()
                    
                    if response.status == 200:
                        logging.info(f"Mensaje enviado exitosamente a {payload.get('to')}")
                        return result
                    else:
                        logging.error(f"Error enviando mensaje: {result}")
                        raise Exception(f"Error API: {result}")
                        
        except Exception as e:
            logging.error(f"Error en send_message: {e}")
            raise
    
    async def send_text(self, to: str, message: str, preview_url: bool = True) -> Dict:
        """Enviar mensaje de texto"""
        payload = {
            "messaging_product": "whatsapp",
            "recipient_type": "individual",
            "to": to,
            "type": "text",
            "text": {
                "preview_url": preview_url,
                "body": message
            }
        }
        return await self.send_message(payload)
    
    async def send_buttons(self, to: str, body_text: str, buttons: List[Dict]) -> Dict:
        """Enviar botones interactivos"""
        if len(buttons) > 3:
            raise ValueError("Máximo 3 botones permitidos")
            
        button_components = [
            {
                "type": "reply",
                "reply": {
                    "id": btn["id"],
                    "title": btn["title"][:20]
                }
            }
            for btn in buttons
        ]
        
        payload = {
            "messaging_product": "whatsapp",
            "recipient_type": "individual",
            "to": to,
            "type": "interactive",
            "interactive": {
                "type": "button",
                "body": {"text": body_text},
                "action": {"buttons": button_components}
            }
        }
        return await self.send_message(payload)

# Ejemplo de uso del cliente unificado
client = WhatsAppBusinessClient(ACCESS_TOKEN, PHONE_NUMBER_ID)

# Enviar texto simple
await client.send_text("573001234567", "¡Hola desde RobertAI! 🤖")

# Enviar botones interactivos
await client.send_buttons(
    "573001234567",
    "¿Qué te gustaría saber?",
    [
        {"id": "services", "title": "🔍 Servicios"},
        {"id": "demo", "title": "🚀 Demo"},
        {"id": "contact", "title": "📞 Contacto"}
    ]
)
```

## Próximos Pasos

1. **Implementar webhooks**: Continuar con [Eventos de Webhook](04-webhook-events.md)
2. **Manejar multimedia**: Seguir [Manejo de Contenido Multimedia](05-multimedia-handling.md)
3. **Integrar con Bird.com**: Configurar [Integración con Bird.com](06-bird-integration.md)
4. **Aplicar mejores prácticas**: Revisar [Mejores Prácticas](08-best-practices.md)

---

**Nota**: Todos los ejemplos están optimizados para trabajar con Bird.com AI Employees y incluyen manejo de errores, rate limiting y logging apropiado para uso en producción.