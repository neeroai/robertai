**Bird API (Bird/MessageBird) y su uso con AI Employees** 

**1\. Visión general de la API de Bird** 

Bird (antes MessageBird) ofrece dos APIs principales para mensajería omnicanal: 

| API/Concepto Descripción Endpoints clave |
| ----- |
| API omnicanal que unifica los mensajes de  diferentes plataformas (WhatsApp, SMS, Email, etc.).  Permite crear conversaciones, añadir participantes y  enviar mensajes. Los mensajes son objetos con un   type y un bloque content (p. ej. text ,   image , audio ). Al recuperar mensajes, la función  getMessageContent del ejemplo de soporte de  **Conversations API**  Bird demuestra que el código accede a   message.content.text para textos y a   message.content.image.url ,   message.content.video.url ,   message.content.audio.url o   message.content.file.url para otros tipos  .  1 |
| \* **Crear conversación**  ( POST /workspaces/  {workspaceId}/  conversations ) |
| \* **Crear mensaje** ( POST /  workspaces/  {workspaceId}/  conversations/  {conversationId}/  messages ) – se utiliza tanto  para WhatsApp como para  otros canales .  2 |

1

| API/Concepto Descripción Endpoints clave |
| ----- |
| \* **Presigned upload**  ( POST /workspaces/  {workspaceId}/  conversations/  {conversationId}/  presigned-upload ) –  genera URLs para subir  archivos y medios .  3 |
| \* **Listar mensajes** ( GET /  conversations/  {conversationId}/  messages ) – devuelve una  lista con elementos type ,   content ,   createdDatetime , etc.  que se pueden filtrar por  tipo .  4 |
| Abstracción de mensajes por canal. Proporciona el  mismo formato de mensaje para múltiples servicios  (WhatsApp, SMS, RCS, Email…). La documentación  especifica que los tipos de mensaje disponibles  **Channels API**  incluyen text , images , files , list ,   carousel y template , y menciona que no todos  los canales soportan todos los tipos .  5 |
| \* **Enviar mensajes de canal**  ( POST /messages ) –  admite campos como   receiver.contacts y   body con un objeto según  el tipo de mensaje. |
| \* **Supported Channels** –  lista de plataformas  (WhatsApp, SMS, Email, etc.)  con instrucciones para  configurar cada canal. |

2

| API/Concepto Descripción Endpoints clave |
| ----- |
| Paso **Fetch  Variables**,   **Call Function**,  Herramienta no‑code de Bird para definir flujos de  **Send**  interacción. Permite añadir pasos como “Recibir  **Message**,   mensaje”, “Enviar mensaje”, “Obtener variables”,  **Workflows (Flow Builder)  Condition**;  “Llamar función” o “Llamar API”. Los flujos se pueden  integrable con  desencadenar por mensajes entrantes de WhatsApp  scripts en  y otras fuentes.  JavaScript  para procesar  contenido. |
| POST /  calls ,   POST /  API para llamadas de voz y TTS, útil para respuestas  calls/{id}/  **Voice API**  en audio. Los métodos incluyen iniciar llamada,  play ,   reproducir mensaje, sintetizar texto a voz, etc.  POST /  calls/{id}/  tts , etc. |

**Estructura de los mensajes** – Los mensajes creados con la Conversations API incluyen un cuerpo ( body ) con un campo type y la información asociada. Por ejemplo, al crear un mensaje de texto se envía 2   
body: { "type": "text", "text": { "text": "Hola" } } . La documentación de soporte muestra que al recuperar mensajes el type permite distinguir textos, imágenes, vídeo, audio, archivos y 6   
ubicaciones; cada tipo posee su propio objeto con una URL o propiedades relacionadas . Para contenido multimedia, la API requiere primero generar y subir un archivo mediante una **pre‑signed upload**. El endpoint presigned-upload devuelve una URL temporal ( mediaUrl ), junto con uploadUrl y 7   
uploadFormData con claves de Amazon S3 . Una vez subido el archivo a la URL S3, se puede enviar el mensaje referenciando mediaUrl en el cuerpo del mensaje . Estas URLs son indispensables para   
8 

enviar imágenes, audio o vídeo a través de WhatsApp. 

**2\. Mensajes multimodales soportados (WhatsApp)** 

