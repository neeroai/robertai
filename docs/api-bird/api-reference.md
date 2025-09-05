# Bird.com AI Employees API Reference

## Overview

The Bird.com AI Employees API enables developers to programmatically manage AI-powered conversational agents that can handle customer interactions across multiple channels, primarily WhatsApp Business API. This comprehensive reference provides technical details for integrating with Bird.com's platform.

## Base URLs

```
Production: https://api.bird.com/v1
Sandbox: https://sandbox-api.bird.com/v1
```

## Authentication

### API Key Authentication

All API requests require authentication using your API key in the Authorization header:

```bash
curl -H "Authorization: Bearer YOUR_API_KEY" \
     -H "Content-Type: application/json" \
     https://api.bird.com/v1/ai-employees
```

### HMAC Signature Verification (Webhooks)

For webhook security, Bird.com signs requests with HMAC-SHA256:

```javascript
const crypto = require('crypto');

function verifyWebhookSignature(payload, signature, secret) {
  const expectedSignature = crypto
    .createHmac('sha256', secret)
    .update(payload)
    .digest('hex');
  
  return signature === `sha256=${expectedSignature}`;
}
```

## Core API Endpoints

### AI Employees Management

#### List AI Employees

```http
GET /v1/ai-employees
```

**Parameters:**
- `page` (optional): Page number for pagination (default: 1)
- `limit` (optional): Items per page (default: 20, max: 100)
- `status` (optional): Filter by status (`active`, `inactive`, `training`)

**Response:**

```json
{
  "data": [
    {
      "id": "ai_employee_123",
      "name": "Customer Support Agent",
      "description": "Handles customer inquiries and support tickets",
      "status": "active",
      "channel": "whatsapp",
      "knowledge_base_id": "kb_456",
      "personality_config": {
        "tone": "professional",
        "language": "es",
        "response_style": "helpful"
      },
      "created_at": "2024-01-15T10:30:00Z",
      "updated_at": "2024-01-20T14:45:00Z"
    }
  ],
  "pagination": {
    "current_page": 1,
    "total_pages": 5,
    "total_items": 87,
    "per_page": 20
  }
}
```

#### Create AI Employee

```http
POST /v1/ai-employees
```

**Request Body:**

```json
{
  "name": "Sales Assistant",
  "description": "Assists with product inquiries and sales",
  "channel": "whatsapp",
  "knowledge_base_id": "kb_789",
  "personality_config": {
    "tone": "friendly",
    "language": "es",
    "response_style": "conversational",
    "max_response_length": 500
  },
  "llm_config": {
    "provider": "openai",
    "model": "gpt-4",
    "temperature": 0.7,
    "max_tokens": 1000
  }
}
```

**Response (201 Created):**

```json
{
  "id": "ai_employee_789",
  "name": "Sales Assistant",
  "description": "Assists with product inquiries and sales",
  "status": "training",
  "channel": "whatsapp",
  "knowledge_base_id": "kb_789",
  "personality_config": {
    "tone": "friendly",
    "language": "es",
    "response_style": "conversational",
    "max_response_length": 500
  },
  "llm_config": {
    "provider": "openai",
    "model": "gpt-4",
    "temperature": 0.7,
    "max_tokens": 1000
  },
  "created_at": "2024-01-25T09:15:00Z",
  "updated_at": "2024-01-25T09:15:00Z"
}
```

#### Update AI Employee

```http
PUT /v1/ai-employees/{id}
```

#### Delete AI Employee

```http
DELETE /v1/ai-employees/{id}
```

### Knowledge Base Management

#### Create Knowledge Base

```http
POST /v1/knowledge-bases
```

**Request Body:**

```json
{
  "name": "Product Documentation",
  "description": "Comprehensive product information and FAQs",
  "language": "es",
  "documents": [
    {
      "title": "Guía de Productos",
      "content": "Información detallada sobre nuestros productos...",
      "type": "text",
      "metadata": {
        "category": "products",
        "version": "1.0"
      }
    }
  ]
}
```

#### Upload Document to Knowledge Base

```http
POST /v1/knowledge-bases/{id}/documents
```

**Multipart Form Data:**
- `file`: Document file (PDF, DOC, TXT)
- `title`: Document title
- `category`: Document category
- `metadata`: Additional metadata (JSON)

```bash
curl -X POST \
  -H "Authorization: Bearer YOUR_API_KEY" \
  -F "file=@product-guide.pdf" \
  -F "title=Guía de Productos 2024" \
  -F "category=products" \
  -F 'metadata={"version":"2.0","department":"sales"}' \
  https://api.bird.com/v1/knowledge-bases/kb_123/documents
```

### Conversation Management

#### Send Message

```http
POST /v1/conversations/{conversation_id}/messages
```

**Request Body:**

```json
{
  "type": "text",
  "content": "¿Cuáles son los precios de sus productos?",
  "sender": {
    "type": "customer",
    "phone": "+34612345678",
    "name": "María González"
  },
  "ai_employee_id": "ai_employee_123"
}
```

**Response:**

