# Conversations API Documentation

## Descripción General

La Conversations API de Bird.com permite gestionar mensajes intercambiados entre dos o más participantes de manera centralizada. Esta API es opcional pero proporciona capacidades avanzadas para el seguimiento del historial de conversaciones y la preservación del contexto a través de diferentes etapas de interacción.

## Características Principales

- **Gestión Centralizada**: Control completo sobre conversaciones multi-participante
- **Historial Completo**: Seguimiento de mensajes a través de diferentes etapas de interacción
- **Preservación de Contexto**: Mantiene el contexto del contacto a lo largo de su journey
- **Integración Flexible**: Opcional, con alternativas simplificadas disponibles

## Base URL

```
https://api.bird.com/v1
```

## Autenticación

```bash
Authorization: Bearer YOUR_API_TOKEN
```

## Endpoints Principales

### 1. Gestión de Conversaciones

#### Crear Conversación

**POST** `/v1/conversations`

```bash
curl -X POST "https://api.bird.com/v1/conversations" \
  -H "Authorization: Bearer YOUR_API_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "participants": [
      {
        "contact_id": "contact_123",
        "role": "customer"
      },
      {
        "agent_id": "agent_456",
        "role": "agent"
      }
    ],
    "channel": "whatsapp",
    "subject": "Consulta sobre producto",
    "tags": ["soporte", "producto"]
  }'
```

**Respuesta:**
```json
{
  "id": "conv_789",
  "status": "active",
  "created_at": "2024-01-15T10:30:00Z",
  "updated_at": "2024-01-15T10:30:00Z",
  "participants": [
    {
      "id": "participant_001",
      "contact_id": "contact_123",
      "role": "customer",
      "joined_at": "2024-01-15T10:30:00Z"
    },
    {
      "id": "participant_002", 
      "agent_id": "agent_456",
      "role": "agent",
      "joined_at": "2024-01-15T10:30:00Z"
    }
  ],
  "channel": "whatsapp",
  "subject": "Consulta sobre producto",
  "tags": ["soporte", "producto"],
  "message_count": 0
}
```

#### Listar Conversaciones

**GET** `/v1/conversations`

```bash
curl -X GET "https://api.bird.com/v1/conversations?status=active&channel=whatsapp&limit=20" \
  -H "Authorization: Bearer YOUR_API_TOKEN"
```

**Respuesta:**
```json
{
  "conversations": [
    {
      "id": "conv_789",
      "status": "active",
      "created_at": "2024-01-15T10:30:00Z",
      "last_message_at": "2024-01-15T11:15:00Z",
      "participants_count": 2,
      "message_count": 5,
      "channel": "whatsapp",
      "subject": "Consulta sobre producto"
    }
  ],
  "pagination": {
    "limit": 20,
    "offset": 0,
    "total": 1,
    "has_more": false
  }
}
```

#### Obtener Conversación

**GET** `/v1/conversations/{conversation_id}`

```bash
curl -X GET "https://api.bird.com/v1/conversations/conv_789" \
  -H "Authorization: Bearer YOUR_API_TOKEN"
```

#### Actualizar Conversación

**PATCH** `/v1/conversations/{conversation_id}`

```json
{
  "status": "resolved",
  "tags": ["soporte", "producto", "resuelto"],
  "metadata": {
    "resolution": "Producto enviado correctamente",
    "satisfaction_score": 5
  }
}
```

#### Eliminar Conversación

**DELETE** `/v1/conversations/{conversation_id}`

### 2. Gestión de Participantes

#### Agregar Participante

**POST** `/v1/conversations/{conversation_id}/participants`

```json
{
  "contact_id": "contact_999",
  "role": "supervisor",
  "permissions": ["read", "write"]
}
```

**Respuesta:**
```json
{
  "id": "participant_003",
  "contact_id": "contact_999", 
  "role": "supervisor",
  "permissions": ["read", "write"],
  "joined_at": "2024-01-15T12:00:00Z"
}
```

#### Listar Participantes

**GET** `/v1/conversations/{conversation_id}/participants`