Las APIs de Bird permiten enviar y recibir diferentes tipos de contenido a través de WhatsApp. Aunque la documentación específica de cada tipo está detrás de un portal GitBook (difícil de consultar directamente), la lista de tipos de mensaje (Text, Images, Files, List, Carousel y Template) y los ejemplos accesibles permiten inferir cómo se estructuran. El soporte para cada tipo depende del canal; WhatsApp admite: 

3

| Tipo Descripción y estructura (resumen) Comentario |
| ----- |
| Soporte universal. Los  "type": "text" y un objeto text con el texto. Puede  **Texto**  AI Employees ya  **simple**  incluir botones de **reply** o **postback** dentro de actions .  responden texto  9 usando GPT‑4o.  |
| "type": "image" con un objeto image o images .  Actualmente  Generalmente se utiliza images: \[{"url": mediaUrl,   soportado por el AI  "altText": "Descripción"}\] . Para enviar la imagen se  **Imagen**  Employee; se usa para  debe generar un mediaUrl mediante presigned-upload  procesar imágenes  3  y cargar el archivo ; después se envía el mensaje incluyendo  con GPT‑4o.  esa URL . Puede combinarse con texto o botones.  8 |
| "type": "file" con objeto file que incluye url ,   Permite que el  filename y posiblemente mimeType . Igual que la imagen,  AI Employee envíe  **Archivo**  informes, facturas o  requiere pre‑signed upload. Útil para enviar PDFs, documentos  PDFs vía WhatsApp. o audios.  |
| "type": "audio" con objeto audio (p. ej. url ,   Puede usarse para  duration ). Para recibir audios, el Conversations API devuelve  transcribir notas de  **Audio**  message.content.audio.url . Para enviarlos se genera  voz (speech‑to‑text) o  6 para responder con  un mediaUrl mediante presigned-upload y se envía un  audio (text‑to‑speech).  mensaje con ese URL.  |
| Amplía la experiencia  "type": "video" con objeto video ( url , caption ).  del cliente con  **Video**  Requiere pre‑signed upload. Ideal para enviar tutoriales o  contenidos  demostraciones.  audiovisuales. |
| Permite crear  "type": "list" con un objeto que define encabezado,  interfaces  descripción, botón y secciones con opciones. Utilizado por  **Lista**  conversacionales y  WhatsApp para menús interactivos (selección de productos,  derivar flujos según la  servicios, etc.).  opción seleccionada. |
| "type": "carousel" con tarjetas (cada una con título,  Útil para mostrar  varios productos o  descripción, imagen y botones). Actualmente WhatsApp tiene  **Carrusel**  elementos de forma  soporte limitado; suele usarse en otros canales (Instagram,  visual. RCS).  |
| Útil para  "type": "template" con template.projectId y  notificaciones oficiales  **Plantilla**  como OTPs,  variables. Necesita aprobación previa de Meta. Bird permite  **(HSM)**  confirmaciones de  enviar plantillas con texto o imágenes .  10 pedidos, etc.  |
| Permite solicitar al  **Ubicación**"type": "location" con coordenadas. La API devuelve   usuario su ubicación o  message.content.location.latitude/longitude .  11 enviar una dirección.  |

4  
**3\. Conversión de AI Employees a agentes multimodales en WhatsApp** 

Los AI Employees se ejecutan dentro de la plataforma de Bird y utilizan un **workflow** (flow builder) con pasos predefinidos: recepción de mensajes, llamada al modelo GPT‑4o‑Mini y envío de respuesta. Actualmente solo procesan texto e imágenes. Para convertirlos en agentes multimodales que manejen audio, vídeo u otros tipos de contenido, se pueden explorar las siguientes estrategias: 

**3.1 Añadir pasos al workflow (Flow Builder)** 

1\.    
**Clasificar el tipo de mensaje entrante**. Mediante el paso *Fetch Variables* se puede leer las variables proporcionadas por el disparador del canal (por ejemplo, event.body.type y  

event.body.content ). Se puede añadir un paso *Condition* que redirija el flujo según el tipo ( text , image , audio , video , file , location ). 

2\.    
**Procesar audio/vídeo mediante funciones personalizadas**. Para notas de voz o vídeos, se puede 

añadir un paso *Call Function* o *Call API* que realice: 

3\.    
**Descarga del contenido**: usando la URL devuelta en message.content.audio.url o  6   
message.content.video.url . 

4\.    
**Transcripción o análisis**: llamar a una API de speech‑to‑text (p. ej. Whisper de OpenAI, Google Speech‑to‑Text) para convertir audio en texto. Para vídeo, se pueden extraer frames o audio y procesar con un servicio de análisis o transcripción. 