```json
{
  "message_id": "msg_456",
  "conversation_id": "conv_789",
  "ai_response": {
    "type": "text",
    "content": "¡Hola María! Me complace ayudarte con información sobre nuestros precios. Tenemos diferentes categorías de productos...",
    "confidence_score": 0.95,
    "response_time_ms": 450
  },
  "created_at": "2024-01-25T10:30:00Z"
}
```

#### Get Conversation History

```http
GET /v1/conversations/{conversation_id}/messages
```

### AI Actions and Integrations

#### Create AI Action

```http
POST /v1/ai-actions
```

**Request Body:**

```json
{
  "name": "create_support_ticket",
  "description": "Creates a support ticket in the CRM system",
  "type": "webhook",
  "config": {
    "webhook_url": "https://your-api.com/tickets",
    "method": "POST",
    "headers": {
      "Authorization": "Bearer YOUR_CRM_TOKEN",
      "Content-Type": "application/json"
    },
    "payload_template": {
      "title": "{{issue_summary}}",
      "description": "{{customer_message}}",
      "customer_phone": "{{customer.phone}}",
      "priority": "{{priority|default:medium}}"
    }
  },
  "trigger_conditions": [
    {
      "intent": "create_ticket",
      "confidence_threshold": 0.8
    }
  ]
}
```

#### Execute AI Action

```http
POST /v1/ai-actions/{action_id}/execute
```

## Webhook Events

### Webhook Configuration

Configure webhook endpoints to receive real-time events:

```http
POST /v1/webhooks
```

**Request Body:**

```json
{
  "url": "https://your-app.com/webhooks/bird",
  "events": [
    "message.received",
    "message.sent",
    "conversation.started",
    "ai_employee.response_generated"
  ],
  "secret": "your_webhook_secret_key"
}
```

### Event Types

#### Message Received

```json
{
  "event": "message.received",
  "timestamp": "2024-01-25T10:30:00Z",
  "data": {
    "conversation_id": "conv_123",
    "message_id": "msg_456",
    "sender": {
      "phone": "+34612345678",
      "name": "María González"
    },
    "content": "Necesito ayuda con mi pedido",
    "channel": "whatsapp"
  }
}
```

#### AI Response Generated

```json
{
  "event": "ai_employee.response_generated",
  "timestamp": "2024-01-25T10:30:15Z",
  "data": {
    "ai_employee_id": "ai_employee_123",
    "conversation_id": "conv_123",
    "response": {
      "content": "¡Por supuesto! Estaré encantado de ayudarte con tu pedido...",
      "confidence_score": 0.92,
      "response_time_ms": 380,
      "knowledge_sources": ["kb_doc_789", "kb_doc_234"]
    }
  }
}
```

## Integration with KOAJ API

### KOAJ Endpoints Integration

Bird.com integrates with KOAJ API for enhanced functionality:

```javascript
// KOAJ API Integration Example
const koajClient = {
  baseURL: 'https://api.neero.link/v1',
  
  async processCustomerQuery(query, context) {
    const response = await fetch(`${this.baseURL}/process`, {
      method: 'POST',
      headers: {
        'Authorization': 'Bearer YOUR_KOAJ_TOKEN',
        'Content-Type': 'application/json'
      },
      body: JSON.stringify({
        query,
        context,
        bird_integration: true
      })
    });
    
    return response.json();
  }
};
```

## Error Handling

### HTTP Status Codes

- `200` - OK
- `201` - Created
- `400` - Bad Request
- `401` - Unauthorized
- `403` - Forbidden
- `404` - Not Found
- `429` - Rate Limit Exceeded
- `500` - Internal Server Error

### Error Response Format

```json
{
  "error": {
    "code": "INVALID_REQUEST",
    "message": "The request body contains invalid parameters",
    "details": [
      {
        "field": "personality_config.language",
        "message": "Supported languages are: es, en, fr, de"
      }
    ],
    "request_id": "req_123456789"
  }
}
```

## Rate Limiting

- **Standard Plan**: 1000 requests/hour
- **Premium Plan**: 5000 requests/hour
- **Enterprise Plan**: Custom limits

Rate limit headers are included in all responses:

```
X-RateLimit-Limit: 1000
X-RateLimit-Remaining: 847
X-RateLimit-Reset: 1640995200
```

## SDK Examples

### Python SDK

```python
from bird_ai import BirdClient

client = BirdClient(api_key='your_api_key')

# Create AI Employee
ai_employee = client.ai_employees.create(
    name="Customer Support",
    channel="whatsapp",
    knowledge_base_id="kb_123",
    personality_config={
        "tone": "professional",
        "language": "es"
    }
)

# Send message and get AI response
response = client.conversations.send_message(
    conversation_id="conv_123",
    content="¿Cómo puedo hacer un pedido?",
    ai_employee_id=ai_employee.id
)

print(f"AI Response: {response.ai_response.content}")
```

### JavaScript SDK

