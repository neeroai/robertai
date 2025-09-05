# Integración con Bird.com - WhatsApp Business API

## Introducción

Esta guía detalla la integración completa entre WhatsApp Business API y Bird.com AI Employees, optimizada para el ecosistema RobertAI. La integración permite crear experiencias conversacionales avanzadas con capacidades multimodales.

## Configuración de Bird.com AI Employee

### 1. Configuración Inicial

```python
# bird_whatsapp_integration.py
import os
from bird_ai import BirdClient, AIEmployee, Channel
from typing import Dict, List, Optional
import asyncio
import logging

class BirdWhatsAppIntegration:
    def __init__(self):
        self.bird_client = BirdClient(
            api_key=os.getenv('BIRD_API_KEY'),
            workspace_id=os.getenv('BIRD_WORKSPACE_ID')
        )
        
        self.whatsapp_config = {
            'channel_type': 'whatsapp',
            'provider': 'meta',
            'webhook_url': f"{os.getenv('BASE_URL')}/webhooks/whatsapp",
            'capabilities': {
                'text_processing': True,
                'image_analysis': True,
                'audio_transcription': True,
                'document_parsing': True,
                'multimodal_reasoning': True
            }
        }
    
    async def setup_ai_employee(self) -> str:
        """Configurar AI Employee optimizado para WhatsApp"""
        
        ai_employee_config = {
            'name': 'RobertAI WhatsApp Assistant',
            'description': 'Asistente AI multimodal para WhatsApp Business',
            'language': 'es',
            'personality': {
                'tone': 'professional_friendly',
                'formality': 'casual',
                'emoji_usage': 'moderate',
                'response_length': 'concise'
            },
            'capabilities': {
                'multimodal_processing': {
                    'images': {
                        'object_detection': True,
                        'text_extraction': True,
                        'scene_understanding': True,
                        'product_recognition': True
                    },
                    'audio': {
                        'transcription': True,
                        'sentiment_analysis': True,
                        'language_detection': True
                    },
                    'documents': {
                        'text_extraction': True,
                        'summarization': True,
                        'key_information_extraction': True
                    }
                },
                'conversation_management': {
                    'context_retention': '24_hours',
                    'user_profiling': True,
                    'conversation_memory': True,
                    'escalation_detection': True
                },
                'business_integration': {
                    'crm_integration': True,
                    'appointment_scheduling': True,
                    'product_catalog_access': True,
                    'order_processing': True
                }
            },
            'response_templates': {
                'greeting': "¡Hola! Soy tu asistente de RobertAI 🤖 ¿En qué puedo ayudarte hoy?",
                'image_received': "Perfecto, estoy analizando tu imagen...",
                'audio_received': "Escuchando tu mensaje de voz...",
                'document_received': "Procesando tu documento...",
                'escalation': "Te voy a conectar con uno de nuestros especialistas.",
                'error': "Disculpa, tuve un problema técnico. ¿Podrías intentar de nuevo?"
            }
        }
        
        # Crear AI Employee
        ai_employee = await self.bird_client.ai_employees.create(ai_employee_config)
        
        logging.info(f"AI Employee creado: {ai_employee.id}")
        return ai_employee.id
    
    async def configure_whatsapp_channel(self, ai_employee_id: str) -> str:
        """Configurar canal WhatsApp para el AI Employee"""
        
        channel_config = {
            'type': 'whatsapp',
            'name': 'WhatsApp Business - RobertAI',
            'credentials': {
                'access_token': os.getenv('WHATSAPP_ACCESS_TOKEN'),
                'phone_number_id': os.getenv('WHATSAPP_PHONE_NUMBER_ID'),
                'business_account_id': os.getenv('WHATSAPP_BUSINESS_ACCOUNT_ID')
            },
            'webhook_config': {
                'url': self.whatsapp_config['webhook_url'],
                'verify_token': os.getenv('WHATSAPP_WEBHOOK_VERIFY_TOKEN'),
                'signature_secret': os.getenv('WHATSAPP_WEBHOOK_SECRET')
            },
            'settings': {
                'auto_response_enabled': True,
                'business_hours': {
                    'enabled': True,
                    'timezone': 'America/Bogota',
                    'schedule': {
                        'monday': {'start': '09:00', 'end': '18:00'},
                        'tuesday': {'start': '09:00', 'end': '18:00'},
                        'wednesday': {'start': '09:00', 'end': '18:00'},
                        'thursday': {'start': '09:00', 'end': '18:00'},
                        'friday': {'start': '09:00', 'end': '18:00'},
                        'saturday': {'start': '10:00', 'end': '14:00'},
                        'sunday': {'enabled': False}
                    }
                },
                'rate_limiting': {
                    'messages_per_minute': 60,
                    'burst_limit': 10
                }
            }
        }
        
        # Crear canal
        channel = await self.bird_client.channels.create(channel_config)
        
        # Asociar canal con AI Employee
        await self.bird_client.ai_employees.add_channel(ai_employee_id, channel.id)
        
        logging.info(f"Canal WhatsApp configurado: {channel.id}")
        return channel.id
```

