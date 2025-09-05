# Developer Quick Start - Bird.com AI Employees API

⚡ **Get your AI Employee running in 5 minutes!**

## Prerequisites

- Bird.com account with API access
- API key from Bird.com dashboard
- Basic knowledge of REST APIs
- Development environment (Python/JavaScript/curl)

## Step 1: Authentication Setup

### Get Your API Key
1. Log into your Bird.com dashboard
2. Navigate to **Settings > API Keys**
3. Create a new API key with `AI Employees` permissions
4. Copy your API key (it starts with `bird_api_`)

### Test Authentication

```bash
# Test your API key
curl -H "Authorization: Bearer YOUR_API_KEY" \
     https://api.bird.com/v1/ai-employees

# Expected response: List of your AI employees (may be empty)
```

## Step 2: Create Your First Knowledge Base

```bash
curl -X POST https://api.bird.com/v1/knowledge-bases \
  -H "Authorization: Bearer YOUR_API_KEY" \
  -H "Content-Type: application/json" \
  -d '{
    "name": "Product FAQ",
    "description": "Common questions about our products",
    "language": "es",
    "documents": [
      {
        "title": "Preguntas Frecuentes",
        "content": "P: ¿Cuáles son nuestros horarios de atención?\nR: Atendemos de lunes a viernes de 9:00 AM a 6:00 PM.\n\nP: ¿Ofrecen envío gratis?\nR: Sí, ofrecemos envío gratis en compras superiores a $100.000 COP.",
        "type": "text",
        "metadata": {
          "category": "faq",
          "version": "1.0"
        }
      }
    ]
  }'
```

**Save the `knowledge_base_id` from the response - you'll need it next!**

## Step 3: Create Your AI Employee

```bash
curl -X POST https://api.bird.com/v1/ai-employees \
  -H "Authorization: Bearer YOUR_API_KEY" \
  -H "Content-Type: application/json" \
  -d '{
    "name": "Customer Support Bot",
    "description": "Handles customer inquiries and support",
    "channel": "whatsapp",
    "knowledge_base_id": "YOUR_KNOWLEDGE_BASE_ID",
    "personality_config": {
      "tone": "friendly",
      "language": "es",
      "response_style": "helpful",
      "max_response_length": 300
    },
    "llm_config": {
      "provider": "openai",
      "model": "gpt-3.5-turbo",
      "temperature": 0.7
    }
  }'
```

**Save the `ai_employee_id` from the response!**

## Step 4: Test Your AI Employee

```bash
# Send a test message
curl -X POST https://api.bird.com/v1/conversations/test_conv_123/messages \
  -H "Authorization: Bearer YOUR_API_KEY" \
  -H "Content-Type: application/json" \
  -d '{
    "type": "text",
    "content": "¿Cuáles son sus horarios de atención?",
    "sender": {
      "type": "customer",
      "phone": "+1234567890",
      "name": "Test User"
    },
    "ai_employee_id": "YOUR_AI_EMPLOYEE_ID"
  }'
```

**Expected Response:**
```json
{
  "message_id": "msg_abc123",
  "conversation_id": "test_conv_123",
  "ai_response": {
    "type": "text",
    "content": "¡Hola! Nuestros horarios de atención son de lunes a viernes de 9:00 AM a 6:00 PM. ¿En qué más puedo ayudarte?",
    "confidence_score": 0.95,
    "response_time_ms": 420
  }
}
```

## Step 5: Set Up Webhooks (Optional)

### Create Webhook Endpoint

```javascript
// Express.js example
const express = require('express');
const crypto = require('crypto');
const app = express();

app.use(express.json());

app.post('/webhooks/bird', (req, res) => {
  // Verify webhook signature
  const signature = req.headers['x-bird-signature'];
  const payload = JSON.stringify(req.body);
  
  // Process the event
  const event = req.body;
  console.log('Received event:', event.event_type);
  
  if (event.event_type === 'message.received') {
    console.log('New message:', event.data.content);
  }
  
  res.status(200).json({ received: true });
});

app.listen(3000, () => {
  console.log('Webhook server running on port 3000');
});
```