```javascript
import { BirdClient } from '@bird/ai-sdk';

const client = new BirdClient({ apiKey: 'your_api_key' });

// Create knowledge base with documents
const kb = await client.knowledgeBases.create({
  name: 'Product Catalog',
  language: 'es',
  documents: [
    {
      title: 'Catálogo de Productos',
      content: 'Lista completa de productos disponibles...',
      type: 'text'
    }
  ]
});

// Set up webhook listener
client.webhooks.on('message.received', async (event) => {
  console.log(`New message: ${event.data.content}`);
  
  // Process with AI Employee
  const response = await client.conversations.sendMessage({
    conversationId: event.data.conversation_id,
    content: event.data.content,
    aiEmployeeId: 'ai_employee_123'
  });
  
  console.log(`AI Response: ${response.aiResponse.content}`);
});
```

## Best Practices

### 1. Conversation Context Management

```javascript
// Maintain conversation context for better responses
const contextManager = {
  conversations: new Map(),
  
  updateContext(conversationId, message, response) {
    const context = this.conversations.get(conversationId) || [];
    context.push({ message, response, timestamp: Date.now() });
    
    // Keep last 10 exchanges for context
    if (context.length > 10) {
      context.shift();
    }
    
    this.conversations.set(conversationId, context);
  }
};
```

### 2. Error Handling with Retry Logic

```python
import time
import requests
from tenacity import retry, stop_after_attempt, wait_exponential

@retry(
    stop=stop_after_attempt(3),
    wait=wait_exponential(multiplier=1, min=4, max=10)
)
def send_message_with_retry(conversation_id, content):
    response = requests.post(
        f"https://api.bird.com/v1/conversations/{conversation_id}/messages",
        headers={
            "Authorization": f"Bearer {API_KEY}",
            "Content-Type": "application/json"
        },
        json={
            "type": "text",
            "content": content,
            "ai_employee_id": "ai_employee_123"
        }
    )
    
    if response.status_code == 429:
        # Rate limited - wait before retry
        time.sleep(60)
        response.raise_for_status()
    
    return response.json()
```

### 3. Knowledge Base Optimization

```python
# Optimize knowledge base with proper document structure
def optimize_knowledge_base(documents):
    optimized = []
    
    for doc in documents:
        # Split large documents into sections
        if len(doc['content']) > 2000:
            sections = split_into_sections(doc['content'])
            for i, section in enumerate(sections):
                optimized.append({
                    'title': f"{doc['title']} - Sección {i+1}",
                    'content': section,
                    'metadata': {
                        **doc.get('metadata', {}),
                        'section': i+1,
                        'parent_document': doc['title']
                    }
                })
        else:
            optimized.append(doc)
    
    return optimized
```

## Performance Monitoring

### Analytics Endpoints

```http
GET /v1/analytics/ai-employees/{id}/performance
```

**Response:**

```json
{
  "period": "last_30_days",
  "metrics": {
    "total_conversations": 1247,
    "average_response_time_ms": 420,
    "customer_satisfaction_score": 4.2,
    "resolution_rate": 0.87,
    "escalation_rate": 0.13,
    "top_intents": [
      {"intent": "product_inquiry", "count": 342},
      {"intent": "order_status", "count": 298},
      {"intent": "technical_support", "count": 187}
    ]
  }
}
```

## Troubleshooting

### Common Issues

#### 1. Low AI Confidence Scores

**Problem**: AI responses have low confidence scores (<0.7)

**Solutions**:
- Enhance knowledge base with more relevant documents
- Adjust AI Employee personality settings
- Review and improve training data quality

```python
# Check confidence scores and improve knowledge base
def improve_knowledge_base(ai_employee_id):
    # Get recent low-confidence responses
    low_confidence_responses = client.analytics.get_low_confidence_responses(
        ai_employee_id=ai_employee_id,
        confidence_threshold=0.7,
        limit=50
    )
    
    # Analyze common topics that need improvement
    topics_to_improve = analyze_topics(low_confidence_responses)
    
    # Suggest knowledge base improvements
    return suggest_knowledge_improvements(topics_to_improve)
```

#### 2. High Response Times

**Problem**: AI responses taking >2 seconds

**Solutions**:
- Optimize knowledge base size and structure
- Use appropriate LLM model for your use case
- Implement response caching for common queries

```javascript
// Implement response caching
const responseCache = new Map();

async function getCachedOrNewResponse(query, aiEmployeeId) {
  const cacheKey = `${aiEmployeeId}:${hashQuery(query)}`;
  
  if (responseCache.has(cacheKey)) {
    return responseCache.get(cacheKey);
  }
  
  const response = await client.conversations.sendMessage({
    content: query,
    aiEmployeeId: aiEmployeeId
  });
  
  // Cache responses for common queries
  if (response.confidence_score > 0.9) {
    responseCache.set(cacheKey, response);
  }
  
  return response;
}
```

## Additional Resources

- [Spanish Documentation](getting-started/introduction.md) - Comprehensive conceptual guides
- [Setup Templates](templates/) - Ready-to-use configuration templates
- [Webhook Examples](https://github.com/bird-com/webhook-examples) - Sample webhook implementations
- [Community Forum](https://community.bird.com) - Developer community and support
- [Status Page](https://status.bird.com) - API status and incident reports

---

*This API reference complements the comprehensive Spanish-language documentation in this repository. For conceptual guides and setup instructions, refer to the main documentation sections.*