### 2. Procesamiento de Mensajes con Bird.com

```python
# bird_message_processor.py
from typing import Dict, List, Optional, Any
import asyncio
import json
from datetime import datetime

class BirdMessageProcessor:
    def __init__(self, bird_client, ai_employee_id: str):
        self.bird_client = bird_client
        self.ai_employee_id = ai_employee_id
        self.conversation_contexts = {}  # Cache de contextos de conversación
    
    async def process_text_message(self, message_data: Dict) -> Dict:
        """Procesar mensaje de texto con Bird.com AI"""
        
        user_id = message_data['from']
        text = message_data['text']
        context = await self.get_conversation_context(user_id)
        
        # Preparar datos para Bird.com
        bird_request = {
            'ai_employee_id': self.ai_employee_id,
            'channel': 'whatsapp',
            'user_id': user_id,
            'message': {
                'type': 'text',
                'content': text,
                'timestamp': datetime.now().isoformat()
            },
            'context': context,
            'user_profile': await self.get_user_profile(user_id)
        }
        
        # Procesar con Bird.com AI
        response = await self.bird_client.conversations.process_message(bird_request)
        
        # Actualizar contexto
        await self.update_conversation_context(user_id, text, response)
        
        return self.format_response_for_whatsapp(response)
    
    async def process_image_message(self, message_data: Dict) -> Dict:
        """Procesar mensaje con imagen usando capacidades multimodales"""
        
        user_id = message_data['from']
        image_data = message_data['image_data']
        caption = message_data.get('caption', '')
        context = await self.get_conversation_context(user_id)
        
        # Análisis de imagen con Bird.com AI
        bird_request = {
            'ai_employee_id': self.ai_employee_id,
            'channel': 'whatsapp',
            'user_id': user_id,
            'message': {
                'type': 'image',
                'image_data': image_data,
                'caption': caption,
                'timestamp': datetime.now().isoformat()
            },
            'context': context,
            'analysis_options': {
                'object_detection': True,
                'text_extraction': True,
                'scene_understanding': True,
                'product_identification': True,
                'generate_description': True
            }
        }
        
        response = await self.bird_client.multimodal.analyze_image(bird_request)
        
        # Generar respuesta conversacional
        conversation_response = await self._generate_conversational_response(
            response, 'image', context
        )
        
        await self.update_conversation_context(
            user_id, f"[Imagen: {caption}]", conversation_response
        )
        
        return self.format_response_for_whatsapp(conversation_response)
    
    async def process_audio_message(self, message_data: Dict) -> Dict:
        """Procesar mensaje de audio con transcripción y análisis"""
        
        user_id = message_data['from']
        audio_data = message_data['audio_data']
        context = await self.get_conversation_context(user_id)
        
        bird_request = {
            'ai_employee_id': self.ai_employee_id,
            'channel': 'whatsapp',
            'user_id': user_id,
            'message': {
                'type': 'audio',
                'audio_data': audio_data,
                'timestamp': datetime.now().isoformat()
            },
            'context': context,
            'transcription_options': {
                'language': 'es',
                'include_confidence': True,
                'detect_sentiment': True,
                'identify_intent': True
            }
        }
        
        response = await self.bird_client.multimodal.transcribe_audio(bird_request)
        
        # Si la transcripción es exitosa, procesar como mensaje de texto
        if response.get('transcription', {}).get('confidence', 0) > 0.7:
            transcribed_text = response['transcription']['text']
            
            # Procesar texto transcrito
            text_response = await self.process_text_message({
                'from': user_id,
                'text': transcribed_text,
                'source': 'audio_transcription'
            })
            
            # Agregar información sobre la transcripción
            text_response['metadata'] = {
                'transcribed_from_audio': True,
                'confidence': response['transcription']['confidence'],
                'sentiment': response.get('sentiment')
            }
            
            return text_response
        
        else:
            # Transcripción de baja calidad
            return {
                'type': 'text',
                'text': "No pude entender claramente tu mensaje de voz. ¿Podrías escribirlo o intentar de nuevo?",
                'metadata': {'transcription_failed': True}
            }
    
    async def process_document_message(self, message_data: Dict) -> Dict:
        """Procesar documento con extracción y análisis de contenido"""
        
        user_id = message_data['from']
        document_data = message_data['document_data']
        filename = message_data.get('filename', 'document')
        context = await self.get_conversation_context(user_id)
        
        bird_request = {
            'ai_employee_id': self.ai_employee_id,
            'channel': 'whatsapp',
            'user_id': user_id,
            'message': {
                'type': 'document',
                'document_data': document_data,
                'filename': filename,
                'timestamp': datetime.now().isoformat()
            },
            'context': context,
            'processing_options': {
                'extract_text': True,
                'generate_summary': True,
                'identify_key_points': True,
                'detect_document_type': True,
                'extract_entities': True
            }
        }
        
        response = await self.bird_client.multimodal.analyze_document(bird_request)
        
        # Generar respuesta conversacional basada en el análisis
        conversation_response = await self._generate_document_response(
            response, filename, context
        )
        
        await self.update_conversation_context(
            user_id, f"[Documento: {filename}]", conversation_response
        )
        
        return self.format_response_for_whatsapp(conversation_response)
    
    async def process_interactive_message(self, message_data: Dict) -> Dict:
        """Procesar interacción con botones o listas"""
        
        user_id = message_data['from']
        interaction_type = message_data['interaction_type']
        interaction_data = message_data['interaction_data']
        context = await self.get_conversation_context(user_id)
        
        bird_request = {
            'ai_employee_id': self.ai_employee_id,
            'channel': 'whatsapp',
            'user_id': user_id,
            'message': {
                'type': 'interactive',
                'interaction_type': interaction_type,
                'data': interaction_data,
                'timestamp': datetime.now().isoformat()
            },
            'context': context
        }
        
        response = await self.bird_client.conversations.handle_interaction(bird_request)
        
        await self.update_conversation_context(
            user_id, f"[Selección: {interaction_data}]", response
        )
        
        return self.format_response_for_whatsapp(response)
    
    async def get_conversation_context(self, user_id: str) -> Dict:
        """Obtener contexto de conversación para un usuario"""
        
        # Buscar en cache local
        if user_id in self.conversation_contexts:
            return self.conversation_contexts[user_id]
        
        # Obtener de Bird.com
        context = await self.bird_client.conversations.get_context(user_id)
        
        # Guardar en cache
        self.conversation_contexts[user_id] = context
        
        return context
    
    async def update_conversation_context(self, user_id: str, 
                                        user_message: str, ai_response: Dict):
        """Actualizar contexto de conversación"""
        
        context_update = {
            'user_message': user_message,
            'ai_response': ai_response.get('text', ''),
            'timestamp': datetime.now().isoformat(),
            'metadata': ai_response.get('metadata', {})
        }
        
        # Actualizar cache local
        if user_id not in self.conversation_contexts:
            self.conversation_contexts[user_id] = {'history': []}
        
        self.conversation_contexts[user_id]['history'].append(context_update)
        
        # Actualizar en Bird.com
        await self.bird_client.conversations.update_context(user_id, context_update)
    
    async def get_user_profile(self, user_id: str) -> Dict:
        """Obtener perfil de usuario desde Bird.com"""
        
        try:
            profile = await self.bird_client.users.get_profile(user_id)
            return profile
        except:
            # Perfil básico si no existe
            return {
                'user_id': user_id,
                'channel': 'whatsapp',
                'first_interaction': datetime.now().isoformat(),
                'preferences': {},
                'conversation_count': 1
            }
    
    def format_response_for_whatsapp(self, bird_response: Dict) -> Dict:
        """Formatear respuesta de Bird.com para WhatsApp"""
        
        if bird_response.get('type') == 'text':
            return {
                'type': 'text',
                'text': bird_response['text']
            }
        
        elif bird_response.get('type') == 'interactive':
            if bird_response['interactive_type'] == 'buttons':
                return {
                    'type': 'buttons',
                    'text': bird_response['text'],
                    'buttons': bird_response['buttons']
                }
            elif bird_response['interactive_type'] == 'list':
                return {
                    'type': 'list',
                    'text': bird_response['text'],
                    'button_text': bird_response['button_text'],
                    'sections': bird_response['sections']
                }
        
        elif bird_response.get('type') == 'media':
            return {
                'type': bird_response['media_type'],
                'url': bird_response['media_url'],
                'caption': bird_response.get('caption', '')
            }
        
        # Fallback a texto simple
        return {
            'type': 'text',
            'text': bird_response.get('text', 'Disculpa, tuve un problema procesando tu mensaje.')
        }
```

