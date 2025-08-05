

# **Arquitectura de Soluciones para Agentes de IA Multimodales en WhatsApp a través de la Plataforma Bird**

## **Resumen Ejecutivo: Arquitectura de IA Multimodal en la Plataforma Bird**

### **A. El Desafío Central: Más Allá del Texto y la Imagen**

La inteligencia artificial conversacional ha evolucionado hacia modelos multimodales capaces de interpretar un espectro de entradas de datos que va más allá del texto. Modelos como GPT-4o Mini, que impulsan a los AI Employees de Bird, poseen la capacidad inherente de procesar imágenes, audio y documentos. Sin embargo, la implementación actual del marco de AI Employee dentro de la plataforma Bird abstrae gran parte de esta capacidad, presentando una interfaz simplificada que, de forma nativa, solo procesa interacciones de texto e imagen a través del canal de WhatsApp.1 Este enfoque, si bien acelera el despliegue de chatbots para casos de uso comunes, crea una barrera técnica para las organizaciones que buscan aprovechar todo el potencial multimodal de la IA para crear experiencias de cliente más ricas y eficientes. El propósito de este informe es proporcionar planos arquitectónicos detallados y viables que permitan a los equipos de desarrollo superar esta limitación y transformar sus AI Employees en agentes verdaderamente multimodales.

### **B. Las Dos Arquitecturas de Solución Primarias**

Para habilitar el procesamiento de audio, video y documentos, es necesario construir una capa de orquestación personalizada que intercepte, procese y responda a estos tipos de medios. Este informe detalla dos arquitecturas principales para lograr este objetivo, cada una con un balance distinto entre velocidad de implementación, control y complejidad:

1. **El Enfoque Centrado en Flow Builder:** Una metodología de desarrollo rápido y predominantemente visual que utiliza el Flow Builder de Bird para interceptar los mensajes multimedia entrantes. Este flujo de trabajo desvía los tipos de medios no estándar (audio, video, documentos) hacia un servicio de procesamiento de IA externo a través de una llamada HTTP, para luego reinyectar la respuesta procesada en la conversación. Se presenta como la ruta más directa y rápida para obtener valor, ideal para la mayoría de los casos de uso empresariales.  
2. **El Enfoque Impulsado por API:** Una metodología de "código primero" (code-first) que ofrece un control granular y una flexibilidad máxima. Esta arquitectura gestiona todo el ciclo de vida de la conversación de manera programática mediante el uso de webhooks y las API de Bird (principalmente Channels y Conversations). Es la solución preferida para desarrolladores que requieren una lógica conversacional altamente compleja, integraciones profundas con sistemas de backend o que están construyendo un producto central sobre la infraestructura de Bird.

### **C. Hallazgos Clave y Recomendación Estratégica**

El análisis de la plataforma Bird revela que la clave para la multimodalidad no reside en la configuración del componente "AI Employee", sino en la construcción de una canalización de datos personalizada a su alrededor. La plataforma proporciona todas las herramientas necesarias para este fin, aunque no de manera unificada en una única interfaz. El hallazgo fundamental es que la plataforma normaliza los diversos tipos de medios entrantes en estructuras de datos predecibles, exponiendo el contenido a través de una URL segura (mediaUrl), que se convierte en el pivote para cualquier integración externa.

La recomendación estratégica para la mayoría de las organizaciones es adoptar el **Enfoque Centrado en Flow Builder**. Esta arquitectura logra un equilibrio óptimo entre potencia, velocidad de implementación y bajo mantenimiento. Permite a los equipos aprovechar la robustez del entorno de ejecución gestionado de Bird mientras delegan la lógica de IA especializada a un microservicio externo, que puede ser desarrollado y mantenido de forma independiente. El enfoque impulsado por API se reserva para escenarios que demandan un nivel de personalización y control que excede las capacidades del entorno visual de Flow Builder.

## **Análisis Fundacional: Deconstruyendo el Manejo de Medios de WhatsApp en Bird**

### **A. El Marco de AI Employee: Capacidades y Limitaciones**

