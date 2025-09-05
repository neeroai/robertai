# Bird.com API Documentation

## Descripción General

Bird.com es una plataforma de comunicación omnicanal que permite a los desarrolladores integrar capacidades de mensajería, voz y AI Employees en sus aplicaciones. Esta documentación proporciona una guía completa de todas las APIs disponibles.

## APIs Principales

### 🚀 [Channels API](./channels/README.md)
Gestión de canales de comunicación incluyendo WhatsApp Business API, SMS, Email, RCS y más.

- **WhatsApp Business API** (Canal Principal) - Mensajería multimedia completa
- SMS, RCS, Email - Canales adicionales
- Mensajes interactivos - Botones, listas, carruseles, plantillas
- Configuración de webhooks y eventos

### 💬 [Conversations API](./conversations/README.md)
Gestión centralizada de conversaciones multi-participante con historial completo.

- Creación y gestión de conversaciones
- Manejo de participantes
- Preservación de contexto
- Integración con AI Employees

### 👥 [Contacts API](./contacts/README.md)
Gestión completa de contactos, listas y segmentación.

- Perfiles de contacto y atributos personalizados
- Listas y segmentación avanzada
- Tracking de eventos e interacciones

### 📞 [Numbers API](./numbers/README.md)
Búsqueda, compra y gestión de números telefónicos.

- Búsqueda y adquisición de números
- Cumplimiento normativo y registro 10DLC
- Gestión de configuraciones

### 🎤 [Voice API](./voice/README.md)
Capacidades de voz incluyendo llamadas, grabaciones y transcripción.

- Gestión de llamadas
- Grabaciones y transcripciones
- Integración con flujos conversacionales

### 🤖 [AI Employees](./ai-employees/README.md)
Configuración y gestión de agentes de IA conversacionales.

- Configuración de agentes inteligentes
- Procesamiento multimodal
- Flujos conversacionales personalizados
- Integración con sistemas externos

## Capacidades Especializadas

### 🎯 [Multimodal](./multimodal/README.md)
Procesamiento avanzado de contenido multimedia.

- **Imágenes**: JPG, PNG, WebP (hasta 5MB)
- **Videos**: MP4, 3GPP (hasta 16MB)
- **Audio**: AAC, M4A, AMRNB, MP3 (hasta 16MB)
- **Documentos**: PDF, DOCX, PPTX, XLSX (hasta 100MB)

### 🔧 [Integrations](./integrations/README.md)
Patrones de integración y mejores prácticas.

- Integraciones con CRM
- Conectividad con bases de datos
- Flujos de trabajo empresariales
- Webhooks y eventos

## Recursos de Desarrollo

### 📝 [Code Examples](./code-examples/README.md)
Ejemplos prácticos en múltiples lenguajes.

- Python (requests, SDK)
- JavaScript/Node.js
- cURL
- Casos de uso comunes

### 📋 [OpenAPI Specification](./openapi/README.md)
Especificaciones técnicas y herramientas.

- `openapi.yaml` - Especificación completa
- Colección Postman
- Herramientas de desarrollo

## Guías Esenciales

- [**Autenticación**](./authentication.md) - Métodos de autenticación y seguridad
- [**Rate Limits**](./rate-limits.md) - Límites de velocidad y cuotas
- [**Webhooks**](./webhooks.md) - Configuración de webhooks y eventos
- [**Error Handling**](./error-handling.md) - Códigos de error y manejo
- [**Best Practices**](./best-practices.md) - Mejores prácticas y recomendaciones

## Inicio Rápido

### 1. Autenticación
```bash
curl -H "Authorization: Bearer YOUR_API_TOKEN" \
     https://api.bird.com/v1/channels
```

### 2. Envío de Mensaje WhatsApp
```python
import requests

headers = {
    'Authorization': 'Bearer YOUR_API_TOKEN',
    'Content-Type': 'application/json'
}

data = {
    'to': '+1234567890',
    'type': 'text',
    'text': {
        'body': 'Hola desde Bird.com API!'
    }
}

response = requests.post(
    'https://api.bird.com/v1/channels/whatsapp/messages',
    headers=headers,
    json=data
)
```

### 3. Configuración de Webhook
```javascript
const webhook = {
    url: 'https://your-domain.com/webhook',
    events: ['message.received', 'message.delivered']
};

fetch('https://api.bird.com/v1/webhooks', {
    method: 'POST',
    headers: {
        'Authorization': 'Bearer YOUR_API_TOKEN',
        'Content-Type': 'application/json'
    },
    body: JSON.stringify(webhook)
});
```

## Soporte y Recursos

- **Documentación Oficial**: [docs.bird.com](https://docs.bird.com)
- **API Reference**: [docs.bird.com/api](https://docs.bird.com/api)
- **Soporte Técnico**: [support@bird.com](mailto:support@bird.com)
- **Status Page**: [status.bird.com](https://status.bird.com)

## Versionado

La API actual es **v1**. Todas las URLs base usan:
```
https://api.bird.com/v1/
```

## Límites y Cuotas

- **Rate Limit**: 1000 requests/minute por API key
- **Rate Limit por Usuario**: 100 requests/minute por usuario
- **Tamaño Máximo**: 100MB para documentos, 16MB para multimedia
- **Retención**: Webhooks retenidos por 7 días

---

Esta documentación está mantenida por el equipo de RobertAI y se actualiza regularmente con las últimas características de la plataforma Bird.com.