### 3. Flujos Conversacionales Avanzados

```python
# conversation_flows.py
from typing import Dict, List, Optional
import asyncio
from enum import Enum

class ConversationFlow:
    """Sistema de flujos conversacionales para Bird.com AI Employee"""
    
    def __init__(self, bird_client, ai_employee_id: str):
        self.bird_client = bird_client
        self.ai_employee_id = ai_employee_id
        self.active_flows = {}  # user_id -> flow_state
    
    async def start_flow(self, user_id: str, flow_type: str, 
                        trigger_data: Dict) -> Dict:
        """Iniciar un flujo conversacional"""
        
        flow_handlers = {
            'product_inquiry': self.handle_product_inquiry_flow,
            'support_request': self.handle_support_request_flow,
            'appointment_booking': self.handle_appointment_booking_flow,
            'lead_qualification': self.handle_lead_qualification_flow
        }
        
        if flow_type not in flow_handlers:
            return {'error': f'Flujo no soportado: {flow_type}'}
        
        # Inicializar estado del flujo
        flow_state = {
            'type': flow_type,
            'step': 'initial',
            'data': {},
            'started_at': datetime.now().isoformat()
        }
        
        self.active_flows[user_id] = flow_state
        
        # Ejecutar handler del flujo
        handler = flow_handlers[flow_type]
        return await handler(user_id, 'start', trigger_data)
    
    async def continue_flow(self, user_id: str, user_input: Dict) -> Dict:
        """Continuar un flujo activo"""
        
        if user_id not in self.active_flows:
            return None  # No hay flujo activo
        
        flow_state = self.active_flows[user_id]
        flow_type = flow_state['type']
        
        # Obtener handler del flujo
        flow_handlers = {
            'product_inquiry': self.handle_product_inquiry_flow,
            'support_request': self.handle_support_request_flow,
            'appointment_booking': self.handle_appointment_booking_flow,
            'lead_qualification': self.handle_lead_qualification_flow
        }
        
        handler = flow_handlers.get(flow_type)
        if handler:
            return await handler(user_id, 'continue', user_input)
        
        return None
    
    async def handle_product_inquiry_flow(self, user_id: str, 
                                        action: str, data: Dict) -> Dict:
        """Flujo de consulta de productos"""
        
        flow_state = self.active_flows[user_id]
        
        if action == 'start':
            # Análisis de imagen de producto si se envió
            if data.get('image_analysis'):
                product_match = await self._find_product_from_image(
                    data['image_analysis']
                )
                
                if product_match:
                    flow_state['data']['product'] = product_match
                    flow_state['step'] = 'product_found'
                    
                    return {
                        'type': 'buttons',
                        'text': f"¡Encontré el producto! {product_match['name']}\n\n"
                               f"Precio: {product_match['price']}\n"
                               f"Disponibilidad: {product_match['stock']} unidades\n\n"
                               f"¿Qué te gustaría hacer?",
                        'buttons': [
                            {'id': 'more_info', 'title': '📋 Más información'},
                            {'id': 'add_cart', 'title': '🛒 Agregar al carrito'},
                            {'id': 'similar', 'title': '🔍 Ver similares'}
                        ]
                    }
            
            # No se encontró producto en imagen
            flow_state['step'] = 'need_details'
            return {
                'type': 'text',
                'text': "¿Qué producto te interesa? Puedes describirlo o enviarme una foto 📸"
            }
        
        elif action == 'continue':
            current_step = flow_state['step']
            
            if current_step == 'product_found':
                selection = data.get('button_id')
                
                if selection == 'more_info':
                    product = flow_state['data']['product']
                    return await self._send_product_details(product)
                
                elif selection == 'add_cart':
                    return await self._start_purchase_flow(user_id, flow_state['data']['product'])
                
                elif selection == 'similar':
                    return await self._show_similar_products(flow_state['data']['product'])
            
            elif current_step == 'need_details':
                # Búsqueda por texto
                search_results = await self._search_products(data['text'])
                
                if search_results:
                    return await self._show_product_options(search_results)
                else:
                    return {
                        'type': 'text',
                        'text': "No encontré productos que coincidan. ¿Podrías ser más específico o enviar una foto?"
                    }
        
        return {'type': 'text', 'text': 'Error en el flujo de productos'}
    
    async def handle_support_request_flow(self, user_id: str, 
                                        action: str, data: Dict) -> Dict:
        """Flujo de solicitud de soporte"""
        
        flow_state = self.active_flows[user_id]
        
        if action == 'start':
            flow_state['step'] = 'category_selection'
            
            return {
                'type': 'list',
                'text': "¿Con qué necesitas ayuda?",
                'button_text': "Seleccionar categoría",
                'sections': [
                    {
                        'title': "Soporte Técnico",
                        'rows': [
                            {'id': 'tech_issue', 'title': 'Problema técnico', 'description': 'Error en la aplicación o servicio'},
                            {'id': 'login_issue', 'title': 'Problema de acceso', 'description': 'No puedo iniciar sesión'}
                        ]
                    },
                    {
                        'title': "Facturación",
                        'rows': [
                            {'id': 'billing_issue', 'title': 'Problema de facturación', 'description': 'Consulta sobre pagos o facturas'},
                            {'id': 'refund_request', 'title': 'Solicitar reembolso', 'description': 'Quiero devolver un producto'}
                        ]
                    }
                ]
            }
        
        elif action == 'continue':
            if flow_state['step'] == 'category_selection':
                category = data.get('list_id')
                flow_state['data']['category'] = category
                flow_state['step'] = 'details_collection'
                
                return {
                    'type': 'text',
                    'text': "Perfecto. Cuéntame más detalles sobre tu problema. Puedes enviar texto, imágenes o audios."
                }
            
            elif flow_state['step'] == 'details_collection':
                # Recopilar información del problema
                flow_state['data']['details'] = data
                
                # Crear ticket de soporte
                ticket = await self._create_support_ticket(user_id, flow_state['data'])
                
                # Finalizar flujo
                del self.active_flows[user_id]
                
                return {
                    'type': 'text',
                    'text': f"✅ He creado tu ticket de soporte #{ticket['id']}\n\n"
                           f"Nuestro equipo te contactará en un máximo de 24 horas.\n\n"
                           f"¿Hay algo más en lo que pueda ayudarte?"
                }
        
        return {'type': 'text', 'text': 'Error en el flujo de soporte'}
    
    async def _find_product_from_image(self, image_analysis: Dict) -> Optional[Dict]:
        """Buscar producto basado en análisis de imagen"""
        # Integración con catálogo de productos
        objects = image_analysis.get('objects', [])
        text = image_analysis.get('text', '')
        
        # Lógica de búsqueda de productos
        # Esto se integraría con el sistema de productos real
        return {
            'id': 'prod_123',
            'name': 'Laptop Gaming XZ',
            'price': '$1,299.99',
            'stock': 5,
            'image_url': 'https://example.com/laptop.jpg'
        }
    
    async def _create_support_ticket(self, user_id: str, ticket_data: Dict) -> Dict:
        """Crear ticket de soporte en el sistema"""
        # Integración con sistema de tickets
        ticket = {
            'id': f'TICK-{datetime.now().strftime("%Y%m%d%H%M%S")}',
            'user_id': user_id,
            'category': ticket_data['category'],
            'details': ticket_data['details'],
            'status': 'open',
            'priority': 'medium',
            'created_at': datetime.now().isoformat()
        }
        
        # Guardar en Bird.com
        await self.bird_client.tickets.create(ticket)
        
        return ticket
```