El marco de AI Employee de Bird está diseñado para ofrecer una solución de soporte automatizado y disponible 24/7.1 Sus funciones principales incluyen la resolución autónoma de consultas de clientes, la ejecución de tareas administrativas como la programación de citas y la asistencia en compras con recomendaciones de productos.1 La configuración estándar es un proceso sencillo que implica dos componentes clave: la instalación de una integración con OpenAI para proporcionar la capacidad de razonamiento del agente y la creación de una base de conocimientos (Knowledge Base) que sirve como fuente de información para responder a las preguntas de los clientes.2

Este diseño deliberadamente simplificado es una abstracción poderosa. Facilita a las empresas el despliegue rápido de agentes de IA funcionales sin necesidad de una profunda experiencia en desarrollo de software. Sin embargo, esta misma abstracción que otorga facilidad de uso también impone limitaciones. Al examinar la documentación, se observa una ausencia notable de directrices sobre el manejo de tipos de medios más allá del texto y la imagen dentro del contexto de un AI Employee.1 Esta omisión no es accidental; indica que el componente "AI Employee" está optimizado para un subconjunto de interacciones conversacionales y no expone directamente los controles de bajo nivel necesarios para gestionar flujos de datos multimodales complejos como audio o video. Por lo tanto, para alcanzar los objetivos de la consulta, es imperativo mirar más allá de la interfaz de configuración del AI Employee y operar en una capa más fundamental de la plataforma, donde los datos de los mensajes se manejan en su forma más cruda.

### **B. La Capa de Datos del Canal de WhatsApp: Cómo Bird Percibe los Medios**

Para construir una solución multimodal, primero se debe comprender con precisión cómo la plataforma Bird interpreta y estructura los datos de un mensaje entrante de WhatsApp. La documentación de la API de Channels es fundamental en este aspecto, ya que proporciona los esquemas JSON exactos que se reciben a través de webhooks cuando un usuario final envía diferentes tipos de contenido.3

El análisis de estos esquemas revela una decisión de diseño crucial por parte de Bird: la normalización de los medios. Si bien una imagen se trata como un tipo distinto, la mayoría de los otros formatos de archivo se agrupan bajo una categoría común.

* **Imágenes:** Un mensaje con una imagen llega con un objeto body cuyo type es "image". Dentro de este, un objeto image contiene un array images, donde cada elemento tiene una mediaUrl que apunta al activo.3  
* **Audio:** Un mensaje de voz o un archivo de audio llega con un body.type de "file". El objeto file contiene un array files, y cada elemento especifica el contentType (por ejemplo, "audio/ogg") y la mediaUrl correspondiente.3  
* **Video:** De manera similar al audio, un archivo de video se representa con un body.type de "file". El contentType dentro del array files indicará el tipo de video (por ejemplo, "video/mp4"), junto con su mediaUrl.3  
* **Documentos:** Los documentos (PDF, DOCX, etc.) siguen el mismo patrón. El body.type es "file", y el contentType (por ejemplo, "application/pdf") y la mediaUrl se encuentran en el array files.3

Esta estandarización es la piedra angular que permite la arquitectura de la solución. Significa que, en la capa de intercepción inicial, no es necesario construir una lógica completamente separada para un video, un archivo de audio o un documento. El flujo de trabajo puede tener una única rama para manejar "archivos" y luego usar el campo contentType para una diferenciación más fina si es necesario. Esta normalización simplifica drásticamente el diseño de la lógica de enrutamiento y procesamiento.

### **C. La mediaUrl: La Clave Universal para el Contenido del Usuario**

En cada uno de los esquemas de mensajes multimedia, el elemento de datos más importante es la mediaUrl. Esta URL no es un simple enlace; es un identificador seguro y de tiempo limitado para el activo multimedia que el usuario ha enviado, alojado temporalmente en la infraestructura de Bird.3 Este mecanismo es análogo al proceso de carga de medios para mensajes salientes, donde una aplicación primero solicita una URL de carga pre-firmada a Bird para subir un archivo, y luego usa la

mediaUrl resultante para incluir ese archivo en un mensaje.3

La mediaUrl funciona como un contrato de API. La plataforma Bird garantiza que, durante un período de validez, el activo del usuario será accesible para otro proceso autorizado, como el servicio de IA externo que se construirá. Este concepto permite un desacoplamiento fundamental entre la recepción del mensaje y el procesamiento del medio. La lógica de la aplicación no necesita manejar directamente los datos binarios del archivo en el momento de la recepción. En su lugar, puede tratar el manejo de medios como un proceso transaccional y predecible:

