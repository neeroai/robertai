# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

**RobertAI** es un repositorio integral para el desarrollo de un **Asistente Personal Multimodal por WhatsApp**. Este repositorio contiene toda la documentación, arquitectura de código y estrategias de implementación necesarias para desarrollar un asistente personal sofisticado que aprovecha la **WhatsApp Business API** para interacciones multimodales incluyendo texto, voz, imágenes, documentos y mensajería interactiva.

### Funcionalidades Principales

- **Gestión Inteligente de Recordatorios**: Alarmas únicas y recurrentes con sincronización de calendario
- **Agendamiento Automatizado**: Programación de citas, reuniones y reservas inteligentes
- **Procesamiento Multimodal**: Transcripción de audio, análisis de imágenes, procesamiento de documentos
- **Mensajería Programada**: Envío automático y respuestas inteligentes 24/7
- **Integraciones Avanzadas**: Google Calendar, APIs externas, servicios de terceros
- **Conversational AI**: Flujos conversacionales naturales con contexto multimodal

## Important Constraints

## Default Channel Configuration

**WhatsApp Business API** es el canal predeterminado y recomendado para la implementación del Asistente Personal RobertAI. Todas las funcionalidades principales, flujos de trabajo e integraciones están diseñadas y optimizadas específicamente para WhatsApp Business API.

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

### Arquitectura del Asistente Personal

El sistema opera en una arquitectura por capas:

- **Capa de Canal**: WhatsApp Business API (principal)
- **Capa de Procesamiento IA**: Motor NLP, Gestor de Contexto, Resolución de Intenciones, Acciones IA, Base de Conocimiento, Generación de Respuestas
- **Capa de Integración**: REST APIs, Webhooks, Event Streams
- **Sistemas Externos**: Google Calendar, APIs de servicios, Integraciones de bases de datos

### Arquitectura de la Plataforma RobertAI

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

### Categorías de Acciones del Asistente

RobertAI soporta 6 categorías principales de acciones IA para procesamiento multimodal:

1. **Acciones de Recordatorios**: Gestión inteligente de alarmas y notificaciones programadas
2. **Acciones de Agendamiento**: Programación automática de citas y eventos con sincronización de calendario
3. **Acciones Multimodales**: Procesamiento de audio, imágenes y documentos con análisis contextual
4. **Acciones de Mensajería**: Envío programado, respuestas automáticas y difusión personalizada
5. **Acciones de Integración**: Conectividad con APIs externas y servicios de terceros
6. **Acciones Conversacionales**: Gestión de contexto y flujos de conversación natural

### Conversational Flow Design

RobertAI soporta flujos conversacionales flexibles que pueden ser personalizados para diferentes casos de uso personal:

- **Welcome & User Identification**: Initial greeting and user context gathering
- **Intent Recognition**: Understanding user goals and routing appropriately
- **Information Gathering**: Collecting necessary details through natural conversation
- **Action Execution**: Performing tasks via AI Actions and API integrations
- **Response Generation**: Providing helpful, contextual responses
- **Escalation Management**: Seamless handoff to human agents when needed

## Implementation Approach

### Componentes Base

- Documentación completa para configuración del Asistente Personal RobertAI
- Guías paso a paso para configuración de la plataforma
- Estructuración de base de conocimiento y gestión de contenido
- Metodologías de diseño de flujos conversacionales
- Frameworks de pruebas y validación

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

El repositorio contiene análisis comprensivo para implementar capacidades multimodales en el Asistente Personal RobertAI con **ROI estimado de 150-200%** en eficiencia conversacional.

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

## Dual Configuration Architecture

This repository uses a **dual configuration system** with strict separation of concerns to prevent conflicts:

### `.bmad-core` - BMad Methodology System
- **Purpose**: Development methodology, PMO workflows, project management
- **Agents**: `/BMadPM`, `/BMadDev`, `/BMadQA`, `/BMadArchitect`, `/BMadPO`
- **Namespace**: `BMad*` prefix (reserved)
- **Focus**: Documentation templates, checklists, user stories, architecture planning

### `.claude` - Sistema RobertAI Asistente Personal  
- **Purpose**: Capacidades del asistente personal, procesamiento multimodal, integración WhatsApp
- **Agents**: `/robert-master`, `/multimodal-analyst`, `/conversation-designer`, `/whatsapp-specialist`
- **Tools**: `analyze_multimodal`, `whatsapp_api_client`, `conversation_flow`, `calendar_handler`, `reminder_manager`
- **Focus**: Flujos de IA personal, procesamiento multimedia, flujos conversacionales

