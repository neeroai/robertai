# Channels API Documentation

## Descripción General

La Channels API de Bird.com proporciona una solución omnicanal completa para mensajería a través de múltiples plataformas de comunicación. Esta API permite enviar y recibir mensajes, gestionar configuraciones de canales y configurar webhooks para eventos en tiempo real.

## Canales Soportados

### 📱 WhatsApp Business API (Canal Principal)
- **Alcance Global**: Más de 2 mil millones de usuarios activos mensuales en 180+ países
- **Conversaciones Bidireccionales**: Comunicación completa empresa-cliente
- **Soporte Multimedia Completo**: Imágenes, videos, audio, documentos
- **Mensajes Interactivos**: Botones, listas, carruseles, plantillas
- **Ventana de Atención**: 24 horas para responder mensajes entrantes

### 📨 Otros Canales Disponibles
- **SMS**: Mensajería de texto tradicional
- **RCS**: Rich Communication Services
- **Email**: Correo electrónico
- **Telegram**: Mensajería instantánea
- **Line**: Popular en Asia-Pacífico

## Endpoints Principales

### Base URL
```
https://api.bird.com/v1
```

### Autenticación
```bash
Authorization: Bearer YOUR_API_TOKEN
```

## WhatsApp Business API

### Configuración Inicial

#### Requisitos Previos
- Cuenta personal de Facebook para Meta Business Manager
- Nombre legal de la empresa y nombre para mostrar
- URL del sitio web de la empresa
- Email y teléfono comercial
- Acceso al número de teléfono para verificación

#### Niveles de Verificación
- **Básico**: Funcionalidades limitadas
- **Completo**: Acceso a todas las características (recomendado)

### Tipos de Mensajes

#### 1. Mensajes de Texto
```json
{
  "to": "+1234567890",
  "type": "text",
  "text": {
    "body": "¡Hola! ¿En qué puedo ayudarte hoy?"
  }
}
```

#### 2. Mensajes Multimedia

**Imágenes**
```json
{
  "to": "+1234567890",
  "type": "image",
  "image": {
    "url": "https://example.com/image.jpg",
    "caption": "Descripción de la imagen"
  }
}
```

**Documentos**
```json
{
  "to": "+1234567890",
  "type": "document",
  "document": {
    "url": "https://example.com/document.pdf",
    "filename": "documento.pdf",
    "caption": "Aquí está tu documento"
  }
}
```

**Audio**
```json
{
  "to": "+1234567890",
  "type": "audio",
  "audio": {
    "url": "https://example.com/audio.mp3"
  }
}
```

**Video**
```json
{
  "to": "+1234567890",
  "type": "video",
  "video": {
    "url": "https://example.com/video.mp4",
    "caption": "Mira este video"
  }
}
```

#### 3. Mensajes Interactivos

**Botones**
```json
{
  "to": "+1234567890",
  "type": "interactive",
  "interactive": {
    "type": "button",
    "header": {
      "type": "text",
      "text": "Selecciona una opción"
    },
    "body": {
      "text": "¿Qué te gustaría hacer?"
    },
    "action": {
      "buttons": [
        {
          "type": "reply",
          "reply": {
            "id": "info",
            "title": "Más información"
          }
        },
        {
          "type": "reply",
          "reply": {
            "id": "contact",
            "title": "Contactar"
          }
        }
      ]
    }
  }
}
```

**Lista**
```json
{
  "to": "+1234567890",
  "type": "interactive",
  "interactive": {
    "type": "list",
    "header": {
      "type": "text",
      "text": "Productos Disponibles"
    },
    "body": {
      "text": "Selecciona un producto de la lista:"
    },
    "footer": {
      "text": "Precios sujetos a cambio"
    },
    "action": {
      "button": "Ver Productos",
      "sections": [
        {
          "title": "Electrónicos",
          "rows": [
            {
              "id": "phone_001",
              "title": "Smartphone",
              "description": "iPhone 15 Pro Max"
            },
            {
              "id": "laptop_001",
              "title": "Laptop",
              "description": "MacBook Air M2"
            }
          ]
        }
      ]
    }
  }
}
```

#### 4. Mensajes de Plantilla