1. Recibir la notificación del mensaje.  
2. Extraer la mediaUrl del payload JSON.  
3. Pasar esta URL como un puntero al servicio que sabe cómo consumirla.

Esta arquitectura basada en punteros es eficiente, segura y escalable, y constituye la base de las dos soluciones que se detallan a continuación.

## **La Ruta Principal: Aumentando los AI Employees a través de Flow Builder para una Multimodalidad Completa**

Este enfoque utiliza las herramientas visuales de Bird para construir una canalización de datos que enriquece la funcionalidad existente del AI Employee. Es la ruta recomendada por su rapidez y menor carga de mantenimiento.

### **A. Intercepción y Ramificación por Tipo de Medio**

El primer paso es crear un flujo que intercepte todos los mensajes entrantes del canal de WhatsApp y los enrute según su tipo de contenido.

1. **Crear un Flujo:** En el panel de Bird, navegue hasta Flow Builder y cree un nuevo flujo personalizado.  
2. **Seleccionar el Disparador (Trigger):** Elija el disparador Omnichannel.4 Este disparador es esencial porque permite que un solo flujo maneje mensajes de múltiples canales y, lo que es más importante, expone variables que identifican el tipo de contenido del mensaje.  
3. **Añadir un Paso de Ramificación (Branch):** Inmediatamente después del disparador, agregue un paso Branch.4 Este paso actuará como el centro de clasificación de nuestro flujo.  
4. **Configurar las Ramas:** En lugar de ramificar según el contenido del mensaje, configure el paso para usar una "Condición personalizada". La variable clave a utilizar aquí es {{conversationMessageType}}.4 Esta variable, disponible gracias al disparador  
   Omnichannel, contiene el tipo de contenido del mensaje entrante (por ejemplo, "audio", "video", "file", "text").  
   * **Rama de Audio:** Cree una rama donde la condición sea {{conversationMessageType}} es igual a audio.  
   * **Rama de Video:** Cree otra rama donde {{conversationMessageType}} es igual a video.  
   * **Rama de Documentos:** Cree una tercera rama donde {{conversationMessageType}} es igual a file.  
   * **Rama Predeterminada (Else):** La rama Else capturará todo lo demás, principalmente mensajes de texto e imágenes. En esta rama, puede colocar su paso de "AI Employee" existente para mantener la funcionalidad actual sin cambios.

Este diseño de ramificación es posible porque Flow Builder no es solo un autómata de estados, sino un motor de transformación y enrutamiento de datos. Las variables como {{conversationMessageType}} y las variables de contenido específicas ({{messageAudio}}, {{messageVideo}}, {{messageFile}}) 4 actúan como el pegamento que conecta los datos brutos del canal con la lógica del flujo de trabajo, convirtiendo a Flow Builder en una plataforma de integración capaz.

### **B. El Paso "Call HTTP Endpoint": La Puerta de Enlace a la IA Externa**

Dentro de cada una de las nuevas ramas de medios (audio, video, documentos), el componente central será el paso Call HTTP endpoint.5 Este paso permite que el flujo de Bird se comunique con cualquier servicio web externo, que en este caso será nuestro procesador de IA multimodal.

La configuración de este paso es la siguiente:

1. **Método:** Establezca el método HTTP en POST.  
2. **URL:** Ingrese la URL del punto final de su servicio de procesamiento externo. Se recomienda encarecidamente utilizar una arquitectura de funciones sin servidor (serverless) como AWS Lambda o Google Cloud Functions para este servicio.  
3. **Cuerpo de la Solicitud (Request Body):** Construya un payload JSON que se enviará al servicio externo. Este payload debe contener la información esencial para el procesamiento. Lo más importante es la URL del medio.  
   * Para la rama de audio, el cuerpo podría ser: {"media\_url": "{{messageAudio}}", "conversation\_id": "{{conversation.id}}"}.  
   * Para la rama de video: {"media\_url": "{{messageVideo}}", "conversation\_id": "{{conversation.id}}"}.  
   * Para la rama de documentos: {"media\_url": "{{messageFile}}", "conversation\_id": "{{conversation.id}}"}.