#### Actualizar Participante

**PATCH** `/v1/conversations/{conversation_id}/participants/{participant_id}`

```json
{
  "role": "manager",
  "permissions": ["read", "write", "manage"]
}
```

#### Eliminar Participante

**DELETE** `/v1/conversations/{conversation_id}/participants/{participant_id}`

### 3. Gestión de Mensajes

#### Crear Mensaje en Conversación

**POST** `/v1/conversations/{conversation_id}/messages`

```json
{
  "type": "text",
  "text": {
    "body": "Hola, gracias por contactarnos. ¿En qué podemos ayudarte?"
  },
  "sender": {
    "agent_id": "agent_456"
  },
  "metadata": {
    "internal_note": "Primera respuesta automática"
  }
}
```

**Respuesta:**
```json
{
  "id": "msg_001",
  "conversation_id": "conv_789",
  "type": "text",
  "text": {
    "body": "Hola, gracias por contactarnos. ¿En qué podemos ayudarte?"
  },
  "sender": {
    "agent_id": "agent_456",
    "name": "Ana García"
  },
  "timestamp": "2024-01-15T10:35:00Z",
  "status": "sent"
}
```

#### Listar Mensajes de Conversación

**GET** `/v1/conversations/{conversation_id}/messages`

```bash
curl -X GET "https://api.bird.com/v1/conversations/conv_789/messages?limit=50&order=desc" \
  -H "Authorization: Bearer YOUR_API_TOKEN"
```

**Respuesta:**
```json
{
  "messages": [
    {
      "id": "msg_003",
      "type": "text",
      "text": {
        "body": "Perfecto, muchas gracias por la ayuda!"
      },
      "sender": {
        "contact_id": "contact_123",
        "name": "Juan Pérez"
      },
      "timestamp": "2024-01-15T11:15:00Z",
      "status": "read"
    },
    {
      "id": "msg_002",
      "type": "image",
      "image": {
        "url": "https://cdn.bird.com/images/product_123.jpg",
        "caption": "Aquí está la imagen del producto"
      },
      "sender": {
        "agent_id": "agent_456",
        "name": "Ana García"
      },
      "timestamp": "2024-01-15T10:50:00Z",
      "status": "delivered"
    }
  ],
  "pagination": {
    "limit": 50,
    "offset": 0,
    "total": 3
  }
}
```

#### Obtener Mensaje Específico

**GET** `/v1/conversations/{conversation_id}/messages/{message_id}`

#### Actualizar Mensaje

**PATCH** `/v1/conversations/{conversation_id}/messages/{message_id}`

```json
{
  "metadata": {
    "edited": true,
    "edit_reason": "Corrección de información"
  }
}
```

#### Eliminar Mensaje

**DELETE** `/v1/conversations/{conversation_id}/messages/{message_id}`

### 4. Subida de Archivos

#### Crear Pre-signed Upload

**POST** `/v1/conversations/{conversation_id}/uploads`

```json
{
  "filename": "documento.pdf",
  "content_type": "application/pdf",
  "size": 1024000
}
```

**Respuesta:**
```json
{
  "upload_url": "https://uploads.bird.com/signed-url-here",
  "file_id": "file_123",
  "expires_at": "2024-01-15T11:30:00Z"
}
```

### 5. Configuración de Workspace

#### Configurar Antispam

**POST** `/v1/workspace/settings/antispam`

```json
{
  "enabled": true,
  "sensitivity": "medium",
  "actions": ["flag", "quarantine"],
  "whitelist_domains": ["empresa.com"],
  "blacklist_keywords": ["spam", "promotional"]
}
```

#### Crear Reglas de Comunicación

**POST** `/v1/workspace/communication-rules`

```json
{
  "name": "Horario Comercial",
  "type": "allow",
  "conditions": {
    "time_range": {
      "start": "09:00",
      "end": "18:00",
      "timezone": "America/Mexico_City"
    },
    "days": ["monday", "tuesday", "wednesday", "thursday", "friday"]
  },
  "actions": {
    "auto_reply": "Estamos fuera del horario comercial. Te contactaremos pronto.",
    "route_to": "after_hours_queue"
  }
}
```

