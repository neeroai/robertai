# Manejo de Contenido Multimedia - WhatsApp Business API

## Introducción

WhatsApp Business API soporta una amplia gama de contenido multimedia que permite crear experiencias conversacionales ricas. Esta guía cubre el manejo completo de archivos multimedia para integración con Bird.com AI Employees.

## Formatos Soportados y Límites

### 1. Especificaciones Técnicas

```yaml
Imágenes:
  Formatos: JPEG, PNG, WebP
  Tamaño máximo: 5MB
  Resolución máxima: 4096x4096px
  Resolución recomendada: 1080x1080px
  Relación de aspecto: Cualquiera
  
Videos:
  Formatos: MP4, 3GPP
  Tamaño máximo: 16MB
  Duración máxima: 90 segundos
  Resolución máxima: 1920x1080px
  Codec recomendado: H.264
  
Audio:
  Formatos: AAC, M4A, AMRNB, MP3, OGG, OPUS
  Tamaño máximo: 16MB
  Duración máxima: 16 minutos
  Bitrate recomendado: 128kbps
  
Documentos:
  Formatos: PDF, DOC, DOCX, PPT, PPTX, XLS, XLSX
  Tamaño máximo: 100MB
  Páginas máximas: Sin límite oficial
```

## Gestión de Archivos Multimedia

### 1. Sistema de Upload y Gestión