El principio de un flujo que orquesta llamadas a API externas es un patrón poderoso dentro de la plataforma Bird. Ejemplos como la integración con webhooks de WooCommerce 6 o la creación de funciones personalizadas que llaman a la propia API de Bird 7 demuestran la flexibilidad de este enfoque para extender las capacidades de la plataforma.

### **C. Plano Arquitectónico: El Servicio Externo de Procesamiento Multimodal**

El servicio externo es el "cerebro" de la operación multimodal. Es una pieza de código que se ejecuta fuera de Bird y es responsable de interactuar con la API del modelo de IA.

Pila Tecnológica Recomendada:  
Funciones sin servidor (AWS Lambda, Google Cloud Functions, Azure Functions) son ideales debido a su escalabilidad automática, modelo de pago por uso y facilidad de despliegue.  
**Lógica Central del Servicio (Paso a Paso):**

1. **Recepción de la Solicitud:** La función se activa mediante una solicitud POST desde el paso Call HTTP endpoint de Flow Builder.  
2. **Extracción de la mediaUrl:** El código analiza el cuerpo JSON de la solicitud para obtener la mediaUrl y cualquier otro dato de contexto, como el conversation\_id.  
3. **Descarga del Medio:** La función realiza una solicitud GET a la mediaUrl proporcionada. Esto descarga el archivo de audio, video o documento en la memoria de la función o en un almacenamiento temporal.  
4. **Procesamiento con IA:**  
   * **Para Audio:** Los datos de audio descargados se envían al punto final de transcripción de la API de OpenAI (Whisper). La API devuelve una transcripción de texto.  
   * **Para Video/Documentos:** El archivo se envía al punto final del modelo multimodal (por ejemplo, la API de GPT-4o con capacidades de visión). El prompt debe instruir al modelo sobre la tarea a realizar: "Describe el contenido de este video", "Extrae el nombre del cliente y el importe total de esta factura", etc.  
5. **Formateo de la Respuesta:** La salida del modelo de IA (la transcripción, la descripción del video, los datos extraídos del documento) se empaqueta en un objeto JSON limpio y estructurado. Por ejemplo: {"status": "success", "result\_type": "transcript", "data": "El cliente pregunta sobre el estado de su pedido..."}.  
6. **Retorno de la Respuesta:** La función devuelve este objeto JSON con un código de estado 200 OK al Flow Builder.

La creación de este servicio intermediario proporciona un beneficio estratégico fundamental: desacopla la lógica de negocio en Bird de la implementación específica del proveedor de IA. Si en el futuro se desea cambiar de OpenAI a otro proveedor como Google o Anthropic, solo se necesita actualizar el código de esta función externa. La configuración del Flow Builder en Bird permanece intacta, lo que evita el bloqueo del proveedor (vendor lock-in) en la capa de IA y garantiza la flexibilidad a largo plazo.

### **D. Consumo de la Respuesta de IA y Finalización del Flujo**

El ciclo se completa dentro de Flow Builder una vez que el paso Call HTTP endpoint recibe la respuesta del servicio externo.

1. **Almacenamiento de la Respuesta:** Flow Builder almacena automáticamente la respuesta JSON completa del servicio externo en una variable. Por defecto, esta variable suele estar disponible en el objeto {{http\_response}}.  
2. **Acceso a los Datos:** Se puede acceder a los datos anidados dentro de la respuesta utilizando la notación de puntos. Por ejemplo, para obtener la transcripción del ejemplo anterior, se usaría la variable {{http\_response.body.data}}.  
3. **Envío de la Respuesta al Usuario:** Agregue un paso Reply to channel message después del paso Call HTTP endpoint.4 En el cuerpo del mensaje de este paso, inserte la variable que contiene el resultado procesado. Por ejemplo: "He procesado su mensaje de voz. La transcripción es:  
   {{http\_response.body.data}}".  
4. **Pasos Finales:** Después de enviar la respuesta, el flujo puede terminar con un paso End of flow o puede continuar con lógica adicional, como crear un ticket en Inbox 4 y agregar la transcripción o el análisis como una nota interna para los agentes humanos.

## **Implementación Avanzada: Orquestación Directa con API para Conversaciones Multimodales**

Este enfoque ofrece el máximo control y es adecuado para escenarios con requisitos de lógica complejos o integraciones profundas.