## Tipos de Mensaje Soportados

### Mensaje de Texto
```json
{
  "type": "text",
  "text": {
    "body": "Mensaje de texto simple"
  }
}
```

### Mensaje Multimedia
```json
{
  "type": "image",
  "image": {
    "url": "https://example.com/image.jpg",
    "caption": "Descripción de la imagen"
  }
}
```

### Mensaje de Ubicación
```json
{
  "type": "location",
  "location": {
    "latitude": 19.4326,
    "longitude": -99.1332,
    "name": "Ciudad de México",
    "address": "CDMX, México"
  }
}
```

### Mensaje de Contacto
```json
{
  "type": "contact",
  "contact": {
    "formatted_name": "Juan Pérez",
    "phones": [
      {
        "phone": "+5215512345678",
        "type": "MOBILE"
      }
    ],
    "emails": [
      {
        "email": "juan@ejemplo.com",
        "type": "WORK"
      }
    ]
  }
}
```

## Webhooks para Conversaciones

### Eventos Disponibles

| Evento | Descripción |
|--------|-------------|
| `conversation.created` | Nueva conversación creada |
| `conversation.updated` | Conversación actualizada |
| `conversation.participant.added` | Participante agregado |
| `conversation.participant.removed` | Participante eliminado |
| `conversation.message.created` | Nuevo mensaje en conversación |
| `conversation.message.updated` | Mensaje actualizado |

### Ejemplo de Webhook

```json
{
  "event": "conversation.message.created",
  "timestamp": "2024-01-15T10:35:00Z",
  "conversation": {
    "id": "conv_789",
    "subject": "Consulta sobre producto"
  },
  "message": {
    "id": "msg_001",
    "type": "text",
    "text": {
      "body": "Nuevo mensaje del cliente"
    },
    "sender": {
      "contact_id": "contact_123",
      "name": "Juan Pérez"
    }
  }
}
```

## Ejemplos de Implementación

### Python - Gestor de Conversaciones

```python
import requests
import json
from datetime import datetime

class BirdConversationsAPI:
    def __init__(self, api_token):
        self.api_token = api_token
        self.base_url = "https://api.bird.com/v1"
        self.headers = {
            'Authorization': f'Bearer {api_token}',
            'Content-Type': 'application/json'
        }
    
    def create_conversation(self, participants, channel, subject=None, tags=None):
        """Crear una nueva conversación"""
        data = {
            "participants": participants,
            "channel": channel,
            "subject": subject,
            "tags": tags or []
        }
        
        response = requests.post(
            f"{self.base_url}/conversations",
            headers=self.headers,
            json=data
        )
        
        return response.json()
    
    def add_message(self, conversation_id, message_type, content, sender):
        """Agregar mensaje a conversación"""
        data = {
            "type": message_type,
            message_type: content,
            "sender": sender
        }
        
        response = requests.post(
            f"{self.base_url}/conversations/{conversation_id}/messages",
            headers=self.headers,
            json=data
        )
        
        return response.json()
    
    def get_conversation_history(self, conversation_id, limit=50):
        """Obtener historial de conversación"""
        response = requests.get(
            f"{self.base_url}/conversations/{conversation_id}/messages?limit={limit}",
            headers=self.headers
        )
        
        return response.json()
    
    def add_participant(self, conversation_id, contact_id, role="participant"):
        """Agregar participante a conversación"""
        data = {
            "contact_id": contact_id,
            "role": role
        }
        
        response = requests.post(
            f"{self.base_url}/conversations/{conversation_id}/participants",
            headers=self.headers,
            json=data
        )
        
        return response.json()
    
    def close_conversation(self, conversation_id, resolution=None):
        """Cerrar conversación"""
        data = {
            "status": "resolved",
            "metadata": {
                "resolution": resolution,
                "closed_at": datetime.now().isoformat()
            }
        }
        
        response = requests.patch(
            f"{self.base_url}/conversations/{conversation_id}",
            headers=self.headers,
            json=data
        )
        
        return response.json()

# Ejemplo de uso
api = BirdConversationsAPI("your_api_token")

# Crear conversación
participants = [
    {"contact_id": "contact_123", "role": "customer"},
    {"agent_id": "agent_456", "role": "agent"}
]

conversation = api.create_conversation(
    participants=participants,
    channel="whatsapp",
    subject="Consulta sobre producto",
    tags=["soporte", "producto"]
)

# Agregar mensaje
message = api.add_message(
    conversation_id=conversation["id"],
    message_type="text",
    content={"body": "Hola, ¿en qué puedo ayudarte?"},
    sender={"agent_id": "agent_456"}
)

print(f"Conversación creada: {conversation['id']}")
print(f"Mensaje enviado: {message['id']}")
```

