# Eventos de Webhook - WhatsApp Business API

## Introducción

Los webhooks de WhatsApp Business API permiten recibir eventos en tiempo real sobre mensajes, estados de entrega y cambios en las conversaciones. Esta guía cubre la implementación completa del manejo de webhooks para integración con Bird.com AI Employees.

## Tipos de Eventos

### 1. Eventos de Mensajes Entrantes

```python
# webhook_message_handler.py
from typing import Dict, List
import asyncio
import logging
from datetime import datetime

class WhatsAppMessageHandler:
    def __init__(self, bird_client):
        self.bird_client = bird_client
        self.message_processors = {
            'text': self.handle_text_message,
            'image': self.handle_image_message,
            'video': self.handle_video_message,
            'audio': self.handle_audio_message,
            'document': self.handle_document_message,
            'location': self.handle_location_message,
            'contacts': self.handle_contacts_message,
            'interactive': self.handle_interactive_message
        }
    
    async def process_webhook_event(self, webhook_data: Dict):
        """Procesar evento de webhook entrante"""
        try:
            for entry in webhook_data.get('entry', []):
                for change in entry.get('changes', []):
                    if change.get('field') == 'messages':
                        await self.process_message_change(change['value'])
            
            return {"status": "success", "processed": True}
            
        except Exception as e:
            logging.error(f"Error procesando webhook: {e}")
            return {"status": "error", "message": str(e)}
    
    async def process_message_change(self, change_data: Dict):
        """Procesar cambio en mensajes"""
        # Procesar mensajes entrantes
        messages = change_data.get('messages', [])
        for message in messages:
            await self.handle_incoming_message(message, change_data)
        
        # Procesar estados de mensaje
        statuses = change_data.get('statuses', [])
        for status in statuses:
            await self.handle_message_status(status)
        
        # Procesar errores
        errors = change_data.get('errors', [])
        for error in errors:
            await self.handle_webhook_error(error)
    
    async def handle_incoming_message(self, message: Dict, context: Dict):
        """Manejar mensaje entrante"""
        message_type = message.get('type')
        from_number = message.get('from')
        message_id = message.get('id')
        timestamp = message.get('timestamp')
        
        # Obtener información del contacto
        contact_info = self.get_contact_info(context, from_number)
        
        # Log del mensaje entrante
        logging.info(f"Mensaje {message_type} recibido de {from_number}: {message_id}")
        
        # Procesar según el tipo de mensaje
        processor = self.message_processors.get(message_type)
        if processor:
            await processor(message, from_number, contact_info)
        else:
            logging.warning(f"Tipo de mensaje no soportado: {message_type}")
            await self.handle_unsupported_message(message, from_number)
    
    async def handle_text_message(self, message: Dict, from_number: str, contact_info: Dict):
        """Procesar mensaje de texto"""
        text_content = message.get('text', {}).get('body', '')
        context = message.get('context')  # Si es respuesta a otro mensaje
        
        # Enviar a Bird.com AI Employee para procesamiento
        ai_response = await self.bird_client.process_text_message({
            'text': text_content,
            'from': from_number,
            'contact_info': contact_info,
            'context': context,
            'channel': 'whatsapp',
            'message_id': message.get('id'),
            'timestamp': message.get('timestamp')
        })
        
        # Enviar respuesta generada por AI
        if ai_response and ai_response.get('response'):
            await self.send_ai_response(from_number, ai_response)
    
    async def handle_image_message(self, message: Dict, from_number: str, contact_info: Dict):
        """Procesar mensaje con imagen"""
        image_data = message.get('image', {})
        image_id = image_data.get('id')
        caption = image_data.get('caption', '')
        mime_type = image_data.get('mime_type')
        
        # Descargar imagen para análisis
        image_url = await self.get_media_url(image_id)
        image_content = await self.download_media(image_url)
        
        # Análisis de imagen con Bird.com AI
        ai_response = await self.bird_client.process_image_message({
            'image_data': image_content,
            'caption': caption,
            'mime_type': mime_type,
            'from': from_number,
            'contact_info': contact_info,
            'channel': 'whatsapp'
        })
        
        # Responder con análisis de imagen
        if ai_response:
            await self.send_ai_response(from_number, ai_response)
    
    async def handle_audio_message(self, message: Dict, from_number: str, contact_info: Dict):
        """Procesar mensaje de audio"""
        audio_data = message.get('audio', {})
        audio_id = audio_data.get('id')
        mime_type = audio_data.get('mime_type')
        
        # Descargar audio para transcripción\n        audio_url = await self.get_media_url(audio_id)
        audio_content = await self.download_media(audio_url)
        
        # Transcripción y análisis con Bird.com AI
        ai_response = await self.bird_client.process_audio_message({
            'audio_data': audio_content,
            'mime_type': mime_type,
            'from': from_number,
            'contact_info': contact_info,
            'channel': 'whatsapp'
        })
        
        if ai_response:
            await self.send_ai_response(from_number, ai_response)
    
    async def handle_interactive_message(self, message: Dict, from_number: str, contact_info: Dict):
        """Procesar respuesta de mensaje interactivo"""
        interactive_data = message.get('interactive', {})
        interaction_type = interactive_data.get('type')
        
        if interaction_type == 'button_reply':
            button_reply = interactive_data.get('button_reply', {})
            button_id = button_reply.get('id')
            button_title = button_reply.get('title')
            
            # Procesar selección de botón
            ai_response = await self.bird_client.process_button_interaction({
                'button_id': button_id,
                'button_title': button_title,
                'from': from_number,
                'contact_info': contact_info,
                'channel': 'whatsapp'
            })
            
        elif interaction_type == 'list_reply':
            list_reply = interactive_data.get('list_reply', {})
            list_id = list_reply.get('id')
            list_title = list_reply.get('title')
            
            # Procesar selección de lista
            ai_response = await self.bird_client.process_list_interaction({
                'list_id': list_id,
                'list_title': list_title,
                'from': from_number,
                'contact_info': contact_info,
                'channel': 'whatsapp'
            })
        
        if ai_response:
            await self.send_ai_response(from_number, ai_response)
```