### **A. La API de Channels como Motor Principal**

En lugar de Flow Builder, esta arquitectura se basa en un webhook personalizado que actúa como el punto de entrada para toda la lógica de la aplicación.

1. **Configuración del Webhook:** En la configuración de desarrollador de Bird, se crea una suscripción de webhook que escuche los eventos conversation.created y conversation.updated.8 La URL de este webhook apuntará a su propia aplicación de backend.  
2. **Uso de la API de Channels:** Aunque el evento proviene del servicio de conversaciones, para el manejo directo de mensajes, la **API de Channels** es la herramienta preferida. Su documentación proporciona los esquemas JSON más explícitos y detallados para los mensajes multimedia entrantes.3  
3. Lógica del Manejador de Webhooks: La aplicación de backend que recibe la notificación del webhook debe implementar la siguiente lógica:  
   a. Validar y analizar el payload JSON entrante.  
   b. Identificar el tipo de mensaje y extraer la mediaUrl, al igual que en el enfoque de Flow Builder.  
   c. Invocar al mismo servicio de procesamiento de IA externo descrito en la Sección III.C.  
   d. Una vez recibida la respuesta del servicio de IA, utilizar el punto final POST /workspaces/{workspaceId}/channels/{channelId}/messages de la API de Channels 3 para enviar un mensaje de respuesta al usuario en WhatsApp.

La elección entre Flow Builder y una implementación de API directa representa un compromiso fundamental entre la facilidad de un entorno de ejecución gestionado y el poder del control total. La documentación de Flow Builder 4 muestra una plataforma que abstrae la gestión del estado, los reintentos y la ejecución. Por el contrario, la documentación de la API 3 revela un conjunto de herramientas de bajo nivel que otorgan al desarrollador un control absoluto, pero también la responsabilidad total sobre la implementación de esa lógica. El enfoque de API solo es superior cuando la lógica conversacional es demasiado compleja o no lineal para ser modelada eficazmente en una interfaz visual, o cuando la aplicación debe integrarse profundamente con otros sistemas de backend fuera del ecosistema de Bird.

### **B. La API de Conversations para la Gestión del Estado y el Contexto**

Un error común en el enfoque de API es utilizar únicamente la API de Channels. Si bien es excelente para la entrada y salida de mensajes (I/O), una solución robusta también debe gestionar el estado y el historial de la interacción. Aquí es donde la **API de Conversations** se vuelve indispensable.8

La API de Channels es transaccional y se centra en el mensaje individual. La API de Conversations es de estado (stateful) y se centra en el hilo de la conversación. Una arquitectura sofisticada utiliza ambas en conjunto:

* Se recibe un mensaje a través de un webhook de la **API de Channels**.  
* La aplicación lo procesa y envía una respuesta utilizando la **API de Channels**.  
* Paralelamente, la aplicación utiliza la **API de Conversations** para registrar tanto el mensaje entrante como la respuesta saliente en el hilo de conversación correcto (usando POST /v1/conversations/{id}/messages).  
* Además, puede usar la API de Conversations para actualizar el estado de la conversación (por ejemplo, de active a done), agregar etiquetas para la analítica o dejar notas internas para los agentes humanos.

Este patrón de doble API aprovecha las fortalezas de cada componente, creando no solo una serie de intercambios de mensajes desconectados, sino un historial de conversación coherente y contextual.

### **C. Arquitectura Propuesta para una Solución Impulsada por API**

Una representación visual de esta arquitectura incluiría los siguientes componentes y flujos de datos:

1. **Usuario de WhatsApp:** Inicia la interacción enviando un mensaje multimedia.  
2. **Plataforma Bird:** Recibe el mensaje y lo enruta al canal de WhatsApp configurado.  
3. **Notificación de Webhook:** Bird envía un evento (conversation.updated) a un punto final predefinido.  
4. **Aplicación Personalizada (Manejador de Webhooks):** Un servicio de backend (por ejemplo, una API REST) que recibe y procesa la notificación.  
5. **Servicio de Procesamiento de IA Externo:** La aplicación personalizada extrae la mediaUrl y la envía a este servicio para su análisis (transcripción, descripción, etc.).  
6. **Llamadas a la API de Bird:** La aplicación personalizada utiliza la respuesta de la IA para realizar dos acciones:  
   * Llamar a la **API de Channels** para enviar el mensaje de respuesta al usuario final.  
   * Llamar a la **API de Conversations** para actualizar el hilo de la conversación con los mensajes intercambiados y cualquier metadato relevante.

