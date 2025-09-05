# Contacts API Documentation

## Descripción General

La Contacts API de Bird.com proporciona una solución completa para gestionar información de contactos de clientes. Esta API permite crear y mantener registros de contactos, gestionar múltiples identificadores, configurar atributos personalizados y realizar seguimiento de eventos e interacciones.

## Características Principales

- **Gestión Completa**: Crear, actualizar, buscar y eliminar contactos
- **Múltiples Identificadores**: Soporte para email, teléfono y otros identificadores
- **Atributos Personalizados**: Esquemas flexibles de datos
- **Listas de Segmentación**: Agrupación y categorización de contactos
- **Seguimiento de Eventos**: Tracking de interacciones y comportamiento
- **Integración Nativa**: Compatible con Channels y Conversations APIs

## Base URL

```
https://api.bird.com/v1
```

## Autenticación

```bash
Authorization: Bearer YOUR_API_TOKEN
```

## Endpoints Principales

### 1. Gestión de Contactos

#### Crear Contacto

**POST** `/v1/contacts`

```bash
curl -X POST "https://api.bird.com/v1/contacts" \
  -H "Authorization: Bearer YOUR_API_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "identifiers": [
      {
        "type": "email",
        "value": "juan.perez@ejemplo.com"
      },
      {
        "type": "phone", 
        "value": "+5215512345678"
      }
    ],
    "attributes": {
      "firstName": "Juan",
      "lastName": "Pérez",
      "company": "Empresa SA",
      "position": "Gerente",
      "preferences": {
        "language": "es",
        "timezone": "America/Mexico_City"
      }
    },
    "tags": ["cliente_vip", "comercial"],
    "source": "website_form"
  }'
```

**Respuesta:**
```json
{
  "id": "contact_123456",
  "created_at": "2024-01-15T10:30:00Z",
  "updated_at": "2024-01-15T10:30:00Z",
  "identifiers": [
    {
      "id": "ident_001",
      "type": "email",
      "value": "juan.perez@ejemplo.com",
      "verified": false,
      "primary": true
    },
    {
      "id": "ident_002", 
      "type": "phone",
      "value": "+5215512345678",
      "verified": false,
      "primary": false
    }
  ],
  "attributes": {
    "firstName": "Juan",
    "lastName": "Pérez",
    "company": "Empresa SA",
    "position": "Gerente",
    "preferences": {
      "language": "es",
      "timezone": "America/Mexico_City"
    }
  },
  "tags": ["cliente_vip", "comercial"],
  "source": "website_form",
  "status": "active",
  "last_activity": null
}
```

#### Buscar Contacto

**GET** `/v1/contacts/{contact_id}`

```bash
curl -X GET "https://api.bird.com/v1/contacts/contact_123456" \
  -H "Authorization: Bearer YOUR_API_TOKEN"
```

**Buscar por Identificador:**

**GET** `/v1/contacts/search`

```bash
curl -X GET "https://api.bird.com/v1/contacts/search?identifier_type=email&identifier_value=juan.perez@ejemplo.com" \
  -H "Authorization: Bearer YOUR_API_TOKEN"
```

#### Listar Contactos

**GET** `/v1/contacts`

```bash
curl -X GET "https://api.bird.com/v1/contacts?limit=50&tags=cliente_vip&source=website" \
  -H "Authorization: Bearer YOUR_API_TOKEN"
```

**Respuesta:**
```json
{
  "contacts": [
    {
      "id": "contact_123456",
      "identifiers": [
        {
          "type": "email",
          "value": "juan.perez@ejemplo.com"
        }
      ],
      "attributes": {
        "firstName": "Juan",
        "lastName": "Pérez"
      },
      "tags": ["cliente_vip"],
      "last_activity": "2024-01-14T15:30:00Z"
    }
  ],
  "pagination": {
    "limit": 50,
    "offset": 0,
    "total": 1,
    "has_more": false
  }
}
```

#### Actualizar Contacto

**PATCH** `/v1/contacts/{contact_id}`

```json
{
  "attributes": {
    "position": "Director General",
    "preferences": {
      "notifications": true,
      "marketing": false
    }
  },
  "tags": ["cliente_vip", "decision_maker"],
  "status": "active"
}
```

#### Eliminar Contacto

**DELETE** `/v1/contacts/{contact_id}`