### JavaScript - Gestor de Conversaciones

```javascript
class BirdConversationsAPI {
    constructor(apiToken) {
        this.apiToken = apiToken;
        this.baseURL = 'https://api.bird.com/v1';
        this.headers = {
            'Authorization': `Bearer ${apiToken}`,
            'Content-Type': 'application/json'
        };
    }
    
    async createConversation(participants, channel, subject, tags = []) {
        const data = {
            participants,
            channel,
            subject,
            tags
        };
        
        const response = await fetch(`${this.baseURL}/conversations`, {
            method: 'POST',
            headers: this.headers,
            body: JSON.stringify(data)
        });
        
        return await response.json();
    }
    
    async addMessage(conversationId, messageType, content, sender) {
        const data = {
            type: messageType,
            [messageType]: content,
            sender
        };
        
        const response = await fetch(
            `${this.baseURL}/conversations/${conversationId}/messages`,
            {
                method: 'POST',
                headers: this.headers,
                body: JSON.stringify(data)
            }
        );
        
        return await response.json();
    }
    
    async getConversationHistory(conversationId, limit = 50) {
        const response = await fetch(
            `${this.baseURL}/conversations/${conversationId}/messages?limit=${limit}`,
            { headers: this.headers }
        );
        
        return await response.json();
    }
    
    async searchConversations(filters = {}) {
        const params = new URLSearchParams(filters);
        
        const response = await fetch(
            `${this.baseURL}/conversations?${params}`,
            { headers: this.headers }
        );
        
        return await response.json();
    }
    
    async transferConversation(conversationId, newAgentId, notes = '') {
        const participant = await this.addParticipant(conversationId, {
            agent_id: newAgentId,
            role: 'agent'
        });
        
        // Agregar nota de transferencia
        await this.addMessage(conversationId, 'text', {
            body: `Conversación transferida. Notas: ${notes}`
        }, {
            agent_id: newAgentId
        });
        
        return participant;
    }
    
    async addParticipant(conversationId, participant) {
        const response = await fetch(
            `${this.baseURL}/conversations/${conversationId}/participants`,
            {
                method: 'POST',
                headers: this.headers,
                body: JSON.stringify(participant)
            }
        );
        
        return await response.json();
    }
}

// Ejemplo de uso con sistema de tickets
class SupportTicketSystem {
    constructor(apiToken) {
        this.conversationAPI = new BirdConversationsAPI(apiToken);
    }
    
    async createSupportTicket(customerContactId, issue, priority = 'normal') {
        const conversation = await this.conversationAPI.createConversation(
            [
                { contact_id: customerContactId, role: 'customer' },
                { agent_id: this.getAvailableAgent(priority), role: 'agent' }
            ],
            'whatsapp',
            `Ticket de Soporte: ${issue}`,
            ['soporte', priority]
        );
        
        // Enviar mensaje inicial
        await this.conversationAPI.addMessage(
            conversation.id,
            'text',
            { body: 'Hemos recibido tu consulta. Un agente te atenderá pronto.' },
            { agent_id: conversation.participants[1].agent_id }
        );
        
        return {
            ticketId: conversation.id,
            status: 'created',
            priority
        };
    }
    
    getAvailableAgent(priority) {
        // Lógica para asignar agente según prioridad
        return priority === 'high' ? 'senior_agent_001' : 'agent_general_001';
    }
}
```