5\.    
**Enriquecimiento**: opcionalmente utilizar un servicio de análisis de imágenes/video para describir el 

contenido, detectar objetos, etc. El resultado se envía como texto al modelo GPT‑4o para generar la respuesta. 

6\.    
**Integrar modelos de texto‑a‑voz (TTS) para respuestas en audio**. Si se desea responder con audio, el flujo puede llamar a un servicio TTS (como el Voice API de Bird) para generar un audio a partir del texto de la respuesta. Posteriormente, se genera un mediaUrl mediante presigned 3   
upload , se sube el archivo y se envía como mensaje audio o file . 

7\.    
**Manejo de archivos**. Para adjuntar reportes o documentos (PDF, etc.), se genera un mediaUrl y se 

envía como mensaje file . Para interpretar archivos entrantes, se puede usar un paso de función que descargue el archivo, lo analice o convierta (por ejemplo, extraer texto de un PDF) y produzca una respuesta. 

8\.    
**Uso de mensajes interactivos**. Las listas y botones facilitan flujos de autogestión. El workflow puede enviar mensajes list para preguntar al usuario qué tipo de respuesta desea (texto, audio, resumen en PDF) y tratar cada opción en ramas diferentes. 

9\.    
**Seguimiento de contexto en la conversación**. Se puede usar el Conversations API para almacenar transcripciones y resultados en variables de contexto; con list conversation messages se 4   
recupera el histórico . 

**3.2 Modificar componentes del workflow ya desplegado** 

Si el AI Employee ya está activo en el canal de WhatsApp, se pueden hacer las siguientes modificaciones: 

•    
**Actualizar el paso “Recibir mensaje”** para incluir audio y file como tipos aceptados. •    
**Añadir un paso “Pre‑signed upload”** al enviar respuestas con medios. Cuando el flujo genere un audio o documento de respuesta, debe llamar a POST /presigned-upload y subir el archivo 

5  
utilizando los datos devueltos; luego utilizar el mediaUrl en el cuerpo del mensaje para enviarlo 

12 

•    
. 

**Crear funciones reutilizables** para convertir audio a texto, extraer texto de PDFs o sintetizar voz. Estas funciones pueden almacenarse en el AI Hub y ser referenciadas en múltiples flujos. •    
**Implementar un paso de “condición de canal”** para asegurar que ciertos tipos de mensajes (por ejemplo, carouseles) solo se envíen cuando el canal lo soporta. 

**3.3 Uso directo de las APIs (Conversations o Channels) desde un servicio externo** 

En lugar de configurar todo en el Flow Builder, una empresa puede crear un microservicio que actúe como “cerebro” del AI Employee y utilice las APIs de Bird de forma programática: 

1\.    
**Recibir webhooks de mensajes entrantes**. Bird puede enviar eventos a un webhook cuando llega 

un mensaje de WhatsApp. El servicio externo recibe el payload y lee type y content para determinar si es texto, imagen, audio, etc. 

2\.  3\.    
**Procesar el contenido**. Según el tipo: 

**Texto o imagen**: enviar el texto o la descripción generada (para imágenes se puede usar GPT‑4o‑Vision) al modelo GPT‑4o‑Mini para obtener la respuesta. 

4\.    
**Audio/vídeo**: descargar el archivo desde message.content.audio.url o  1   
message.content.video.url , transcribir y luego procesar la transcripción con GPT‑4o. 5\.    
**Archivos**: descargar y analizar (por ejemplo, OCR para PDF o imágenes). 

6\.    
**Generar la respuesta**. Basándose en la transcripción o análisis, llamar a GPT‑4o‑Mini u otro modelo para crear una respuesta. Opcionalmente generar audio (TTS) o documentos. 

7\.    
**Enviar la respuesta**. Construir un mensaje de conversación con el tipo adecuado ( text , image ,  audio , etc.) y enviarlo usando POST /workspaces/{workspaceId}/conversations/ 3 8   
{conversationId}/messages . Para medios se sigue el flujo de presigned-upload . El 

cuerpo del mensaje en la API requiere especificar los destinatarios ( recipients ) y el  2   
participantId del AI Employee . 

**3.4 Integración con el Voice API** 

El Voice API de Bird permite iniciar llamadas y reproducir mensajes de voz o texto‑a‑voz. Para un agente realmente multimodal, se puede ofrecer al usuario la opción de recibir una llamada con una respuesta sintetizada. Pasos a seguir: 