### 2. Estados de Mensaje

```python
# message_status_handler.py
class MessageStatusHandler:
    def __init__(self):
        self.status_callbacks = {
            'sent': self.handle_message_sent,
            'delivered': self.handle_message_delivered,
            'read': self.handle_message_read,
            'failed': self.handle_message_failed
        }
    
    async def handle_message_status(self, status_data: Dict):
        """Manejar actualización de estado de mensaje"""
        message_id = status_data.get('id')
        status = status_data.get('status')
        recipient_id = status_data.get('recipient_id')
        timestamp = status_data.get('timestamp')
        
        # Actualizar estado en base de datos
        await self.update_message_status(message_id, status, timestamp)
        
        # Ejecutar callback específico del estado
        callback = self.status_callbacks.get(status)
        if callback:
            await callback(status_data)
        
        # Notificar a Bird.com sobre el cambio de estado
        await self.notify_bird_status_change({
            'message_id': message_id,
            'status': status,
            'recipient_id': recipient_id,
            'timestamp': timestamp,
            'channel': 'whatsapp'
        })
    
    async def handle_message_sent(self, status_data: Dict):
        """Mensaje enviado exitosamente"""
        logging.info(f"Mensaje {status_data['id']} enviado a {status_data['recipient_id']}")
        
        # Actualizar métricas de envío
        await self.update_delivery_metrics('sent')
    
    async def handle_message_delivered(self, status_data: Dict):
        """Mensaje entregado al dispositivo del usuario"""
        logging.info(f"Mensaje {status_data['id']} entregado")
        
        # Actualizar métricas de entrega
        await self.update_delivery_metrics('delivered')
    
    async def handle_message_read(self, status_data: Dict):
        """Usuario leyó el mensaje"""
        logging.info(f"Mensaje {status_data['id']} leído")
        
        # Actualizar métricas de lectura
        await self.update_delivery_metrics('read')
        
        # Trigger para seguimiento de conversación
        await self.trigger_read_receipt_actions(status_data)
    
    async def handle_message_failed(self, status_data: Dict):
        """Fallo en entrega de mensaje"""
        errors = status_data.get('errors', [])
        logging.error(f"Fallo en mensaje {status_data['id']}: {errors}")
        
        # Intentar reenvío si es apropiado
        await self.handle_message_failure(status_data, errors)
        
        # Notificar sistema de alertas
        await self.trigger_failure_alert(status_data, errors)
```

### 3. Manejo de Errores