```python
# multimedia_manager.py
import aiohttp
import aiofiles
import asyncio
from typing import Optional, Dict, Tuple, BinaryIO
import mimetypes
import tempfile
import os
import hashlib
from datetime import datetime, timedelta

class MultimediaManager:
    def __init__(self, access_token: str, phone_number_id: str):
        self.access_token = access_token
        self.phone_number_id = phone_number_id
        self.base_url = "https://graph.facebook.com/v18.0"
        self.upload_cache = {}  # Cache de archivos subidos
        
        # Límites por tipo de archivo
        self.limits = {
            'image': {'max_size': 5 * 1024 * 1024, 'formats': ['jpeg', 'jpg', 'png', 'webp']},
            'video': {'max_size': 16 * 1024 * 1024, 'formats': ['mp4', '3gpp']},
            'audio': {'max_size': 16 * 1024 * 1024, 'formats': ['aac', 'm4a', 'amrnb', 'mp3', 'ogg', 'opus']},
            'document': {'max_size': 100 * 1024 * 1024, 'formats': ['pdf', 'doc', 'docx', 'ppt', 'pptx', 'xls', 'xlsx']}
        }
    
    async def upload_media_file(self, file_path: str, media_type: str, 
                               filename: Optional[str] = None) -> str:
        """Subir archivo multimedia y obtener media_id"""
        
        # Validar archivo
        await self._validate_media_file(file_path, media_type)
        
        # Verificar si ya está en cache
        file_hash = await self._get_file_hash(file_path)
        cached_id = self.upload_cache.get(file_hash)
        if cached_id and await self._is_media_valid(cached_id):
            return cached_id
        
        # Subir archivo
        media_id = await self._perform_upload(file_path, media_type, filename)
        
        # Guardar en cache
        self.upload_cache[file_hash] = media_id
        
        return media_id
    
    async def upload_media_bytes(self, file_data: bytes, media_type: str, 
                                filename: str, mime_type: str) -> str:
        """Subir archivo desde bytes en memoria"""
        
        # Validar datos
        await self._validate_media_bytes(file_data, media_type, mime_type)
        
        # Crear archivo temporal
        temp_file = await self._create_temp_file(file_data, filename)
        
        try:
            return await self.upload_media_file(temp_file, media_type, filename)
        finally:
            # Limpiar archivo temporal
            if os.path.exists(temp_file):
                os.unlink(temp_file)
    
    async def _validate_media_file(self, file_path: str, media_type: str):
        """Validar archivo multimedia"""
        if not os.path.exists(file_path):
            raise FileNotFoundError(f"Archivo no encontrado: {file_path}")
        
        # Verificar tamaño
        file_size = os.path.getsize(file_path)
        max_size = self.limits[media_type]['max_size']
        if file_size > max_size:
            raise ValueError(f"Archivo excede tamaño máximo: {file_size} > {max_size}")
        
        # Verificar formato
        file_extension = os.path.splitext(file_path)[1].lower().lstrip('.')
        allowed_formats = self.limits[media_type]['formats']
        if file_extension not in allowed_formats:
            raise ValueError(f"Formato no soportado: {file_extension}. Permitidos: {allowed_formats}")
    
    async def _perform_upload(self, file_path: str, media_type: str, 
                             filename: Optional[str]) -> str:
        """Realizar upload del archivo"""
        url = f"{self.base_url}/{self.phone_number_id}/media"
        
        headers = {
            'Authorization': f'Bearer {self.access_token}'
        }
        
        # Determinar filename si no se proporciona
        if not filename:
            filename = os.path.basename(file_path)
        
        # Determinar mime_type
        mime_type, _ = mimetypes.guess_type(file_path)
        if not mime_type:
            mime_type = f"{media_type}/*"
        
        # Preparar form data
        data = aiohttp.FormData()
        data.add_field('type', media_type)
        
        async with aiofiles.open(file_path, 'rb') as file:
            file_content = await file.read()
            data.add_field('file', file_content, filename=filename, content_type=mime_type)
        
        # Realizar upload
        async with aiohttp.ClientSession() as session:
            async with session.post(url, headers=headers, data=data) as response:
                if response.status == 200:
                    result = await response.json()
                    return result.get('id')
                else:
                    error_data = await response.json()
                    raise Exception(f"Error subiendo archivo: {error_data}")
    
    async def get_media_info(self, media_id: str) -> Dict:
        """Obtener información de archivo multimedia"""
        url = f"{self.base_url}/{media_id}"
        headers = {'Authorization': f'Bearer {self.access_token}'}
        
        async with aiohttp.ClientSession() as session:
            async with session.get(url, headers=headers) as response:
                if response.status == 200:
                    return await response.json()
                else:
                    raise Exception(f"Error obteniendo info de media: {response.status}")
    
    async def download_media(self, media_id: str, save_path: Optional[str] = None) -> Tuple[bytes, str]:
        """Descargar archivo multimedia"""
        # Obtener URL de descarga
        media_info = await self.get_media_info(media_id)
        download_url = media_info.get('url')
        mime_type = media_info.get('mime_type', 'application/octet-stream')
        
        if not download_url:
            raise Exception("URL de descarga no disponible")
        
        # Descargar archivo
        headers = {'Authorization': f'Bearer {self.access_token}'}
        
        async with aiohttp.ClientSession() as session:
            async with session.get(download_url, headers=headers) as response:
                if response.status == 200:
                    content = await response.read()
                    
                    # Guardar archivo si se especifica ruta
                    if save_path:
                        async with aiofiles.open(save_path, 'wb') as file:
                            await file.write(content)
                    
                    return content, mime_type
                else:
                    raise Exception(f"Error descargando archivo: {response.status}")
    
    async def _get_file_hash(self, file_path: str) -> str:
        """Calcular hash SHA256 del archivo"""
        hash_sha256 = hashlib.sha256()
        async with aiofiles.open(file_path, 'rb') as file:
            while chunk := await file.read(8192):
                hash_sha256.update(chunk)
        return hash_sha256.hexdigest()
    
    async def _is_media_valid(self, media_id: str) -> bool:
        """Verificar si media_id es válido"""
        try:
            await self.get_media_info(media_id)
            return True
        except:
            return False
```

### 2. Procesamiento de Imágenes