```bash
curl -X DELETE "https://api.bird.com/v1/contacts/contact_123456" \
  -H "Authorization: Bearer YOUR_API_TOKEN"
```

### 2. Gestión de Identificadores

#### Agregar Identificador

**POST** `/v1/contacts/{contact_id}/identifiers`

```json
{
  "type": "whatsapp",
  "value": "+5215512345678",
  "primary": false
}
```

**Respuesta:**
```json
{
  "id": "ident_003",
  "type": "whatsapp", 
  "value": "+5215512345678",
  "verified": false,
  "primary": false,
  "created_at": "2024-01-15T11:00:00Z"
}
```

#### Verificar Identificador

**POST** `/v1/contacts/{contact_id}/identifiers/{identifier_id}/verify`

```json
{
  "verification_code": "123456"
}
```

#### Establecer Identificador Principal

**PATCH** `/v1/contacts/{contact_id}/identifiers/{identifier_id}`

```json
{
  "primary": true
}
```

#### Listar Identificadores

**GET** `/v1/contacts/{contact_id}/identifiers`

#### Eliminar Identificador

**DELETE** `/v1/contacts/{contact_id}/identifiers/{identifier_id}`

### 3. Atributos Personalizados

#### Crear Definición de Atributo

**POST** `/v1/attributes`

```json
{
  "name": "fecha_nacimiento",
  "display_name": "Fecha de Nacimiento",
  "type": "date",
  "description": "Fecha de nacimiento del contacto",
  "required": false,
  "validation": {
    "min_date": "1900-01-01",
    "max_date": "2010-12-31"
  },
  "default_value": null
}
```

**Respuesta:**
```json
{
  "id": "attr_001",
  "name": "fecha_nacimiento",
  "display_name": "Fecha de Nacimiento",
  "type": "date",
  "description": "Fecha de nacimiento del contacto",
  "required": false,
  "validation": {
    "min_date": "1900-01-01",
    "max_date": "2010-12-31"
  },
  "created_at": "2024-01-15T10:30:00Z"
}
```

#### Tipos de Atributos Soportados

| Tipo | Descripción | Ejemplo |
|------|-------------|---------|
| `string` | Texto libre | "Juan Pérez" |
| `number` | Número entero o decimal | 25, 99.99 |
| `boolean` | Verdadero/Falso | true, false |
| `date` | Fecha ISO 8601 | "2024-01-15" |
| `datetime` | Fecha y hora | "2024-01-15T10:30:00Z" |
| `email` | Dirección de email | "usuario@ejemplo.com" |
| `phone` | Número telefónico | "+5215512345678" |
| `url` | URL válida | "https://ejemplo.com" |
| `enum` | Lista de valores | ["opcion1", "opcion2"] |
| `json` | Objeto JSON | {"key": "value"} |

#### Obtener Definición de Atributo

**GET** `/v1/attributes/{attribute_id}`

#### Listar Definiciones de Atributos

**GET** `/v1/attributes`

#### Actualizar Definición de Atributo

**PATCH** `/v1/attributes/{attribute_id}`

#### Eliminar Definición de Atributo

**DELETE** `/v1/attributes/{attribute_id}`

### 4. Listas de Contactos

#### Crear Lista

**POST** `/v1/contact-lists`

```json
{
  "name": "Clientes VIP 2024",
  "description": "Lista de clientes VIP para campaña 2024",
  "type": "static",
  "criteria": {
    "tags": ["cliente_vip"],
    "attributes": {
      "status": "active",
      "tier": "premium"
    }
  },
  "metadata": {
    "campaign": "q1_2024",
    "owner": "marketing_team"
  }
}
```

**Respuesta:**
```json
{
  "id": "list_789",
  "name": "Clientes VIP 2024",
  "description": "Lista de clientes VIP para campaña 2024",
  "type": "static",
  "contact_count": 0,
  "created_at": "2024-01-15T10:30:00Z",
  "updated_at": "2024-01-15T10:30:00Z"
}
```

#### Tipos de Lista

- **static**: Lista manual, contactos agregados explícitamente
- **dynamic**: Lista automática basada en criterios
- **smart**: Lista que se actualiza automáticamente

#### Agregar Contactos a Lista

**POST** `/v1/contact-lists/{list_id}/contacts`