## Casos de Uso Comunes

### 1. Sistema de Soporte al Cliente
- Crear conversación por ticket
- Asignar agentes especializados
- Transferir entre departamentos
- Mantener historial completo

### 2. Venta Consultiva
- Seguimiento de leads
- Múltiples interacciones comerciales
- Colaboración entre vendedores
- Preservar contexto de compra

### 3. Servicios Profesionales
- Consultas multi-sesión
- Colaboración con especialistas
- Documentación de avance
- Historial de proyecto

### 4. Atención Médica/Legal
- Expedientes digitales
- Consultas multi-profesional
- Documentación regulada
- Privacidad y confidencialidad

## Mejores Prácticas

### 1. Gestión de Estado
```python
# Definir estados claros
CONVERSATION_STATES = {
    'NEW': 'new',
    'ACTIVE': 'active',
    'WAITING': 'waiting_for_customer',
    'ESCALATED': 'escalated',
    'RESOLVED': 'resolved',
    'CLOSED': 'closed'
}

# Transiciones de estado
def update_conversation_state(conversation_id, new_state, metadata=None):
    return api.update_conversation(conversation_id, {
        'status': new_state,
        'metadata': {
            'state_changed_at': datetime.now().isoformat(),
            'previous_state': get_current_state(conversation_id),
            **(metadata or {})
        }
    })
```

### 2. Etiquetado Inteligente
```python
def smart_tagging(message_content, conversation_context):
    tags = []
    
    # Auto-detectar tipo de consulta
    if any(word in message_content.lower() for word in ['precio', 'costo', 'pago']):
        tags.append('comercial')
    
    if any(word in message_content.lower() for word in ['problema', 'error', 'falla']):
        tags.append('soporte_tecnico')
    
    # Detectar urgencia
    if any(word in message_content.lower() for word in ['urgente', 'emergencia', 'inmediato']):
        tags.append('alta_prioridad')
    
    return tags
```

### 3. Métricas y Análisis
```python
def get_conversation_metrics(conversation_id):
    conversation = api.get_conversation(conversation_id)
    messages = api.get_conversation_history(conversation_id)
    
    return {
        'duration': calculate_duration(conversation),
        'message_count': len(messages['messages']),
        'response_time_avg': calculate_avg_response_time(messages['messages']),
        'participant_count': len(conversation['participants']),
        'resolution_time': calculate_resolution_time(conversation)
    }
```

## Limitaciones y Consideraciones

### 1. Límites de Escalabilidad
- Máximo 100 participantes por conversación
- Historial de mensajes limitado a 10,000 por conversación
- Archivos adjuntos con límite de 100MB

### 2. Rate Limiting
- 1000 requests/minute para conversaciones
- 500 requests/minute para mensajes
- 100 requests/minute para uploads

### 3. Retención de Datos
- Conversaciones activas: Sin límite
- Conversaciones cerradas: 2 años
- Archivos multimedia: 1 año
- Logs de webhook: 30 días

## Códigos de Error Específicos

| Código | Error | Descripción |
|--------|-------|-------------|
| `2001` | Conversation Not Found | Conversación no existe |
| `2002` | Invalid Participant | Participante inválido |
| `2003` | Conversation Closed | No se puede modificar conversación cerrada |
| `2004` | Participant Limit Exceeded | Límite de participantes excedido |
| `2005` | Message Too Large | Mensaje excede tamaño máximo |

## Recursos Relacionados

- [Channels API](../channels/README.md) - Para envío directo de mensajes
- [Contacts API](../contacts/README.md) - Gestión de participantes
- [Webhooks](../webhooks.md) - Eventos de conversación
- [Authentication](../authentication.md) - Configuración de acceso
- [Code Examples](../code-examples/conversations/) - Ejemplos prácticos

---

La Conversations API es ideal para casos de uso que requieren seguimiento detallado de interacciones y colaboración entre múltiples participantes. Para casos más simples, considera usar la Channels API directamente.