```json
{
  "to": "+1234567890",
  "type": "template",
  "template": {
    "name": "welcome_message",
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
            "text": "Premium"
          },
          {
            "type": "text",
            "text": "15"
          }
        ]
      }
    ]
  }
}
```

## Endpoints de la API

### 1. Enviar Mensaje

**POST** `/v1/channels/{channel_id}/messages`

```bash
curl -X POST "https://api.bird.com/v1/channels/whatsapp/messages" \
  -H "Authorization: Bearer YOUR_API_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "to": "+1234567890",
    "type": "text",
    "text": {
      "body": "Hola desde Bird.com!"
    }
  }'
```

**Respuesta Exitosa:**
```json
{
  "id": "msg_1234567890",
  "status": "sent",
  "timestamp": "2024-01-15T10:30:00Z"
}
```

### 2. Obtener Canales

**GET** `/v1/channels`

```bash
curl -X GET "https://api.bird.com/v1/channels" \
  -H "Authorization: Bearer YOUR_API_TOKEN"
```

**Respuesta:**
```json
{
  "channels": [
    {
      "id": "whatsapp_123",
      "type": "whatsapp",
      "status": "active",
      "phone_number": "+1234567890",
      "display_name": "Mi Empresa"
    }
  ]
}
```

### 3. Configurar Canal

**PATCH** `/v1/channels/{channel_id}`

```bash
curl -X PATCH "https://api.bird.com/v1/channels/whatsapp_123" \
  -H "Authorization: Bearer YOUR_API_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "display_name": "Nueva Empresa",
    "about": "Descripción actualizada"
  }'
```

### 4. Estado de Mensaje

**GET** `/v1/channels/{channel_id}/messages/{message_id}`

```bash
curl -X GET "https://api.bird.com/v1/channels/whatsapp_123/messages/msg_1234567890" \
  -H "Authorization: Bearer YOUR_API_TOKEN"
```

**Respuesta:**
```json
{
  "id": "msg_1234567890",
  "status": "delivered",
  "timestamp": "2024-01-15T10:30:00Z",
  "recipient": "+1234567890"
}
```

## Webhooks

### Configuración de Webhook

**POST** `/v1/webhooks`

```json
{
  "url": "https://your-domain.com/webhook",
  "events": [
    "message.received",
    "message.delivered",
    "message.read",
    "message.failed"
  ],
  "channels": ["whatsapp"]
}
```

### Eventos de Webhook

#### Mensaje Recibido
```json
{
  "event": "message.received",
  "timestamp": "2024-01-15T10:30:00Z",
  "channel": {
    "id": "whatsapp_123",
    "type": "whatsapp"
  },
  "message": {
    "id": "msg_incoming_123",
    "from": "+1234567890",
    "type": "text",
    "text": {
      "body": "Hola, necesito ayuda"
    }
  }
}
```

#### Estado de Mensaje
```json
{
  "event": "message.delivered",
  "timestamp": "2024-01-15T10:31:00Z",
  "message_id": "msg_1234567890",
  "status": "delivered"
}
```

## Limitaciones y Consideraciones

### Límites de WhatsApp
- **Tamaño de Archivos**:
  - Imágenes: Hasta 5MB (JPG, PNG, WebP)
  - Videos: Hasta 16MB (MP4, 3GPP)
  - Audio: Hasta 16MB (AAC, M4A, AMRNB, MP3)
  - Documentos: Hasta 100MB (PDF, DOCX, PPTX, XLSX)

### Ventana de Mensajería
- **24 horas**: Ventana para responder a mensajes entrantes
- **Plantillas**: Requeridas para mensajes fuera de la ventana
- **Aprobación**: Las plantillas requieren aprobación de Meta

### Rate Limits
- **API General**: 1000 requests/minute por API key
- **Por Usuario**: 100 requests/minute por usuario final
- **WhatsApp Específico**: Límites adicionales según el nivel de verificación

## Códigos de Error

### Errores Comunes

| Código | Descripción | Solución |
|--------|-------------|-----------|
| `400` | Bad Request | Verificar formato de datos |
| `401` | Unauthorized | Validar token de autorización |
| `403` | Forbidden | Verificar permisos del canal |
| `404` | Not Found | Verificar ID del canal/mensaje |
| `429` | Rate Limited | Implementar rate limiting |
| `500` | Server Error | Reintentar con backoff exponencial |