```json
{
  "contact_ids": [
    "contact_123456",
    "contact_789012",
    "contact_345678"
  ]
}
```

#### Agregar por Criterios (Listas Dinámicas)

```json
{
  "criteria": {
    "tags": ["nuevo_cliente"],
    "attributes": {
      "created_after": "2024-01-01",
      "source": "website"
    }
  }
}
```

#### Listar Contactos en Lista

**GET** `/v1/contact-lists/{list_id}/contacts`

#### Eliminar Contactos de Lista

**DELETE** `/v1/contact-lists/{list_id}/contacts`

```json
{
  "contact_ids": ["contact_123456"]
}
```

#### Obtener Información de Lista

**GET** `/v1/contact-lists/{list_id}`

#### Listar Todas las Listas

**GET** `/v1/contact-lists`

#### Actualizar Lista

**PATCH** `/v1/contact-lists/{list_id}`

#### Eliminar Lista

**DELETE** `/v1/contact-lists/{list_id}`

### 5. Eventos de Contacto

#### Registrar Evento

**POST** `/v1/contacts/{contact_id}/events`

```json
{
  "type": "page_view",
  "properties": {
    "url": "https://ejemplo.com/productos",
    "page_title": "Catálogo de Productos",
    "referrer": "google.com",
    "session_id": "sess_123456"
  },
  "timestamp": "2024-01-15T10:30:00Z",
  "metadata": {
    "user_agent": "Mozilla/5.0...",
    "ip_address": "192.168.1.1"
  }
}
```

**Respuesta:**
```json
{
  "id": "event_001",
  "contact_id": "contact_123456",
  "type": "page_view",
  "properties": {
    "url": "https://ejemplo.com/productos",
    "page_title": "Catálogo de Productos"
  },
  "timestamp": "2024-01-15T10:30:00Z",
  "created_at": "2024-01-15T10:30:00Z"
}
```

#### Tipos de Eventos Comunes

| Tipo | Descripción | Propiedades Comunes |
|------|-------------|---------------------|
| `page_view` | Vista de página web | url, page_title, referrer |
| `form_submit` | Envío de formulario | form_id, form_name, fields |
| `email_open` | Apertura de email | campaign_id, subject |
| `email_click` | Click en email | url, link_text, campaign_id |
| `purchase` | Compra realizada | amount, currency, products |
| `login` | Inicio de sesión | platform, method |
| `download` | Descarga de archivo | file_name, file_type, file_url |
| `video_play` | Reproducción de video | video_id, duration, position |
| `custom` | Evento personalizado | Propiedades definidas por usuario |

#### Listar Eventos de Contacto

**GET** `/v1/contacts/{contact_id}/events`

```bash
curl -X GET "https://api.bird.com/v1/contacts/contact_123456/events?type=purchase&limit=10&order=desc" \
  -H "Authorization: Bearer YOUR_API_TOKEN"
```

#### Obtener Evento Específico

**GET** `/v1/contacts/{contact_id}/events/{event_id}`

## Operaciones en Lote

### Crear Múltiples Contactos

**POST** `/v1/contacts/batch`

```json
{
  "contacts": [
    {
      "identifiers": [{"type": "email", "value": "usuario1@ejemplo.com"}],
      "attributes": {"firstName": "María", "lastName": "González"}
    },
    {
      "identifiers": [{"type": "phone", "value": "+5215587654321"}],
      "attributes": {"firstName": "Carlos", "lastName": "Rodríguez"}
    }
  ],
  "options": {
    "update_if_exists": true,
    "skip_validation": false
  }
}
```

**Respuesta:**
```json
{
  "results": [
    {
      "index": 0,
      "status": "created",
      "contact": {
        "id": "contact_111111",
        "identifiers": [{"type": "email", "value": "usuario1@ejemplo.com"}]
      }
    },
    {
      "index": 1,
      "status": "updated",
      "contact": {
        "id": "contact_222222",
        "identifiers": [{"type": "phone", "value": "+5215587654321"}]
      }
    }
  ],
  "summary": {
    "total": 2,
    "created": 1,
    "updated": 1,
    "failed": 0
  }
}
```

### Actualizar Múltiples Contactos

**PATCH** `/v1/contacts/batch`

```json
{
  "updates": [
    {
      "contact_id": "contact_123456",
      "attributes": {"status": "inactive"},
      "tags": ["ex_cliente"]
    }
  ]
}
```