## Integración con Sistemas Empresariales

### 1. Integración CRM

```python
# crm_integration.py
from typing import Dict, List, Optional
import aiohttp
import asyncio

class CRMIntegration:
    def __init__(self, bird_client, crm_config: Dict):
        self.bird_client = bird_client
        self.crm_config = crm_config
        self.crm_api_url = crm_config['api_url']
        self.crm_api_key = crm_config['api_key']
    
    async def sync_contact(self, whatsapp_user_id: str, contact_data: Dict) -> Dict:
        """Sincronizar contacto con CRM"""
        
        # Buscar contacto existente
        existing_contact = await self._find_contact_by_whatsapp(whatsapp_user_id)
        
        if existing_contact:
            # Actualizar contacto existente
            updated_contact = await self._update_contact(existing_contact['id'], contact_data)
            await self._log_interaction(updated_contact['id'], 'contact_updated')
            return updated_contact
        else:
            # Crear nuevo contacto
            new_contact = await self._create_contact(contact_data)
            await self._link_whatsapp_contact(new_contact['id'], whatsapp_user_id)
            await self._log_interaction(new_contact['id'], 'contact_created')
            return new_contact
    
    async def create_lead(self, whatsapp_user_id: str, lead_data: Dict) -> Dict:
        """Crear lead desde conversación WhatsApp"""
        
        # Obtener o crear contacto
        contact = await self.sync_contact(whatsapp_user_id, lead_data.get('contact_info', {}))
        
        # Crear lead
        lead = {
            'contact_id': contact['id'],
            'source': 'whatsapp',
            'status': 'new',
            'product_interest': lead_data.get('product_interest'),
            'budget_range': lead_data.get('budget_range'),
            'timeline': lead_data.get('timeline'),
            'notes': lead_data.get('notes', ''),
            'conversation_summary': lead_data.get('conversation_summary'),
            'whatsapp_user_id': whatsapp_user_id
        }
        
        created_lead = await self._create_lead(lead)
        await self._log_interaction(contact['id'], 'lead_created', {'lead_id': created_lead['id']})
        
        return created_lead
    
    async def log_conversation(self, whatsapp_user_id: str, 
                             conversation_data: Dict):
        """Registrar conversación en CRM"""
        
        contact = await self._find_contact_by_whatsapp(whatsapp_user_id)
        if not contact:
            return
        
        interaction = {
            'contact_id': contact['id'],
            'type': 'whatsapp_conversation',
            'subject': conversation_data.get('subject', 'WhatsApp Chat'),
            'content': conversation_data.get('summary'),
            'timestamp': conversation_data.get('timestamp'),
            'metadata': {
                'message_count': conversation_data.get('message_count'),
                'duration': conversation_data.get('duration'),
                'sentiment': conversation_data.get('sentiment'),
                'topics': conversation_data.get('topics', [])
            }
        }
        
        await self._log_interaction(contact['id'], 'conversation', interaction)
```