### Register Your Webhook

```bash
curl -X POST https://api.bird.com/v1/webhooks \
  -H "Authorization: Bearer YOUR_API_KEY" \
  -H "Content-Type: application/json" \
  -d '{
    "url": "https://your-app.com/webhooks/bird",
    "events": [
      "message.received",
      "message.sent",
      "ai_employee.response_generated"
    ],
    "secret": "your_webhook_secret_key"
  }'
```

## SDK Quick Start

### Python

```python
# pip install bird-ai-sdk
from bird_ai import BirdClient

client = BirdClient(api_key='your_api_key')

# Create AI Employee
ai_employee = client.ai_employees.create(
    name="Support Assistant",
    channel="whatsapp",
    knowledge_base_id="kb_123",
    personality_config={
        "tone": "professional",
        "language": "es"
    }
)

# Send message
response = client.conversations.send_message(
    conversation_id="conv_123",
    content="¿Tienen descuentos?",
    ai_employee_id=ai_employee.id
)

print(f"AI Response: {response.ai_response.content}")
```

### JavaScript

```javascript
// npm install @bird/ai-sdk
import { BirdClient } from '@bird/ai-sdk';

const client = new BirdClient({ apiKey: 'your_api_key' });

// Create AI Employee
const aiEmployee = await client.aiEmployees.create({
  name: 'Sales Assistant',
  channel: 'whatsapp',
  knowledgeBaseId: 'kb_123',
  personalityConfig: {
    tone: 'friendly',
    language: 'es'
  }
});

// Send message and get response
const response = await client.conversations.sendMessage({
  conversationId: 'conv_123',
  content: '¿Qué productos tienen disponibles?',
  aiEmployeeId: aiEmployee.id
});

console.log('AI Response:', response.aiResponse.content);
```

## Common Issues & Quick Fixes

### Issue: `401 Unauthorized`
**Fix**: Check your API key is correctly set in the `Authorization` header:
```bash
# Correct format
Authorization: Bearer bird_api_your_key_here
```

### Issue: `Low Confidence Scores (<0.7)`
**Fix**: Enhance your knowledge base with more relevant content:
```bash
# Add more documents to your knowledge base
curl -X POST https://api.bird.com/v1/knowledge-bases/YOUR_KB_ID/documents \
  -F "title=Políticas de Devolución" \
  -F "file=@returns-policy.pdf"
```

### Issue: `Slow Response Times (>2s)`
**Fix**: Use a lighter LLM model for faster responses:
```json
{
  "llm_config": {
    "provider": "openai",
    "model": "gpt-3.5-turbo",  // Faster than gpt-4
    "temperature": 0.7,
    "max_tokens": 500  // Limit response length
  }
}
```

## Next Steps

🎯 **You're ready to build!** Here's what to explore next:

1. **[📚 Full API Reference](api-reference.md)** - Complete API documentation
2. **[🔗 API Integrations](development/api-integrations.md)** - Connect external systems
3. **[🔔 Webhooks](development/webhooks.md)** - Real-time event handling
4. **[📊 Analytics](operations/monitoring.md)** - Monitor performance
5. **[🛡️ Security](operations/security.md)** - Production security

## Production Checklist

Before going live, ensure:

- [ ] **API Key Security**: Store API keys in environment variables
- [ ] **Webhook Security**: Implement signature verification  
- [ ] **Error Handling**: Add proper retry logic and error handling
- [ ] **Rate Limiting**: Respect API rate limits (1000 req/hour standard)
- [ ] **Knowledge Base**: Upload comprehensive product/service documentation
- [ ] **Testing**: Test with real user scenarios
- [ ] **Monitoring**: Set up performance monitoring and alerts

## Support

- 📚 [Complete Documentation](README.md)
- 🐛 [Report Issues](https://github.com/bird-com/support)
- 💬 [Community Forum](https://community.bird.com)
- 📧 [Developer Support](mailto:developers@bird.com)

---

**🎉 Congratulations! You now have a working Bird.com AI Employee. Happy building!**