### Eliminar Múltiples Contactos

**DELETE** `/v1/contacts/batch`

```json
{
  "contact_ids": ["contact_123456", "contact_789012"]
}
```

## Búsqueda Avanzada

### Búsqueda por Criterios

**POST** `/v1/contacts/search`

```json
{
  "filters": {
    "attributes": {
      "firstName": "Juan",
      "company": "Empresa*",
      "created_after": "2024-01-01"
    },
    "tags": ["cliente_vip", "comercial"],
    "identifiers": {
      "email": "*@empresa.com"
    },
    "activity": {
      "last_activity_after": "2023-12-01",
      "event_types": ["purchase", "email_open"]
    }
  },
  "sort": [
    {"field": "last_activity", "order": "desc"},
    {"field": "created_at", "order": "asc"}
  ],
  "limit": 100
}
```

**Operadores de Búsqueda:**

| Operador | Descripción | Ejemplo |
|----------|-------------|---------|
| `*` | Wildcard | "Juan*" (empieza con Juan) |
| `?` | Carácter único | "J?an" (Juan, Joan) |
| `>`, `<` | Comparación numérica | `{"age": {"$gt": 18}}` |
| `>=`, `<=` | Comparación inclusiva | `{"score": {"$gte": 90}}` |
| `in` | Dentro de lista | `{"city": {"$in": ["CDMX", "GDL"]}}` |
| `not` | Negación | `{"status": {"$not": "inactive"}}` |
| `exists` | Campo existe | `{"phone": {"$exists": true}}` |
| `regex` | Expresión regular | `{"email": {"$regex": ".*@empresa\\.com$"}}` |

## Ejemplos de Implementación

### Python - Gestor de Contactos