```python
# image_processor.py
from PIL import Image, ImageEnhance, ImageFilter
import io
import asyncio
from typing import Dict, Optional, Tuple

class ImageProcessor:
    def __init__(self, bird_client):
        self.bird_client = bird_client
        self.max_size = (1920, 1920)  # Tamaño máximo recomendado
        self.quality = 85  # Calidad JPEG
    
    async def process_incoming_image(self, image_data: bytes, 
                                   caption: str, metadata: Dict) -> Dict:
        """Procesar imagen entrante con análisis AI"""
        
        # Optimizar imagen si es necesario
        optimized_data = await self.optimize_image(image_data)
        
        # Análisis básico de imagen
        image_analysis = await self.analyze_image_properties(optimized_data)
        
        # Análisis AI con Bird.com
        ai_analysis = await self.bird_client.analyze_image({
            'image_data': optimized_data,
            'caption': caption,
            'metadata': metadata,
            'properties': image_analysis
        })
        
        return {
            'analysis': ai_analysis,
            'properties': image_analysis,
            'optimized': len(optimized_data) < len(image_data),
            'response_suggestions': await self.generate_response_suggestions(ai_analysis)
        }
    
    async def optimize_image(self, image_data: bytes) -> bytes:
        """Optimizar imagen para procesamiento"""
        try:
            # Cargar imagen
            image = Image.open(io.BytesIO(image_data))
            
            # Convertir a RGB si es necesario
            if image.mode in ('RGBA', 'P'):
                image = image.convert('RGB')
            
            # Redimensionar si es muy grande
            if image.size[0] > self.max_size[0] or image.size[1] > self.max_size[1]:
                image.thumbnail(self.max_size, Image.Resampling.LANCZOS)
            
            # Aplicar mejoras si es necesario
            if await self.needs_enhancement(image):
                image = await self.enhance_image(image)
            
            # Convertir a bytes
            output = io.BytesIO()
            image.save(output, format='JPEG', quality=self.quality, optimize=True)
            return output.getvalue()
            
        except Exception as e:
            # Si falla la optimización, devolver original
            return image_data
    
    async def analyze_image_properties(self, image_data: bytes) -> Dict:
        """Analizar propiedades básicas de la imagen"""
        image = Image.open(io.BytesIO(image_data))
        
        return {
            'width': image.width,
            'height': image.height,
            'mode': image.mode,
            'format': image.format,
            'size_bytes': len(image_data),
            'aspect_ratio': round(image.width / image.height, 2),
            'is_landscape': image.width > image.height,
            'is_square': abs(image.width - image.height) < 50
        }
    
    async def generate_response_suggestions(self, ai_analysis: Dict) -> list:
        """Generar sugerencias de respuesta basadas en el análisis"""
        suggestions = []
        
        # Sugerencias basadas en objetos detectados
        objects = ai_analysis.get('objects_detected', [])
        if objects:
            suggestions.append(f"Veo {', '.join(objects)} en la imagen")
        
        # Sugerencias basadas en texto detectado
        text_detected = ai_analysis.get('text_detected', '')
        if text_detected:
            suggestions.append(f"He extraído este texto: {text_detected}")
        
        # Sugerencias basadas en emociones/sentimiento
        sentiment = ai_analysis.get('sentiment', '')
        if sentiment:
            suggestions.append(f"La imagen transmite {sentiment}")
        
        return suggestions
```

### 3. Procesamiento de Audio

```python
# audio_processor.py
import asyncio
import tempfile
import os
from typing import Dict, Optional

class AudioProcessor:
    def __init__(self, bird_client):
        self.bird_client = bird_client
        self.supported_formats = ['aac', 'm4a', 'mp3', 'ogg', 'opus', 'wav']
        self.max_duration = 16 * 60  # 16 minutos en segundos
    
    async def process_incoming_audio(self, audio_data: bytes, 
                                   metadata: Dict) -> Dict:
        """Procesar audio entrante con transcripción y análisis"""
        
        # Validar audio
        audio_info = await self.analyze_audio_properties(audio_data)
        
        if audio_info['duration'] > self.max_duration:
            return {
                'error': f"Audio excede duración máxima de {self.max_duration/60} minutos",
                'properties': audio_info
            }
        
        # Transcripción con Bird.com AI
        transcription_result = await self.bird_client.transcribe_audio({
            'audio_data': audio_data,
            'metadata': metadata,
            'properties': audio_info
        })
        
        # Análisis de sentimientos del audio
        sentiment_analysis = await self.bird_client.analyze_audio_sentiment({
            'transcription': transcription_result.get('text', ''),
            'audio_features': audio_info
        })
        
        return {
            'transcription': transcription_result,
            'sentiment': sentiment_analysis,
            'properties': audio_info,
            'response_suggestions': await self.generate_audio_responses(
                transcription_result, sentiment_analysis
            )
        }
    
    async def analyze_audio_properties(self, audio_data: bytes) -> Dict:
        """Analizar propiedades básicas del audio"""
        # Para análisis real se necesitaría una biblioteca como librosa
        # Aquí simulamos el análisis
        
        return {
            'size_bytes': len(audio_data),
            'duration': 30.5,  # Duración estimada
            'estimated_bitrate': 128,  # kbps estimado
            'is_voice_message': True,  # Detectar si es mensaje de voz
            'quality_score': 8.5  # Calidad estimada 1-10
        }
    
    async def generate_audio_responses(self, transcription: Dict, 
                                     sentiment: Dict) -> list:
        """Generar respuestas sugeridas para audio"""
        suggestions = []
        
        text = transcription.get('text', '')
        confidence = transcription.get('confidence', 0)
        
        if confidence > 0.8:
            suggestions.append(f"Entendí: {text}")
        elif confidence > 0.5:
            suggestions.append(f"Creo que dijiste: {text}")
        else:
            suggestions.append("No pude entender claramente el audio, ¿podrías repetir?")
        
        # Respuestas basadas en sentimiento
        if sentiment.get('emotion') == 'happy':
            suggestions.append("Me alegra escucharte contento! 😊")
        elif sentiment.get('emotion') == 'frustrated':
            suggestions.append("Entiendo tu frustración, déjame ayudarte")
        
        return suggestions
```