## Essential Commands

### Configuration Validation
```bash
# Run comprehensive configuration validation (CRITICAL before any changes)
python3 validate_configurations.py

# Install automated Git hooks for validation
./install-hooks.sh

# Validate Claude-specific configuration
cd .claude && python3 validate_config.py
```

### Development Workflow
```bash
# Before making any configuration changes - validate current state
python3 validate_configurations.py

# Commit changes (automatic validation via pre-commit hook)
git add . && git commit -m "Your message"

# Push changes (automatic validation via pre-push hook)  
git push
```

## Critical Configuration Rules

### Namespace Separation (STRICTLY ENFORCED)
- **BMad namespace**: `BMad*`, `/BMad*` - EXCLUSIVE to `.bmad-core`
- **RobertAI namespace**: `robert_*`, `/robert-*` - EXCLUSIVE to `.claude`
- **Reserved**: `whatsapp*`, `multimodal*`, `reminder*`, `calendar*` - EXCLUSIVE to `.claude`

### File Path Allocation
- **`.bmad-core` controls**: `docs/prd/`, `docs/architecture/`, `docs/stories/`
- **`.claude` controls**: `.claude/tools/`, `.claude/agents/`
- **Shared**: `docs/` root, `CLAUDE.md`

## Agent Usage Patterns

### BMad Development Methodology
```bash
/BMadPM          # Product management, PRD creation
/BMadDev         # Story implementation, coding standards
/BMadQA          # Quality assurance, testing frameworks
/BMadArchitect   # System design, technical architecture
/BMadPO          # Requirements validation, story acceptance
```

### Capacidades RobertAI Asistente Personal
```bash
/robert-master            # Orquestador universal del Asistente Personal RobertAI
/multimodal-analyst       # Análisis de contenido multimedia
/conversation-designer    # Arquitectura de flujos conversacionales personales
/whatsapp-specialist      # Optimización WhatsApp Business API para uso personal
/integration-engineer     # Integraciones API y gestión de webhooks
/reminder-specialist      # Especialista en recordatorios y agendamiento
```

## Architecture Overview

### Repository Structure
```
robertai/
├── .bmad-core/              # BMad methodology configuration
│   ├── core-config.yaml     # BMad system configuration
│   ├── tasks/               # Development workflows
│   ├── templates/           # Document templates
│   └── checklists/          # Validation checklists
├── .claude/                 # Sistema RobertAI Asistente Personal
│   ├── tools.json           # Custom AI tools definition
│   ├── settings.local.json  # Claude permissions
│   ├── tools/               # Python tool implementations
│   └── agents/              # Specialized agent definitions
├── .config/                 # Integration configuration
│   └── integration.yaml     # Cross-system compatibility rules
├── docs/                    # Shared documentation
└── validate_configurations.py  # Master validation script
```

### Tool Integration Patterns
The `.claude/tools/` directory contains Python implementations for:
- **analyze_multimodal.py**: Multimedia content processing
- **whatsapp_api_client.py**: Integración WhatsApp Business API
- **calendar_integration.py**: Integración con Google Calendar
- **reminder_manager.py**: Gestor de recordatorios y alarmas
- **conversation_flow.py**: Conversational workflow management
- **whatsapp_handler.py**: WhatsApp Business API functionality
- **knowledge_base.py**: AI knowledge management
- **workflow_orchestrator.py**: Complex workflow coordination

## Development Guidelines

### Before Any Configuration Changes
1. **ALWAYS** run `python3 validate_configurations.py`
2. Review `CONFIGURATION_GUIDE.md` for namespace rules
3. Understand which system (`.bmad-core` vs `.claude`) owns the area you're modifying
4. Test changes in isolation before committing

### Content Creation Guidelines
- Write in Spanish for user-facing documentation
- Use technical English for API documentation and code examples  
- Follow established documentation structure and formatting
- Include practical examples and code snippets where relevant
- Maintain consistency with existing tone and style
- **NEVER** violate namespace separation rules

### Critical Files to Never Modify Without Validation
- `.bmad-core/core-config.yaml` - BMad system configuration
- `.claude/tools.json` - AI tool definitions
- `.claude/settings.local.json` - Claude permissions
- `.config/integration.yaml` - Cross-system rules

# important-instruction-reminders
Do what has been asked; nothing more, nothing less.
NEVER create files unless they're absolutely necessary for achieving your goal.
ALWAYS prefer editing an existing file to creating a new one.
NEVER proactively create documentation files (*.md) or README files. Only create documentation files if explicitly requested by the User.