```python
import requests
import json
from datetime import datetime, timedelta

class BirdContactsAPI:
    def __init__(self, api_token):
        self.api_token = api_token
        self.base_url = "https://api.bird.com/v1"
        self.headers = {
            'Authorization': f'Bearer {api_token}',
            'Content-Type': 'application/json'
        }
    
    def create_contact(self, identifiers, attributes=None, tags=None, source=None):
        """Crear nuevo contacto"""
        data = {
            "identifiers": identifiers,
            "attributes": attributes or {},
            "tags": tags or [],
            "source": source
        }
        
        response = requests.post(
            f"{self.base_url}/contacts",
            headers=self.headers,
            json=data
        )
        
        return response.json()
    
    def find_contact_by_email(self, email):
        """Buscar contacto por email"""
        response = requests.get(
            f"{self.base_url}/contacts/search",
            headers=self.headers,
            params={
                'identifier_type': 'email',
                'identifier_value': email
            }
        )
        
        return response.json()
    
    def update_contact_attributes(self, contact_id, attributes):
        """Actualizar atributos de contacto"""
        data = {"attributes": attributes}
        
        response = requests.patch(
            f"{self.base_url}/contacts/{contact_id}",
            headers=self.headers,
            json=data
        )
        
        return response.json()
    
    def add_contact_to_list(self, list_id, contact_ids):
        """Agregar contactos a lista"""
        data = {"contact_ids": contact_ids}
        
        response = requests.post(
            f"{self.base_url}/contact-lists/{list_id}/contacts",
            headers=self.headers,
            json=data
        )
        
        return response.json()
    
    def track_event(self, contact_id, event_type, properties=None, timestamp=None):
        """Registrar evento de contacto"""
        data = {
            "type": event_type,
            "properties": properties or {},
            "timestamp": timestamp or datetime.now().isoformat()
        }
        
        response = requests.post(
            f"{self.base_url}/contacts/{contact_id}/events",
            headers=self.headers,
            json=data
        )
        
        return response.json()
    
    def create_smart_list(self, name, criteria, description=None):
        """Crear lista inteligente"""
        data = {
            "name": name,
            "description": description,
            "type": "smart",
            "criteria": criteria
        }
        
        response = requests.post(
            f"{self.base_url}/contact-lists",
            headers=self.headers,
            json=data
        )
        
        return response.json()
    
    def advanced_search(self, filters, sort=None, limit=100):
        """Búsqueda avanzada de contactos"""
        data = {
            "filters": filters,
            "sort": sort or [{"field": "created_at", "order": "desc"}],
            "limit": limit
        }
        
        response = requests.post(
            f"{self.base_url}/contacts/search",
            headers=self.headers,
            json=data
        )
        
        return response.json()

# Ejemplo de uso completo
class CustomerManager:
    def __init__(self, api_token):
        self.contacts = BirdContactsAPI(api_token)
    
    def onboard_customer(self, email, phone, first_name, last_name, company=None):
        """Proceso completo de onboarding"""
        
        # 1. Verificar si el contacto ya existe
        existing = self.contacts.find_contact_by_email(email)
        
        if existing.get('contact'):
            contact_id = existing['contact']['id']
            print(f"Cliente existente encontrado: {contact_id}")
        else:
            # 2. Crear nuevo contacto
            identifiers = [
                {"type": "email", "value": email, "primary": True},
                {"type": "phone", "value": phone}
            ]
            
            attributes = {
                "firstName": first_name,
                "lastName": last_name,
                "company": company,
                "onboarded_at": datetime.now().isoformat(),
                "status": "active"
            }
            
            contact = self.contacts.create_contact(
                identifiers=identifiers,
                attributes=attributes,
                tags=["nuevo_cliente"],
                source="onboarding_api"
            )
            
            contact_id = contact['id']
            print(f"Nuevo cliente creado: {contact_id}")
        
        # 3. Registrar evento de onboarding
        self.contacts.track_event(
            contact_id=contact_id,
            event_type="customer_onboarded",
            properties={
                "onboarding_method": "api",
                "company": company,
                "source": "registration_form"
            }
        )
        
        # 4. Agregar a lista de nuevos clientes
        new_customers_list = "list_new_customers_2024"
        self.contacts.add_contact_to_list(new_customers_list, [contact_id])
        
        return contact_id
    
    def segment_customers_by_activity(self):
        """Segmentar clientes por actividad"""
        
        # Clientes activos (actividad en últimos 30 días)
        active_customers = self.contacts.advanced_search({
            "activity": {
                "last_activity_after": (datetime.now() - timedelta(days=30)).isoformat()
            },
            "attributes": {
                "status": "active"
            }
        })
        
        # Clientes inactivos (sin actividad en 90+ días)
        inactive_customers = self.contacts.advanced_search({
            "activity": {
                "last_activity_before": (datetime.now() - timedelta(days=90)).isoformat()
            },
            "attributes": {
                "status": "active"
            }
        })
        
        # Crear listas inteligentes
        self.contacts.create_smart_list(
            name="Clientes Activos",
            criteria={
                "activity": {
                    "last_activity_after": (datetime.now() - timedelta(days=30)).isoformat()
                }
            },
            description="Clientes con actividad en los últimos 30 días"
        )
        
        return {
            "active": len(active_customers.get('contacts', [])),
            "inactive": len(inactive_customers.get('contacts', []))
        }

# Uso
manager = CustomerManager("your_api_token")
customer_id = manager.onboard_customer(
    email="nuevo@cliente.com",
    phone="+5215512345678",
    first_name="Ana",
    last_name="Martínez",
    company="Startup Tech"
)

segmentation = manager.segment_customers_by_activity()
print(f"Segmentación: {segmentation}")
```

### JavaScript - Sistema de CRM

