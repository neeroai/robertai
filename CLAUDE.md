# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

**RobertAI** is a comprehensive documentation and analysis repository for Bird.com AI Employees implementation. This repository contains extensive documentation, architectural guidance, and multimodal enhancement strategies for conversational AI agents, with **WhatsApp Business API as the default and primary channel** for implementation across multiple communication platforms.

### Key Features
- Complete Bird.com AI Employee configuration documentation
- AI agent implementation guides and best practices
- Multimodal capabilities analysis and enhancement strategies
- API integration patterns for business workflows
- Conversational flow design and optimization

## Important Constraints

## Default Channel Configuration

**WhatsApp Business API** is the default and recommended channel for Bird.com AI Employee implementations. All primary features, workflows, and integrations are designed and optimized for WhatsApp Business API first, with additional channels available as secondary options.

### WhatsApp Business API Benefits
- **Native multimedia support**: 
  - Images: JPG, PNG, WebP (up to 5MB)
  - Videos: MP4, 3GPP (up to 16MB)
  - Audio: AAC, M4A, AMRNB, MP3 (up to 16MB)
  - Documents: PDF, DOCX, PPTX, XLSX (up to 100MB)
  - Interactive messages: Buttons (up to 3), Lists (up to 10), Carousels, Templates
- Rich interactive messaging capabilities
- Widespread user adoption and familiarity
- Robust webhook and API integration support
- Advanced business features and analytics

## Key Technical Concepts

### AI Employee Architecture
The system operates on a layered architecture:
- **Channel Layer**: WhatsApp Business API (default), SMS, Email, Voice, Web Chat
- **AI Processing Layer**: NLP Engine, Context Manager, Intent Resolver, AI Actions, Knowledge Base, Response Generation
- **Integration Layer**: REST APIs, Webhooks, Event Streams
- **External Systems**: Business APIs, CRM Systems, Database Integrations

### Bird.com Platform Architecture
```yaml
Core Engine:
  - AI Engine (NLP/NLU Processing with multimodal capabilities)
  - Context Manager (multimedia context enrichment)
  - Action Executor (6 categories of AI Actions)
  - Response Generator (multimedia response generation)

Integration Layer:
  - Authentication (API Keys, HMAC-SHA256)
  - Rate Limiting (1000 req/min API, 100 req/min user)
  - Request Routing (content-type aware)
  - Response Transformation (multimedia optimization)

Channel Support:
  - WhatsApp Business API (primary - full multimedia support)
  - SMS, Email, Voice, Web Chat, Social Media (secondary)
```

### AI Actions Categories
Bird.com supports 6 main categories of AI Actions for multimodal processing:

1. **Bots Actions**: Machine learning chatbot with multimedia query processing
2. **Channel Actions**: Multi-platform messaging with channel-specific multimedia handling
3. **Collaboration Actions**: Inbox management with multimedia context and intelligent assignment
4. **Conversation Actions**: Multimedia conversation tracking and content pattern analysis
5. **Engagement Actions**: Customer data management with visual context and personalization
6. **Number Management Actions**: Multimedia-optimized configuration and intelligent routing

### Conversational Flow Design
Bird.com AI Employees support flexible conversational flows that can be customized for different business use cases:
- **Welcome & User Identification**: Initial greeting and user context gathering
- **Intent Recognition**: Understanding user goals and routing appropriately
- **Information Gathering**: Collecting necessary details through natural conversation
- **Action Execution**: Performing tasks via AI Actions and API integrations
- **Response Generation**: Providing helpful, contextual responses
- **Escalation Management**: Seamless handoff to human agents when needed

## Implementation Approach

### Foundation Components
- Comprehensive documentation for Bird.com AI Employee setup
- Step-by-step configuration guides for manual platform setup
- Knowledge base structuring and content management
- Conversational flow design methodologies
- Testing and validation frameworks

### Advanced Capabilities
- Multimodal AI capabilities analysis and enhancement strategies
- API integration patterns and best practices
- Webhook and event-driven architecture implementation
- Performance monitoring and analytics setup
- Security and compliance guidelines

### Future Enhancements
- Cross-platform integration strategies
- Advanced personalization techniques
- A/B testing methodologies for conversation optimization
- Multi-channel expansion approaches
- **Multimodal capabilities enhancement** (primary focus area)

## Multimodal Enhancement Strategy

The repository contains comprehensive analysis for implementing multimodal capabilities in Bird.com AI Employees with **estimated ROI of 150-200%** in conversational efficiency.