## Monitoreo y Analytics

```python
# bird_analytics.py
from typing import Dict, List
from datetime import datetime, timedelta
import asyncio

class BirdAnalytics:
    def __init__(self, bird_client):
        self.bird_client = bird_client
    
    async def get_conversation_metrics(self, period_days: int = 7) -> Dict:
        """Obtener métricas de conversación"""
        
        end_date = datetime.now()
        start_date = end_date - timedelta(days=period_days)
        
        metrics = await self.bird_client.analytics.get_conversation_metrics({
            'start_date': start_date.isoformat(),
            'end_date': end_date.isoformat(),
            'channel': 'whatsapp'
        })
        
        return {
            'total_conversations': metrics.get('total_conversations', 0),
            'unique_users': metrics.get('unique_users', 0),
            'avg_messages_per_conversation': metrics.get('avg_messages_per_conversation', 0),
            'resolution_rate': metrics.get('resolution_rate', 0),
            'avg_response_time': metrics.get('avg_response_time', 0),
            'user_satisfaction': metrics.get('user_satisfaction', 0),
            'top_intents': metrics.get('top_intents', []),
            'escalation_rate': metrics.get('escalation_rate', 0)
        }
    
    async def get_multimodal_usage(self) -> Dict:
        """Obtener estadísticas de uso multimodal"""
        
        multimodal_metrics = await self.bird_client.analytics.get_multimodal_metrics({
            'channel': 'whatsapp'
        })
        
        return {
            'image_messages': multimodal_metrics.get('image_messages', 0),
            'audio_messages': multimodal_metrics.get('audio_messages', 0),
            'document_messages': multimodal_metrics.get('document_messages', 0),
            'successful_image_analysis': multimodal_metrics.get('successful_image_analysis', 0),
            'successful_transcriptions': multimodal_metrics.get('successful_transcriptions', 0),
            'document_extraction_success': multimodal_metrics.get('document_extraction_success', 0)
        }
```

## Próximos Pasos

1. **Implementar API reference**: Continuar con [Referencia de API](07-api-reference.md)
2. **Aplicar mejores prácticas**: Seguir [Mejores Prácticas](08-best-practices.md)
3. **Configurar troubleshooting**: Implementar [Guía de Resolución de Problemas](10-troubleshooting.md)

---

**Nota de Integración**: Esta configuración optimiza Bird.com AI Employee específicamente para WhatsApp Business API con capacidades multimodales completas y flujos conversacionales avanzados.