```javascript
class BirdCRM {
    constructor(apiToken) {
        this.apiToken = apiToken;
        this.baseURL = 'https://api.bird.com/v1';
        this.headers = {
            'Authorization': `Bearer ${apiToken}`,
            'Content-Type': 'application/json'
        };
    }
    
    async createLead(leadData) {
        const contact = await this.createContact({
            identifiers: [
                { type: 'email', value: leadData.email, primary: true }
            ],
            attributes: {
                firstName: leadData.firstName,
                lastName: leadData.lastName,
                company: leadData.company,
                leadScore: leadData.score || 0,
                leadSource: leadData.source,
                status: 'lead'
            },
            tags: ['lead', leadData.source],
            source: 'crm_system'
        });
        
        // Registrar evento de nuevo lead
        await this.trackEvent(contact.id, 'lead_created', {
            source: leadData.source,
            score: leadData.score,
            campaign: leadData.campaign
        });
        
        return contact;
    }
    
    async convertLeadToCustomer(contactId, dealValue = 0) {
        // Actualizar status y agregar datos de conversión
        const updated = await this.updateContact(contactId, {
            attributes: {
                status: 'customer',
                customerSince: new Date().toISOString(),
                lifetimeValue: dealValue
            },
            tags: ['customer', 'converted']
        });
        
        // Registrar conversión
        await this.trackEvent(contactId, 'lead_converted', {
            dealValue: dealValue,
            conversionDate: new Date().toISOString()
        });
        
        // Mover a lista de clientes
        await this.addToList('customers_list', [contactId]);
        await this.removeFromList('leads_list', [contactId]);
        
        return updated;
    }
    
    async createNurtureSequence(listId, sequenceType = 'email_course') {
        const contacts = await this.getListContacts(listId);
        
        for (const contact of contacts) {
            // Personalizar secuencia basada en atributos
            const sequence = this.buildSequenceForContact(contact, sequenceType);
            
            // Programar eventos de nurturing
            for (let i = 0; i < sequence.length; i++) {
                setTimeout(async () => {
                    await this.trackEvent(contact.id, 'nurture_step', {
                        step: i + 1,
                        content: sequence[i].content,
                        sequenceType: sequenceType
                    });
                }, sequence[i].delay * 1000);
            }
        }
    }
    
    async getCustomerInsights(contactId) {
        // Obtener eventos del contacto
        const events = await this.getContactEvents(contactId);
        const contact = await this.getContact(contactId);
        
        // Calcular métricas
        const insights = {
            totalInteractions: events.length,
            lastActivity: events[0]?.timestamp,
            engagementScore: this.calculateEngagementScore(events),
            preferredChannels: this.analyzeChannelPreference(events),
            customerJourney: this.mapCustomerJourney(events),
            recommendations: this.generateRecommendations(contact, events)
        };
        
        return insights;
    }
    
    // Métodos auxiliares de la API
    async createContact(data) {
        const response = await fetch(`${this.baseURL}/contacts`, {
            method: 'POST',
            headers: this.headers,
            body: JSON.stringify(data)
        });
        return await response.json();
    }
    
    async getContact(contactId) {
        const response = await fetch(`${this.baseURL}/contacts/${contactId}`, {
            headers: this.headers
        });
        return await response.json();
    }
    
    async updateContact(contactId, data) {
        const response = await fetch(`${this.baseURL}/contacts/${contactId}`, {
            method: 'PATCH',
            headers: this.headers,
            body: JSON.stringify(data)
        });
        return await response.json();
    }
    
    async trackEvent(contactId, eventType, properties) {
        const response = await fetch(`${this.baseURL}/contacts/${contactId}/events`, {
            method: 'POST',
            headers: this.headers,
            body: JSON.stringify({
                type: eventType,
                properties: properties,
                timestamp: new Date().toISOString()
            })
        });
        return await response.json();
    }
    
    async getContactEvents(contactId, limit = 100) {
        const response = await fetch(
            `${this.baseURL}/contacts/${contactId}/events?limit=${limit}&order=desc`,
            { headers: this.headers }
        );
        const data = await response.json();
        return data.events || [];
    }
    
    // Métodos de análisis
    calculateEngagementScore(events) {
        const weights = {
            'email_open': 1,
            'email_click': 3,
            'page_view': 2,
            'form_submit': 5,
            'purchase': 10
        };
        
        return events.reduce((score, event) => {
            return score + (weights[event.type] || 0);
        }, 0);
    }
    
    analyzeChannelPreference(events) {
        const channels = {};
        events.forEach(event => {
            const channel = event.properties?.channel || 'unknown';
            channels[channel] = (channels[channel] || 0) + 1;
        });
        
        return Object.entries(channels)
            .sort(([,a], [,b]) => b - a)
            .map(([channel, count]) => ({ channel, count }));
    }
    
    mapCustomerJourney(events) {
        return events
            .filter(event => ['lead_created', 'email_open', 'page_view', 'purchase', 'lead_converted'].includes(event.type))
            .map(event => ({
                stage: this.getJourneyStage(event.type),
                timestamp: event.timestamp,
                details: event.properties
            }));
    }
    
    getJourneyStage(eventType) {
        const stageMap = {
            'lead_created': 'Awareness',
            'email_open': 'Interest',
            'page_view': 'Consideration',
            'form_submit': 'Intent',
            'purchase': 'Purchase',
            'lead_converted': 'Loyalty'
        };
        return stageMap[eventType] || 'Other';
    }
}

// Uso del sistema CRM
const crm = new BirdCRM('your_api_token');

// Crear nuevo lead
const lead = await crm.createLead({
    email: 'prospecto@empresa.com',
    firstName: 'María',
    lastName: 'González',
    company: 'TechCorp',
    source: 'webinar',
    score: 75,
    campaign: 'Q1_2024_Webinar'
});

// Obtener insights del cliente
const insights = await crm.getCustomerInsights(lead.id);
console.log('Customer Insights:', insights);
```