Este diagrama solidifica el flujo de control y datos, proporcionando un plano claro para el equipo de desarrollo.

## **Recomendaciones Estratégicas y Planos de Implementación**

### **A. Matriz de Decisión: Eligiendo su Arquitectura**

La elección de la arquitectura adecuada depende de las limitaciones y prioridades del proyecto. Un líder técnico debe justificar su decisión basándose en un análisis de las compensaciones. La siguiente matriz proporciona un marco para esta decisión, pasando de la pregunta de "cómo" a la de "por qué", lo cual es característico de un análisis de alto nivel.

| Criterio | Enfoque Centrado en Flow Builder | Enfoque Impulsado por API |
| :---- | :---- | :---- |
| **Velocidad de Implementación** | **Alta:** Desarrollo visual, ejecución gestionada. Días a semanas. | **Baja:** Requiere codificación de backend, configuración de infraestructura, gestión de estado. Semanas a meses. |
| **Flexibilidad y Control** | **Alta:** Excelente para la mayoría de los casos de uso a través de funciones externas. | **Muy Alta:** Control absoluto sobre cada aspecto de la lógica, el estado y la integración. |
| **Carga de Mantenimiento** | **Baja:** La lógica es visual y gestionada por Bird. La función externa es el único código a mantener. | **Media-Alta:** Responsabilidad total sobre el código, dependencias, infraestructura y tiempo de actividad. |
| **Experiencia Requerida** | Dominio de la plataforma Bird, conocimientos básicos de API/funciones sin servidor. | Desarrollo avanzado de backend, diseño de API, gestión de infraestructura. |
| **Escalabilidad** | **Buena:** Escala con la plataforma Bird. La función externa es el posible cuello de botella a gestionar. | **Excelente:** La escalabilidad se diseña a medida para satisfacer demandas específicas. |
| **Ideal Para** | Prototipado rápido, la mayoría de los casos de uso empresariales estándar, equipos que desean minimizar el código personalizado. | Lógica conversacional altamente compleja o no lineal, integración profunda con sistemas propietarios, construcción de un producto central sobre la infraestructura de Bird. |

### **B. Hoja de Ruta de Implementación por Fases**

Se recomienda un enfoque por fases para mitigar riesgos y demostrar valor de forma incremental.

1. **Fase 1 (Prueba de Concepto):** Implementar únicamente la transcripción de audio utilizando el enfoque de Flow Builder. Este paso valida toda la canalización con el caso de uso multimodal más simple y de mayor valor inmediato.  
2. **Fase 2 (Expansión):** Añadir la lógica de ramificación y procesamiento para video y documentos, reutilizando el patrón establecido en la Fase 1\.  
3. **Fase 3 (Refinamiento):** Mejorar el manejo de errores en el flujo y en el servicio externo. Añadir lógica de respuesta más sofisticada (por ejemplo, respuestas diferentes según el contenido extraído). Integrar la creación de tickets en Inbox para una escalada fluida a agentes humanos.  
4. **Fase 4 (Evaluación):** Después de varios meses de operación, evaluar si la complejidad de la lógica de negocio ha superado las capacidades de Flow Builder. Si es así, planificar una migración al enfoque impulsado por API, reutilizando el servicio de procesamiento de IA ya construido.

### **C. Consideraciones de Seguridad, Escalabilidad y Costo**