### 4. Procesamiento de Documentos

```python
# document_processor.py
import asyncio
from typing import Dict, Optional
import PyPDF2
import docx
import io

class DocumentProcessor:
    def __init__(self, bird_client):
        self.bird_client = bird_client
        self.supported_formats = {
            'pdf': self.process_pdf,
            'docx': self.process_docx,
            'doc': self.process_doc,
            'txt': self.process_txt
        }
    
    async def process_incoming_document(self, document_data: bytes, 
                                      filename: str, mime_type: str, 
                                      metadata: Dict) -> Dict:
        """Procesar documento entrante"""
        
        # Determinar tipo de documento
        file_extension = filename.split('.')[-1].lower()
        
        if file_extension not in self.supported_formats:
            return {
                'error': f"Formato de documento no soportado: {file_extension}",
                'supported_formats': list(self.supported_formats.keys())
            }
        
        try:
            # Procesar documento según su tipo
            processor = self.supported_formats[file_extension]
            extracted_content = await processor(document_data)
            
            # Análisis con Bird.com AI
            ai_analysis = await self.bird_client.analyze_document({
                'content': extracted_content,
                'filename': filename,
                'mime_type': mime_type,
                'metadata': metadata
            })
            
            return {
                'extracted_content': extracted_content,
                'analysis': ai_analysis,
                'document_info': {
                    'filename': filename,
                    'size_bytes': len(document_data),
                    'type': file_extension,
                    'page_count': extracted_content.get('page_count', 1)
                },
                'response_suggestions': await self.generate_document_responses(ai_analysis)
            }
            
        except Exception as e:
            return {
                'error': f"Error procesando documento: {str(e)}",
                'filename': filename
            }
    
    async def process_pdf(self, pdf_data: bytes) -> Dict:
        """Procesar archivo PDF"""
        try:
            pdf_reader = PyPDF2.PdfReader(io.BytesIO(pdf_data))
            
            text_content = ""
            for page in pdf_reader.pages:
                text_content += page.extract_text() + "\n"
            
            return {
                'text': text_content.strip(),
                'page_count': len(pdf_reader.pages),
                'metadata': pdf_reader.metadata or {}
            }
            
        except Exception as e:
            raise Exception(f"Error procesando PDF: {str(e)}")
    
    async def process_docx(self, docx_data: bytes) -> Dict:
        """Procesar archivo DOCX"""
        try:
            doc = docx.Document(io.BytesIO(docx_data))
            
            text_content = ""
            for paragraph in doc.paragraphs:
                text_content += paragraph.text + "\n"
            
            return {
                'text': text_content.strip(),
                'paragraph_count': len(doc.paragraphs),
                'tables_count': len(doc.tables)
            }
            
        except Exception as e:
            raise Exception(f"Error procesando DOCX: {str(e)}")
    
    async def generate_document_responses(self, ai_analysis: Dict) -> list:
        """Generar respuestas sugeridas para documentos"""
        suggestions = []
        
        # Resumen del documento
        summary = ai_analysis.get('summary', '')
        if summary:
            suggestions.append(f"Resumen del documento: {summary}")
        
        # Temas principales
        topics = ai_analysis.get('main_topics', [])
        if topics:
            suggestions.append(f"Temas principales: {', '.join(topics)}")
        
        # Acciones sugeridas
        actions = ai_analysis.get('suggested_actions', [])
        if actions:
            suggestions.append(f"Acciones sugeridas: {', '.join(actions)}")
        
        return suggestions
```