## Webhooks para Contactos

### Eventos Disponibles

| Evento | Descripción | Payload |
|--------|-------------|---------|
| `contact.created` | Contacto creado | Datos completos del contacto |
| `contact.updated` | Contacto actualizado | Campos modificados |
| `contact.deleted` | Contacto eliminado | ID del contacto |
| `contact.identifier.added` | Identificador agregado | Nuevo identificador |
| `contact.identifier.verified` | Identificador verificado | Estado de verificación |
| `contact.event.tracked` | Evento registrado | Datos del evento |
| `contact.list.added` | Agregado a lista | Contacto y lista |
| `contact.list.removed` | Removido de lista | Contacto y lista |

### Ejemplo de Webhook

```json
{
  "event": "contact.updated",
  "timestamp": "2024-01-15T10:35:00Z",
  "contact": {
    "id": "contact_123456",
    "identifiers": [
      {
        "type": "email",
        "value": "juan.perez@ejemplo.com"
      }
    ],
    "attributes": {
      "firstName": "Juan",
      "lastName": "Pérez",
      "status": "active"
    },
    "changes": {
      "attributes": {
        "status": {
          "from": "lead",
          "to": "active"
        }
      },
      "tags": {
        "added": ["customer"],
        "removed": ["lead"]
      }
    }
  }
}
```

## Mejores Prácticas

### 1. Normalización de Datos

```python
def normalize_contact_data(raw_data):
    """Normalizar datos de contacto antes de crear"""
    normalized = {}
    
    # Normalizar nombres
    if raw_data.get('first_name'):
        normalized['firstName'] = raw_data['first_name'].title().strip()
    
    if raw_data.get('last_name'):
        normalized['lastName'] = raw_data['last_name'].title().strip()
    
    # Normalizar email
    if raw_data.get('email'):
        normalized['email'] = raw_data['email'].lower().strip()
    
    # Normalizar teléfono
    if raw_data.get('phone'):
        normalized['phone'] = normalize_phone_number(raw_data['phone'])
    
    return normalized

def normalize_phone_number(phone):
    """Normalizar número telefónico a formato E.164"""
    # Implementar lógica de normalización
    import re
    
    # Remover caracteres no numéricos
    digits_only = re.sub(r'[^\d+]', '', phone)
    
    # Agregar código de país si no está presente
    if not digits_only.startswith('+'):
        if len(digits_only) == 10:  # Número mexicano
            digits_only = '+52' + digits_only
    
    return digits_only
```

### 2. Deduplicación Inteligente

```python
def find_duplicates(new_contact):
    """Buscar posibles duplicados antes de crear contacto"""
    potential_duplicates = []
    
    # Buscar por email exacto
    if new_contact.get('email'):
        email_match = api.find_contact_by_email(new_contact['email'])
        if email_match.get('contact'):
            potential_duplicates.append({
                'match_type': 'email_exact',
                'confidence': 1.0,
                'contact': email_match['contact']
            })
    
    # Buscar por nombre y empresa
    if new_contact.get('first_name') and new_contact.get('company'):
        name_company_search = api.advanced_search({
            "filters": {
                "attributes": {
                    "firstName": new_contact['first_name'],
                    "company": new_contact['company']
                }
            }
        })
        
        for contact in name_company_search.get('contacts', []):
            potential_duplicates.append({
                'match_type': 'name_company',
                'confidence': 0.8,
                'contact': contact
            })
    
    return potential_duplicates

def merge_contacts(primary_id, duplicate_id):
    """Fusionar contactos duplicados"""
    # Obtener ambos contactos
    primary = api.get_contact(primary_id)
    duplicate = api.get_contact(duplicate_id)
    
    # Combinar identificadores
    merged_identifiers = primary['identifiers'].copy()
    for ident in duplicate['identifiers']:
        if not any(i['value'] == ident['value'] for i in merged_identifiers):
            merged_identifiers.append(ident)
    
    # Combinar atributos (preferir datos más recientes)
    merged_attributes = {**duplicate['attributes'], **primary['attributes']}
    
    # Combinar tags
    merged_tags = list(set(primary.get('tags', []) + duplicate.get('tags', [])))
    
    # Actualizar contacto principal
    api.update_contact(primary_id, {
        'identifiers': merged_identifiers,
        'attributes': merged_attributes,
        'tags': merged_tags
    })
    
    # Transferir eventos del duplicado al principal
    duplicate_events = api.get_contact_events(duplicate_id)
    for event in duplicate_events:
        api.track_event(primary_id, event['type'], event['properties'])
    
    # Eliminar duplicado
    api.delete_contact(duplicate_id)
    
    return primary_id
```