```python
# webhook_error_handler.py
class WebhookErrorHandler:
    def __init__(self):
        self.error_handlers = {
            131026: self.handle_rate_limit_error,
            131047: self.handle_re_engagement_error,
            131005: self.handle_parameter_error,
            132000: self.handle_generic_error
        }
    
    async def handle_webhook_error(self, error_data: Dict):
        """Manejar error reportado por webhook"""
        error_code = error_data.get('code')
        error_title = error_data.get('title')
        error_message = error_data.get('message')
        error_details = error_data.get('error_data', {})
        
        logging.error(f"Error webhook {error_code}: {error_title} - {error_message}")
        
        # Ejecutar handler específico del error
        handler = self.error_handlers.get(error_code)
        if handler:
            await handler(error_data)
        else:
            await self.handle_unknown_error(error_data)
        
        # Registrar error para análisis
        await self.log_error_for_analysis({
            'code': error_code,
            'title': error_title,
            'message': error_message,
            'details': error_details,
            'timestamp': datetime.now().isoformat(),
            'channel': 'whatsapp'
        })
    
    async def handle_rate_limit_error(self, error_data: Dict):
        \"\"\"Manejar error de rate limiting\"\"\"
        # Implementar backoff exponencial
        wait_time = self.calculate_backoff_time()
        logging.warning(f\"Rate limit excedido. Esperando {wait_time} segundos\")
        
        await asyncio.sleep(wait_time)
        
        # Reactivar procesamiento de mensajes
        await self.resume_message_processing()
    
    async def handle_re_engagement_error(self, error_data: Dict):
        \"\"\"Manejar error de re-engagement (24h window)\"\"\"
        # Usuario fuera de ventana de 24 horas
        recipient_id = error_data.get('error_data', {}).get('details', '')
        
        # Marcar conversación para template message
        await self.mark_for_template_message(recipient_id)
        
        # Notificar al sistema de que se requiere template
        await self.trigger_template_requirement_notification(recipient_id)
```

## Configuración del Servidor Webhook

### 1. Servidor FastAPI

```python
# webhook_server.py
from fastapi import FastAPI, Request, HTTPException, BackgroundTasks
from fastapi.responses import PlainTextResponse
import hmac
import hashlib
import os
import json
import logging

app = FastAPI(title="WhatsApp Business API Webhook")

# Inicializar handlers
message_handler = WhatsAppMessageHandler(bird_client)
status_handler = MessageStatusHandler()
error_handler = WebhookErrorHandler()

@app.get("/webhooks/whatsapp")
async def verify_webhook(
    request: Request,
    hub_mode: str = None,
    hub_verify_token: str = None,
    hub_challenge: str = None
):
    """Verificación del webhook por Meta"""
    
    if hub_mode == "subscribe" and hub_verify_token == os.getenv('WHATSAPP_WEBHOOK_VERIFY_TOKEN'):
        logging.info("Webhook verificado exitosamente")
        return PlainTextResponse(content=hub_challenge)
    else:
        logging.warning("Fallo en verificación de webhook")
        raise HTTPException(status_code=403, detail="Token de verificación inválido")

@app.post("/webhooks/whatsapp")
async def receive_webhook(
    request: Request,
    background_tasks: BackgroundTasks
):
    """Recibir y procesar eventos de WhatsApp"""
    
    # Verificar firma HMAC
    signature = request.headers.get('X-Hub-Signature-256')
    body = await request.body()
    
    if not verify_webhook_signature(body, signature):
        raise HTTPException(status_code=401, detail="Firma HMAC inválida")
    
    # Parsear datos del webhook
    try:
        webhook_data = json.loads(body)
    except json.JSONDecodeError:
        raise HTTPException(status_code=400, detail="JSON inválido")
    
    # Procesar en background para respuesta rápida
    background_tasks.add_task(process_webhook_background, webhook_data)
    
    return PlainTextResponse(content="OK")

def verify_webhook_signature(payload: bytes, signature: str) -> bool:
    """Verificar firma HMAC-SHA256 del webhook"""
    if not signature or not signature.startswith('sha256='):
        return False
    
    expected_signature = 'sha256=' + hmac.new(
        os.getenv('WHATSAPP_WEBHOOK_SECRET').encode(),
        payload,
        hashlib.sha256
    ).hexdigest()
    
    return hmac.compare_digest(signature, expected_signature)

async def process_webhook_background(webhook_data: dict):
    """Procesar webhook en background"""
    try:
        # Procesar eventos de mensaje
        result = await message_handler.process_webhook_event(webhook_data)
        logging.info(f"Webhook procesado: {result}")
        
    except Exception as e:
        logging.error(f"Error procesando webhook en background: {e}")
        await error_handler.handle_processing_error(webhook_data, str(e))

# Health check endpoint
@app.get("/health")
async def health_check():
    """Verificación de salud del webhook"""
    return {
        "status": "healthy",
        "timestamp": datetime.now().isoformat(),
        "service": "whatsapp-webhook",
        "version": "1.0.0"
    }
```

