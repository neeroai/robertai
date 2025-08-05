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
- Native multimedia support (images, documents, audio, video)
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

The repository contains comprehensive analysis for implementing multimodal capabilities in Bird.com AI Employees:

### Enhancement Areas
1. **AI Model Optimization**: Advanced language models with multimodal capabilities
2. **Workflow Extensions**: Multimedia processing integration into conversational flows
3. **API Enhancements**: Visual analysis, audio processing, and document handling capabilities
4. **Channel Optimization**: Full utilization of WhatsApp Business API (primary channel) multimedia features, with secondary optimization for other communication channels

### Expected Benefits
- Significant ROI improvement through enhanced user engagement
- Higher conversation completion rates
- Improved user satisfaction and experience
- Enhanced operational efficiency and automation capabilities

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

## Development Guidelines

### Content Creation Guidelines
- Write in Spanish for user-facing documentation
- Use technical English for API documentation and code examples
- Follow the established documentation structure and formatting
- Include practical examples and code snippets where relevant
- Maintain consistency with existing tone and style