## Optimización y Performance

### 1. Sistema de Cache Inteligente

```python
# media_cache.py
import asyncio
from datetime import datetime, timedelta
from typing import Dict, Optional
import hashlib
import json

class MediaCache:
    def __init__(self, redis_client=None):
        self.redis = redis_client
        self.local_cache = {}
        self.cache_ttl = timedelta(hours=24)  # TTL para cache local
        self.redis_ttl = timedelta(days=7)    # TTL para Redis
    
    async def get_cached_analysis(self, media_hash: str, 
                                analysis_type: str) -> Optional[Dict]:
        """Obtener análisis desde cache"""
        cache_key = f"{analysis_type}:{media_hash}"
        
        # Buscar en cache local primero
        local_result = self.local_cache.get(cache_key)
        if local_result and not self._is_expired(local_result):
            return local_result['data']
        
        # Buscar en Redis si está disponible
        if self.redis:
            redis_result = await self.redis.get(cache_key)
            if redis_result:
                data = json.loads(redis_result)
                # Actualizar cache local
                self.local_cache[cache_key] = {
                    'data': data,
                    'timestamp': datetime.now()
                }
                return data
        
        return None
    
    async def cache_analysis(self, media_hash: str, analysis_type: str, 
                           analysis_data: Dict):
        """Guardar análisis en cache"""
        cache_key = f"{analysis_type}:{media_hash}"
        
        # Guardar en cache local
        self.local_cache[cache_key] = {
            'data': analysis_data,
            'timestamp': datetime.now()
        }
        
        # Guardar en Redis si está disponible
        if self.redis:
            await self.redis.setex(
                cache_key, 
                int(self.redis_ttl.total_seconds()), 
                json.dumps(analysis_data)
            )
    
    def _is_expired(self, cache_entry: Dict) -> bool:
        """Verificar si entrada de cache ha expirado"""
        return datetime.now() - cache_entry['timestamp'] > self.cache_ttl
    
    async def cleanup_expired(self):
        """Limpiar entradas expiradas del cache local"""
        expired_keys = [
            key for key, value in self.local_cache.items()
            if self._is_expired(value)
        ]
        
        for key in expired_keys:
            del self.local_cache[key]
```

### 2. Pool de Workers para Procesamiento

```python
# media_worker_pool.py
import asyncio
from asyncio import Queue
from typing import Dict, Callable, Any
import logging

class MediaWorkerPool:
    def __init__(self, pool_size: int = 5):
        self.pool_size = pool_size
        self.workers = []
        self.task_queue = Queue(maxsize=100)
        self.results = {}
        self.running = False
    
    async def start(self):
        """Iniciar pool de workers"""
        self.running = True
        self.workers = [
            asyncio.create_task(self._worker(f"worker-{i}")) 
            for i in range(self.pool_size)
        ]
        logging.info(f"Pool de {self.pool_size} workers iniciado")
    
    async def stop(self):
        """Detener pool de workers"""
        self.running = False
        
        # Cancelar todos los workers
        for worker in self.workers:
            worker.cancel()
        
        # Esperar a que terminen
        await asyncio.gather(*self.workers, return_exceptions=True)
        logging.info("Pool de workers detenido")
    
    async def submit_task(self, task_id: str, processor: Callable, 
                         *args, **kwargs) -> str:
        """Enviar tarea al pool"""
        if self.task_queue.full():
            raise Exception("Cola de tareas llena")
        
        task_data = {
            'id': task_id,
            'processor': processor,
            'args': args,
            'kwargs': kwargs
        }
        
        await self.task_queue.put(task_data)
        return task_id
    
    async def get_result(self, task_id: str, timeout: float = 30.0) -> Any:
        """Obtener resultado de tarea"""
        start_time = asyncio.get_event_loop().time()
        
        while asyncio.get_event_loop().time() - start_time < timeout:
            if task_id in self.results:
                result = self.results.pop(task_id)
                if isinstance(result, Exception):
                    raise result
                return result
            
            await asyncio.sleep(0.1)
        
        raise TimeoutError(f"Tarea {task_id} no completada en {timeout}s")
    
    async def _worker(self, worker_name: str):
        """Worker que procesa tareas de la cola"""
        logging.info(f"Worker {worker_name} iniciado")
        
        while self.running:
            try:
                # Obtener tarea de la cola
                task_data = await asyncio.wait_for(
                    self.task_queue.get(), timeout=1.0
                )
                
                task_id = task_data['id']
                processor = task_data['processor']
                args = task_data['args']
                kwargs = task_data['kwargs']
                
                logging.info(f"Worker {worker_name} procesando tarea {task_id}")
                
                # Ejecutar tarea
                try:
                    result = await processor(*args, **kwargs)
                    self.results[task_id] = result
                except Exception as e:
                    logging.error(f"Error en tarea {task_id}: {e}")
                    self.results[task_id] = e
                
                # Marcar tarea como completada
                self.task_queue.task_done()
                
            except asyncio.TimeoutError:
                # Timeout esperando tarea - continuar
                continue
            except Exception as e:
                logging.error(f"Error en worker {worker_name}: {e}")
        
        logging.info(f"Worker {worker_name} detenido")
```