### Errores Específicos de WhatsApp

| Código | Error | Descripción |
|--------|-------|-------------|
| `1001` | Invalid Phone Number | Número de teléfono inválido |
| `1002` | Template Not Found | Plantilla no encontrada o no aprobada |
| `1003` | Media Upload Failed | Error al subir archivo multimedia |
| `1004` | Outside Message Window | Fuera de la ventana de 24 horas |

## Ejemplos de Implementación

### Python con Requests
```python
import requests
import json

class BirdWhatsAppAPI:
    def __init__(self, api_token):
        self.api_token = api_token
        self.base_url = "https://api.bird.com/v1"
        self.headers = {
            'Authorization': f'Bearer {api_token}',
            'Content-Type': 'application/json'
        }
    
    def send_text_message(self, to, text):
        data = {
            "to": to,
            "type": "text",
            "text": {"body": text}
        }
        
        response = requests.post(
            f"{self.base_url}/channels/whatsapp/messages",
            headers=self.headers,
            json=data
        )
        
        return response.json()
    
    def send_image(self, to, image_url, caption=None):
        data = {
            "to": to,
            "type": "image",
            "image": {
                "url": image_url,
                "caption": caption
            }
        }
        
        response = requests.post(
            f"{self.base_url}/channels/whatsapp/messages",
            headers=self.headers,
            json=data
        )
        
        return response.json()

# Uso
api = BirdWhatsAppAPI("your_api_token")
result = api.send_text_message("+1234567890", "¡Hola desde Python!")
```

### JavaScript/Node.js
```javascript
const axios = require('axios');

class BirdWhatsAppAPI {
    constructor(apiToken) {
        this.apiToken = apiToken;
        this.baseURL = 'https://api.bird.com/v1';
        this.headers = {
            'Authorization': `Bearer ${apiToken}`,
            'Content-Type': 'application/json'
        };
    }
    
    async sendTextMessage(to, text) {
        const data = {
            to: to,
            type: 'text',
            text: { body: text }
        };
        
        try {
            const response = await axios.post(
                `${this.baseURL}/channels/whatsapp/messages`,
                data,
                { headers: this.headers }
            );
            
            return response.data;
        } catch (error) {
            console.error('Error sending message:', error.response.data);
            throw error;
        }
    }
    
    async sendInteractiveButtons(to, body, buttons) {
        const data = {
            to: to,
            type: 'interactive',
            interactive: {
                type: 'button',
                body: { text: body },
                action: {
                    buttons: buttons.map((button, index) => ({
                        type: 'reply',
                        reply: {
                            id: `btn_${index}`,
                            title: button
                        }
                    }))
                }
            }
        };
        
        const response = await axios.post(
            `${this.baseURL}/channels/whatsapp/messages`,
            data,
            { headers: this.headers }
        );
        
        return response.data;
    }
}

// Uso
const api = new BirdWhatsAppAPI('your_api_token');
api.sendTextMessage('+1234567890', '¡Hola desde JavaScript!')
   .then(result => console.log(result));
```

## Mejores Prácticas

### 1. Gestión de Errores
- Implementar retry logic con backoff exponencial
- Manejar errores específicos de WhatsApp
- Logging detallado para debugging

### 2. Optimización de Performance
- Batch messages cuando sea posible
- Implementar caching para plantillas
- Monitorear rate limits proactivamente

### 3. Experiencia de Usuario
- Usar mensajes interactivos para mejor UX
- Implementar indicadores de typing
- Responder dentro de la ventana de 24 horas

### 4. Seguridad
- Validar webhooks con signatures
- Sanitizar datos de entrada
- Implementar rate limiting en webhooks

## Recursos Adicionales

- [Guía de Webhooks](../webhooks.md)
- [Autenticación](../authentication.md)
- [Códigos de Error Completos](../error-handling.md)
- [Ejemplos de Código](../code-examples/whatsapp/)
- [Mejores Prácticas](../best-practices.md)

---

**Nota**: Esta documentación cubre las características principales de la Channels API. Para casos de uso específicos y configuraciones avanzadas, consulta la documentación oficial de Bird.com o contacta al soporte técnico.