1\.    
Cuando el usuario solicite “escuchar la respuesta”, el flujo llama a POST /calls con el número de teléfono y genera una llamada.  

2\.    
Utiliza POST /calls/{id}/tts para reproducir el texto generado por el AI Employee como habla 

(TTS).  

3\.    
Opcionalmente permite que el usuario interactúe mediante DTMF o que transfiera a un agente humano. 

**4\. Consideraciones finales** 

•    
**Gestión de permisos y credenciales**. Las APIs requieren un AccessKey asociado al workspace. Es importante almacenarlo de forma segura y usar la cabecera Authorization: AccessKey {key} 7   
en cada solicitud . 

6  
•    
**Limitaciones del canal**. WhatsApp impone límites en el tamaño y tipo de medios. Al utilizar listas, 

carruseles o plantillas se debe verificar que el tipo esté permitido.  

•    
**Control de la ventana de atención**. WhatsApp Business dispone de una **ventana de servicio de 24 horas**; fuera de esa ventana, solo se pueden enviar mensajes usando plantillas aprobadas. Es importante que el workflow maneje el tiempo del último mensaje y elija la plantilla apropiada o solicite al usuario que reabra el chat. 

•    
**Privacidad y almacenamiento**. Al procesar medios (audio, vídeo), se almacenan archivos 

temporales en S3. Deben definirse políticas de retención y cifrado adecuados.  

•    
**Monitoreo y fallback**. Si la transcripción o generación de respuesta falla, el flujo debe enviar un 

mensaje de error claro o transferir la conversación a un agente humano.  

**5\. Resumen de opciones para convertir AI Employees en agentes multimodales (WhatsApp)** 

1\.    
**Habilitar y manejar tipos de mensajes adicionales** – Extender el workflow para aceptar mensajes  audio , video , file , list , template y location además de text e image . Leer el  type de cada mensaje y usar diferentes ramas en el flujo para procesarlos.  

2\.    
**Implementar transcripción y análisis** – Usar pasos *Call Function* o servicios externos para transcribir notas de voz o analizar vídeos e imágenes. Pasar el resultado al modelo GPT‑4o‑Mini para obtener una respuesta.  

3\.    
**Generar respuestas en medios alternativos** – Crear funciones para sintetizar voz (TTS) o generar documentos (PDF, imágenes) a partir de la respuesta. Utilizar presigned-upload para subir el 13   
archivo y enviarlo como mensaje de audio o archivo .  

4\.    
**Utilizar mensajes interactivos** – Enviar listas o menús para que el usuario seleccione el formato de respuesta (texto, audio, PDF) o el tema de interés.  

5\.    
**Modificar acciones de AI Employee** – Dentro de la AI hub, personalizar tareas y guardrails para que 

el modelo pueda llamar funciones y manejar archivos. Configurar el límite de tokens y la temperatura del modelo para respuestas concisas.  

6\.    
**Integrar microservicio externo** – Construir un servicio que actúe como intermediario entre Bird y el modelo, reciba los webhooks, procese los medios, llame a GPT‑4o‑Mini y responda a través de la API de Bird. Permite un mayor control y la incorporación de otras inteligencias artificiales.  7\.    
**Aprovechar el Voice API** – Ofrecer la opción de llamadas salientes con respuestas sintetizadas o confirmaciones mediante TTS.  

Implementando estas estrategias y aprovechando las capacidades de la Conversations y Channels API de Bird, los AI   Employees podrán evolucionar de procesar solamente texto e imágenes a convertirse en agentes verdaderamente multimodales capaces de gestionar audio, vídeo, archivos y mensajes interactivos a través de WhatsApp y otros canales. 

1 4 6 11 Center   
Making an API request and formatting the results in a Flow Function \- MessageBird Support 

https://messagebird-support-center.framer.website/support-center/omnichannel-and-connectivity/flow-builder/making-an-api request-and-formatting-the-results-in-a-flow-function 

2 10   
Create conversation message | Bird API Docs 

https://docs.bird.com/api/conversations-api/api-reference/conversations-messaging/create-conversation-message 7  
3 7 8 12 13   
Create pre-signed upload | Bird API Docs 

https://docs.bird.com/api/conversations-api/api-reference/conversations-messaging/create-pre-signed-upload 

5   
Message types | Bird API Docs 

https://docs.bird.com/api/channels-api/message-types 

9   
Text | Bird API Docs 

https://docs.bird.com/api/channels-api/message-types/text 8