### 3. Segmentación Dinámica

```python
def create_behavioral_segments():
    """Crear segmentos basados en comportamiento"""
    
    segments = [
        {
            'name': 'High Value Prospects',
            'criteria': {
                'attributes': {
                    'leadScore': {'$gte': 80}
                },
                'activity': {
                    'event_types': ['form_submit', 'demo_request'],
                    'frequency': {'$gte': 3}
                }
            }
        },
        {
            'name': 'Engaged Email Subscribers',
            'criteria': {
                'activity': {
                    'event_types': ['email_open', 'email_click'],
                    'last_activity_after': '2024-01-01'
                },
                'tags': ['email_subscriber']
            }
        },
        {
            'name': 'At Risk Customers',
            'criteria': {
                'attributes': {
                    'status': 'customer'
                },
                'activity': {
                    'last_activity_before': '2023-10-01'
                }
            }
        }
    ]
    
    created_segments = []
    for segment in segments:
        list_id = api.create_smart_list(
            name=segment['name'],
            criteria=segment['criteria'],
            description=f"Auto-generated segment: {segment['name']}"
        )
        created_segments.append(list_id)
    
    return created_segments
```

## Limitaciones y Consideraciones

### 1. Límites de la API
- **Contactos por workspace**: 1,000,000 contactos
- **Identificadores por contacto**: 10 identificadores máximo
- **Atributos personalizados**: 50 definiciones máximo
- **Listas por contacto**: 100 listas máximo
- **Eventos por contacto**: 100,000 eventos máximo

### 2. Rate Limiting
- **Operaciones individuales**: 1000 requests/minute
- **Operaciones en lote**: 100 requests/minute
- **Búsquedas complejas**: 50 requests/minute
- **Tracking de eventos**: 500 requests/minute

### 3. Retención de Datos
- **Contactos activos**: Sin límite de tiempo
- **Contactos eliminados**: Backup por 30 días
- **Eventos**: 2 años de retención
- **Listas eliminadas**: Backup por 7 días

### 4. Validación de Datos
- **Email**: Validación de formato RFC 5322
- **Teléfono**: Formato E.164 requerido
- **URLs**: Validación HTTP/HTTPS
- **Fechas**: Formato ISO 8601

## Códigos de Error Específicos

| Código | Error | Descripción |
|--------|-------|-------------|
| `3001` | Contact Not Found | Contacto no existe |
| `3002` | Duplicate Identifier | Identificador ya existe |
| `3003` | Invalid Attribute | Atributo no válido o no existe |
| `3004` | Contact Limit Exceeded | Límite de contactos excedido |
| `3005` | List Not Found | Lista no existe |
| `3006` | Invalid Search Criteria | Criterios de búsqueda inválidos |
| `3007` | Batch Size Exceeded | Lote excede tamaño máximo |
| `3008` | Event Limit Exceeded | Límite de eventos excedido |

## Recursos Relacionados

- [Channels API](../channels/README.md) - Para mensajería a contactos
- [Conversations API](../conversations/README.md) - Para historial de conversaciones  
- [Webhooks](../webhooks.md) - Eventos de contacto en tiempo real
- [Authentication](../authentication.md) - Configuración de acceso
- [Code Examples](../code-examples/contacts/) - Ejemplos completos

---

La Contacts API es fundamental para construir una base de datos robusta de clientes y permitir segmentación avanzada, personalización y seguimiento del customer journey completo.