## Monitoreo y Métricas

```python
# multimedia_metrics.py
from datetime import datetime, timedelta
from typing import Dict
import logging

class MultimediaMetrics:
    def __init__(self):
        self.metrics = {
            'files_processed': 0,
            'processing_times': [],
            'file_sizes': [],
            'error_count': 0,
            'cache_hits': 0,
            'cache_misses': 0,
            'type_distribution': {},
            'errors_by_type': {}
        }
    
    async def record_file_processed(self, file_type: str, file_size: int, 
                                  processing_time: float, success: bool):
        """Registrar procesamiento de archivo"""
        self.metrics['files_processed'] += 1
        self.metrics['processing_times'].append(processing_time)
        self.metrics['file_sizes'].append(file_size)
        
        # Distribución por tipo
        if file_type not in self.metrics['type_distribution']:
            self.metrics['type_distribution'][file_type] = 0
        self.metrics['type_distribution'][file_type] += 1
        
        # Errores por tipo
        if not success:
            self.metrics['error_count'] += 1
            if file_type not in self.metrics['errors_by_type']:
                self.metrics['errors_by_type'][file_type] = 0
            self.metrics['errors_by_type'][file_type] += 1
        
        logging.info(
            f"Archivo {file_type} procesado: {file_size} bytes, "
            f"{processing_time:.2f}s, éxito: {success}"
        )
    
    async def record_cache_hit(self):
        """Registrar acierto de cache"""
        self.metrics['cache_hits'] += 1
    
    async def record_cache_miss(self):
        """Registrar fallo de cache"""
        self.metrics['cache_misses'] += 1
    
    async def get_performance_report(self) -> Dict:
        """Generar reporte de rendimiento"""
        total_files = self.metrics['files_processed']
        
        if total_files == 0:
            return {'message': 'No hay datos de procesamiento'}
        
        avg_processing_time = sum(self.metrics['processing_times']) / len(self.metrics['processing_times'])
        avg_file_size = sum(self.metrics['file_sizes']) / len(self.metrics['file_sizes'])
        success_rate = ((total_files - self.metrics['error_count']) / total_files) * 100
        
        total_cache_requests = self.metrics['cache_hits'] + self.metrics['cache_misses']
        cache_hit_rate = (
            (self.metrics['cache_hits'] / total_cache_requests * 100) 
            if total_cache_requests > 0 else 0
        )
        
        return {
            'files_processed': total_files,
            'success_rate': round(success_rate, 2),
            'avg_processing_time_seconds': round(avg_processing_time, 2),
            'avg_file_size_bytes': int(avg_file_size),
            'cache_hit_rate': round(cache_hit_rate, 2),
            'type_distribution': self.metrics['type_distribution'],
            'errors_by_type': self.metrics['errors_by_type']
        }
```

## Próximos Pasos

1. **Configurar integración**: Continuar con [Integración con Bird.com](06-bird-integration.md)
2. **Implementar API reference**: Seguir [Referencia de API](07-api-reference.md)
3. **Aplicar mejores prácticas**: Revisar [Mejores Prácticas](08-best-practices.md)
4. **Configurar troubleshooting**: Implementar [Guía de Resolución de Problemas](10-troubleshooting.md)

---

**Nota de Performance**: Todos los procesadores incluyen cache inteligente, pool de workers y métricas detalladas para uso en producción con alto volumen.