* **Seguridad:** La seguridad de las claves de API es primordial. Es fundamental seguir las advertencias de Bird de no codificar las claves en el código fuente ni registrarlas en repositorios públicos.11 Se debe utilizar el sistema de variables de entorno tanto en la plataforma de Bird (para las funciones de Flow Builder) como en el proveedor de la nube para el servicio externo, tal como se demuestra en los ejemplos de la documentación.7  
* **Escalabilidad:** Se deben tener en cuenta los límites de velocidad de la API de Bird 13 al diseñar la solución. El servicio externo debe estar diseñado para manejar solicitudes concurrentes, especialmente si se esperan picos de tráfico. La arquitectura sin servidor es inherentemente buena para esto, pero se deben configurar los límites de concurrencia de manera apropiada.  
* **Costo:** El costo total de la solución es una suma de tres componentes:  
  1. **Tarifas de Bird:** Costos por mensaje o por conversación según el plan contratado.  
  2. **Costos de Cómputo Externo:** Tarifas de ejecución de la función sin servidor (por ejemplo, AWS Lambda). Generalmente bajos, pero dependen del volumen.  
  3. **Costos de la API de IA:** Costos basados en el uso de tokens o por minuto de audio/video procesado por el proveedor de IA (por ejemplo, OpenAI). Este suele ser el componente de costo variable más significativo.

Un análisis financiero completo debe tener en cuenta estos tres pilares para proyectar el costo total de propiedad de la solución multimodal.

#### **Works cited**

1. AI Agents | Bird Docs, accessed August 5, 2025, [https://docs.bird.com/applications/ai-features/ai-agents](https://docs.bird.com/applications/ai-features/ai-agents)  
2. Use RCS with an AI Agent \- Bird CRM docs, accessed August 5, 2025, [https://docs.bird.com/applications/channels/channels/supported-channels/google-rcs/use-rcs-with-an-ai-agent](https://docs.bird.com/applications/channels/channels/supported-channels/google-rcs/use-rcs-with-an-ai-agent)  
3. Messaging | Bird API Docs, accessed August 5, 2025, [https://docs.bird.com/api/channels-api/api-reference/messaging](https://docs.bird.com/api/channels-api/api-reference/messaging)  
4. Getting Started with Flow Builder | Connectivity Platform \- Bird CRM docs, accessed August 5, 2025, [https://docs.bird.com/connectivity-platform/basics/getting-started-with-flow-builder](https://docs.bird.com/connectivity-platform/basics/getting-started-with-flow-builder)  
5. How to Call HTTP endpoint with SMS | Connectivity Platform \- Bird CRM docs, accessed August 5, 2025, [https://docs.bird.com/connectivity-platform/how-to-guides/how-to-call-http-endpoint-with-sms](https://docs.bird.com/connectivity-platform/how-to-guides/how-to-call-http-endpoint-with-sms)  
6. How to set up WooCommerce order notifications with Flow Builder | Connectivity Platform, accessed August 5, 2025, [https://docs.bird.com/connectivity-platform/use-cases/how-to-set-up-woocommerce-order-notifications-with-flow-builder](https://docs.bird.com/connectivity-platform/use-cases/how-to-set-up-woocommerce-order-notifications-with-flow-builder)  
7. Making an API request and formatting the results in a Flow Function | Connectivity Platform, accessed August 5, 2025, [https://docs.bird.com/connectivity-platform/advanced-functionalities/making-an-api-request-and-formatting-the-results-in-a-flow-function](https://docs.bird.com/connectivity-platform/advanced-functionalities/making-an-api-request-and-formatting-the-results-in-a-flow-function)  
8. Conversations | Bird API Docs, accessed August 5, 2025, [https://docs.bird.com/api/quickstarts/conversations](https://docs.bird.com/api/quickstarts/conversations)  
9. API reference \- Bird CRM docs, accessed August 5, 2025, [https://docs.bird.com/api/channels-api/api-reference](https://docs.bird.com/api/channels-api/api-reference)  
10. What is Flow Builder? | Connectivity Platform \- Bird CRM docs, accessed August 5, 2025, [https://docs.bird.com/connectivity-platform/basics/what-is-flow-builder](https://docs.bird.com/connectivity-platform/basics/what-is-flow-builder)  
11. MessageBird API Reference, accessed August 5, 2025, [https://developers.messagebird.com/api](https://developers.messagebird.com/api)  
12. Conversations API \- MessageBird, accessed August 5, 2025, [https://developers.messagebird.com/api/conversations/](https://developers.messagebird.com/api/conversations/)  
13. Welcome to the Bird API Docs \- Bird CRM docs, accessed August 5, 2025, [https://docs.bird.com/api](https://docs.bird.com/api)  
14. Conversations API | Bird API Docs, accessed August 5, 2025, [https://docs.bird.com/api/conversations-api](https://docs.bird.com/api/conversations-api)