### 2. Manejo de Archivos Multimedia

```python
# media_handler.py
import aiohttp
import aiofiles
from typing import Optional, Tuple
import tempfile
import os

class MediaHandler:
    def __init__(self, access_token: str):
        self.access_token = access_token
        self.base_url = "https://graph.facebook.com/v18.0"
        
    async def get_media_url(self, media_id: str) -> str:
        """Obtener URL de descarga para un media_id"""
        url = f"{self.base_url}/{media_id}"
        headers = {'Authorization': f'Bearer {self.access_token}'}
        
        async with aiohttp.ClientSession() as session:
            async with session.get(url, headers=headers) as response:
                if response.status == 200:
                    data = await response.json()
                    return data.get('url')
                else:
                    raise Exception(f"Error obteniendo URL de media: {response.status}")
    
    async def download_media(self, media_url: str) -> Tuple[bytes, str]:
        """Descargar archivo multimedia"""
        headers = {'Authorization': f'Bearer {self.access_token}'}
        
        async with aiohttp.ClientSession() as session:
            async with session.get(media_url, headers=headers) as response:
                if response.status == 200:
                    content = await response.read()
                    content_type = response.headers.get('Content-Type', '')
                    return content, content_type
                else:
                    raise Exception(f"Error descargando media: {response.status}")
    
    async def save_media_temporarily(self, content: bytes, file_extension: str) -> str:
        """Guardar archivo temporalmente para procesamiento"""
        with tempfile.NamedTemporaryFile(
            delete=False, 
            suffix=f".{file_extension}"
        ) as tmp_file:
            tmp_file.write(content)
            return tmp_file.name
    
    async def process_media_with_bird(self, media_content: bytes, media_type: str, metadata: dict):
        """Procesar archivo multimedia con Bird.com AI"""
        
        # Guardar temporalmente
        file_extension = self.get_file_extension(media_type)
        temp_file_path = await self.save_media_temporarily(media_content, file_extension)
        
        try:
            # Procesar con Bird.com según el tipo
            if media_type.startswith('image/'):
                result = await self.bird_client.analyze_image(temp_file_path, metadata)
            elif media_type.startswith('audio/'):
                result = await self.bird_client.transcribe_audio(temp_file_path, metadata)
            elif media_type.startswith('video/'):
                result = await self.bird_client.analyze_video(temp_file_path, metadata)
            elif media_type == 'application/pdf':
                result = await self.bird_client.parse_document(temp_file_path, metadata)
            else:
                result = {"error": f"Tipo de media no soportado: {media_type}"}
            
            return result
            
        finally:
            # Limpiar archivo temporal
            if os.path.exists(temp_file_path):
                os.unlink(temp_file_path)
```

## Configuración de Retry y Reliability

```python
# webhook_reliability.py
import asyncio
from typing import Dict, List
import logging
from datetime import datetime, timedelta

class WebhookReliabilityManager:
    def __init__(self):
        self.max_retries = 3
        self.base_delay = 1.0  # segundos
        self.max_delay = 60.0  # segundos
        self.failed_messages = {}
        
    async def process_with_retry(self, webhook_data: Dict, processor_func):
        """Procesar webhook con reintentos automáticos"""
        for attempt in range(self.max_retries + 1):
            try:
                result = await processor_func(webhook_data)
                
                # Éxito - limpiar cualquier fallo previo
                message_id = self.extract_message_id(webhook_data)
                if message_id in self.failed_messages:
                    del self.failed_messages[message_id]
                
                return result
                
            except Exception as e:
                if attempt == self.max_retries:
                    # Último intento fallido
                    await self.handle_permanent_failure(webhook_data, str(e))
                    raise
                
                # Calcular delay con backoff exponencial
                delay = min(self.base_delay * (2 ** attempt), self.max_delay)
                logging.warning(f"Intento {attempt + 1} fallido, reintentando en {delay}s: {e}")
                await asyncio.sleep(delay)
    
    async def handle_permanent_failure(self, webhook_data: Dict, error: str):
        """Manejar fallo permanente después de todos los reintentos"""
        message_id = self.extract_message_id(webhook_data)
        
        self.failed_messages[message_id] = {
            'webhook_data': webhook_data,
            'error': error,
            'failed_at': datetime.now(),
            'attempts': self.max_retries + 1
        }
        
        # Enviar a cola de mensajes fallidos para revisión manual
        await self.send_to_dead_letter_queue(webhook_data, error)
        
        # Notificar sistemas de monitoreo
        await self.notify_permanent_failure(message_id, error)
        
    def extract_message_id(self, webhook_data: Dict) -> str:
        """Extraer ID de mensaje del webhook data"""
        try:
            entries = webhook_data.get('entry', [])
            for entry in entries:
                changes = entry.get('changes', [])
                for change in changes:
                    messages = change.get('value', {}).get('messages', [])
                    if messages:
                        return messages[0].get('id', 'unknown')
            return 'unknown'
        except Exception:
            return 'unknown'
```