### Three Implementation Strategies

#### Strategy 1: AI Model Enhancement
**Objective**: Upgrade AI capabilities for advanced multimodal processing
- **Advanced Visual Analysis**: Object detection, scene understanding, text extraction
- **Contextual Processing**: Better multimedia context comprehension
- **Multimodal Reasoning**: Cross-media reasoning capabilities
- **Rich Text Generation**: Detailed descriptions from visual analysis

#### Strategy 2: Workflow Extensions
**Objective**: Expand conversational flows for multimedia interactions
- **Media Detection**: Automatic content classification and routing
- **Visual Analysis**: Image content understanding and context extraction
- **Audio Processing**: Voice transcription, sentiment analysis, intent detection
- **Multimedia Response**: Contextual multimedia response generation

#### Strategy 3: API Extensions & New Components
**Objective**: Specialized API components for multimedia processing
- **/ai/multimodal/analyze-image**: Advanced image analysis and content extraction
- **/ai/multimodal/process-audio**: Audio transcription and analysis
- **/ai/multimodal/process-document**: Document parsing and information extraction

### Implementation Timeline & Budget
```yaml
Phase 1 - Foundation (Weeks 1-3):
  - AI model integration and basic multimedia processing
  - Success metrics: >90% accuracy, <3s processing time

Phase 2 - Workflow Enhancement (Weeks 4-7):
  - Extended conversational flows with multimedia
  - Success metrics: >75% completion rate, <5s processing

Phase 3 - Advanced Features (Weeks 8-12):
  - Advanced AI actions and personalization
  - Success metrics: >40% engagement increase, >60% multimodal usage

Total Investment: $56,000 - $77,000
Team: 4 specialists (AI Engineer, Backend Developer, Integration Specialist, QA)
```

### Expected Benefits
- **ROI**: 150-200% improvement in conversational efficiency
- **Conversion Rates**: 25-35% improvement through enhanced engagement
- **Automation**: 40% reduction in manual content processing
- **User Experience**: More intuitive multimedia interactions
- **Scalability**: Handle diverse content without additional human resources

## Development Workflows

### Documentation Updates
Since all configuration is manual, development primarily involves:
1. **Update documentation** based on manual configuration changes
2. **Validate configurations** through Bird.com web interface
3. **Document API integrations** and webhook configurations
4. **Maintain knowledge base** content and structure
5. **Update analysis reports** with performance data and recommendations

### Testing Approach
- Manual testing through Bird.com platform interface
- Conversation flow validation using test scenarios
- API integration testing through external tools
- Performance monitoring through Bird.com native dashboard

### Knowledge Base Management
- Content stored in structured markdown format
- Categories: FAQ, Policies, Business Information, Process Guidelines
- Manual synchronization with Bird.com platform required
- Version control through this repository

## API Integration Patterns

### Authentication
- API Key-based authentication for external business APIs
- HMAC-SHA256 signature verification for webhooks
- Environment variable management for sensitive credentials

### Error Handling
- Comprehensive retry logic with exponential backoff
- Circuit breaker patterns for external service calls
- Graceful degradation strategies
- Dead letter queue for failed webhook deliveries

### Multimedia Processing Integration
```python
# Enhanced webhook configuration for multimedia content
multimedia_webhook_config = {
    "endpoint": "https://your-api.com/bird/multimodal/webhook",
    "events": [
        "message.image.received",
        "message.audio.received", 
        "message.video.received",
        "message.document.received"
    ],
    "processing_limits": {
        "image_max_size": "5MB",
        "audio_max_duration": "60s", 
        "video_max_duration": "120s",
        "document_max_size": "100MB"
    }
}
```

### Security & Privacy Policies
```yaml
Content Validation:
  - Virus scanning and malware detection
  - Content type verification
  - File size limits enforcement

Data Handling:
  - Temporary storage only (7 days retention)
  - AES-256 encryption at rest
  - TLS 1.3 encryption in transit
  - Access logging enabled

Privacy Controls:
  - Automatic PII detection
  - Metadata removal
  - User consent tracking
  - Data deletion on request

Compliance:
  - GDPR compliant
  - CCPA compliant
  - Data residency controls
  - Comprehensive audit logging
```

## Development Guidelines

### Content Creation Guidelines
- Write in Spanish for user-facing documentation
- Use technical English for API documentation and code examples
- Follow the established documentation structure and formatting
- Include practical examples and code snippets where relevant
- Maintain consistency with existing tone and style