## Monitoreo y Métricas

```python
# webhook_monitoring.py
from datetime import datetime, timedelta
import logging
from typing import Dict
import asyncio

class WebhookMonitor:
    def __init__(self):
        self.metrics = {
            'messages_received': 0,
            'messages_processed': 0,
            'messages_failed': 0,
            'processing_times': [],
            'error_counts': {},
            'last_message_time': None
        }
    
    async def record_message_received(self, message_type: str):
        """Registrar mensaje recibido"""
        self.metrics['messages_received'] += 1
        self.metrics['last_message_time'] = datetime.now()
        
        logging.info(f"Mensaje {message_type} recibido. Total: {self.metrics['messages_received']}")
    
    async def record_processing_time(self, processing_time_ms: float):
        """Registrar tiempo de procesamiento"""
        self.metrics['processing_times'].append(processing_time_ms)
        
        # Mantener solo las últimas 1000 mediciones
        if len(self.metrics['processing_times']) > 1000:
            self.metrics['processing_times'] = self.metrics['processing_times'][-1000:]
    
    async def record_processing_success(self):
        """Registrar procesamiento exitoso"""
        self.metrics['messages_processed'] += 1
    
    async def record_processing_error(self, error_type: str):
        """Registrar error de procesamiento"""
        self.metrics['messages_failed'] += 1
        
        if error_type not in self.metrics['error_counts']:
            self.metrics['error_counts'][error_type] = 0
        self.metrics['error_counts'][error_type] += 1
    
    async def get_health_status(self) -> Dict:
        """Obtener estado de salud del webhook"""
        now = datetime.now()
        
        # Calcular métricas
        success_rate = (
            self.metrics['messages_processed'] / 
            max(self.metrics['messages_received'], 1) * 100
        )
        
        avg_processing_time = (
            sum(self.metrics['processing_times']) / 
            max(len(self.metrics['processing_times']), 1)
        )
        
        # Verificar si hay mensajes recientes
        is_receiving_messages = (
            self.metrics['last_message_time'] and 
            now - self.metrics['last_message_time'] < timedelta(minutes=5)
        )
        
        return {
            'status': 'healthy' if success_rate > 95 and is_receiving_messages else 'warning',
            'metrics': {
                'success_rate': round(success_rate, 2),
                'messages_received': self.metrics['messages_received'],
                'messages_processed': self.metrics['messages_processed'],
                'messages_failed': self.metrics['messages_failed'],
                'avg_processing_time_ms': round(avg_processing_time, 2),
                'error_counts': self.metrics['error_counts'],
                'last_message_ago_minutes': (
                    int((now - self.metrics['last_message_time']).total_seconds() / 60)
                    if self.metrics['last_message_time'] else None
                )
            }
        }
```

## Próximos Pasos

1. **Implementar manejo multimedia**: Continuar con [Manejo de Contenido Multimedia](05-multimedia-handling.md)
2. **Configurar integración**: Seguir [Integración con Bird.com](06-bird-integration.md)
3. **Aplicar mejores prácticas**: Revisar [Mejores Prácticas](08-best-practices.md)
4. **Configurar troubleshooting**: Implementar [Guía de Resolución de Problemas](10-troubleshooting.md)

---

**Nota de Seguridad**: Todos los webhooks deben implementar verificación HMAC y manejo apropiado de errores para uso en producción.