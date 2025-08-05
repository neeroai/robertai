# 03 - Configuración Básica de AI Employees en Bird.com

## ⚠️ IMPORTANTE: Configuración Manual Únicamente

**Bird.com requiere configuración 100% manual a través de su interfaz web**. Esta guía no incluye configuración por JSON, YAML o APIs automatizadas, ya que Bird.com no soporta estos métodos.

## 📋 Prerequisitos

### Requisitos Técnicos

1. **Cuenta Bird.com**
   - Plan Business o superior
   - Acceso a AI Features habilitado
   - Créditos de OpenAI configurados

2. **Canales de Comunicación**
   - WhatsApp Business API aprobada
   - Número de teléfono verificado
   - Otros canales según necesidad

3. **Integraciones (Opcional)**
   - API keys de sistemas externos
   - Endpoints configurados
   - Documentación de APIs

### Requisitos de Negocio

1. **Definición Clara del Caso de Uso**
   - Objetivos del AI Employee
   - Alcance de funcionalidades
   - KPIs a medir

2. **Contenido Preparado**
   - FAQs documentadas
   - Políticas de empresa
   - Flujos conversacionales

3. **Equipo**
   - Product Owner
   - Technical Lead
   - Content Manager

## 🚀 Paso 1: Acceso a Bird.com

### 1.1 Login y Navegación

```
1. Acceder a https://app.bird.com
2. Ingresar credenciales
3. Navegar a Settings > AI
```

### 1.2 Verificar Permisos

Asegurarse de tener acceso a:
- ✅ AI Agents
- ✅ Knowledge Base
- ✅ Actions
- ✅ Analytics

## 🤖 Paso 2: Crear tu Primer AI Agent

### 2.1 Configuración Inicial

1. **Ir a AI Agents**
   ```
   Settings > AI > AI Agents > Create New Agent
   ```

2. **Información Básica**
   ```yaml
   Name: "Mi Primer AI Agent"
   Description: "Asistente virtual para atención al cliente"
   Type: "Customer Support"
   Status: "Draft"
   ```

3. **Seleccionar Modelo AI (En la interfaz web de Bird.com)**
   - **Model**: Seleccionar "GPT-3.5-turbo" desde el dropdown (recomendado para empezar)
   - **Temperature**: Ajustar slider a 0.7 (balance entre creatividad y consistencia)
   - **Max Tokens**: Establecer en 500 (para respuestas concisas)

### 2.2 Configuración de Personalidad

#### Display Information (Configurar en Bird.com)
- **Display Name**: Ingresar "Asistente Virtual" en el campo de nombre
- **Biography**: Escribir "Tu asistente para resolver dudas" en el campo de biografía
- **Avatar**: Subir imagen amigable usando el botón de upload

#### Personality Settings (Completar campos en Bird.com)

**Purpose** (Campo de texto largo):
```
Eres un asistente virtual amigable y profesional.
Tu objetivo es ayudar a los clientes con sus consultas
de manera eficiente y cordial.
```

**Tasks** (Lista en el campo correspondiente):
- Responder preguntas frecuentes
- Proporcionar información de productos
- Ayudar con problemas básicos
- Escalar casos complejos

**Audience** (Campo de texto):
```
Clientes actuales y potenciales que buscan
información rápida y soluciones a sus consultas.
```

**Tone** (Seleccionar opciones en la interfaz):
- Amigable y profesional
- Claro y conciso
- Empático y servicial
- Positivo y proactivo

## 📚 Paso 3: Configurar Knowledge Base

### 3.1 Crear Knowledge Base

1. **Navegar a Knowledge Base**
   ```
   Settings > AI > Knowledge Base > Add New
   ```

2. **Estructura Básica**
   ```
   Mi Knowledge Base/
   ├── Información General/
   │   └── about-company.md
   ├── Preguntas Frecuentes/
   │   ├── productos.md
   │   └── servicios.md
   └── Políticas/
       ├── envios.md
       └── devoluciones.md
   ```

### 3.2 Formato de Documentos

#### Ejemplo: about-company.md
```markdown
# Acerca de Nuestra Empresa

## ¿Quiénes somos?
Somos una empresa líder en [industria] con más de [X] años
de experiencia brindando [productos/servicios] de calidad.

## Nuestra Misión
[Descripción de la misión]

## Nuestros Valores
- Calidad
- Servicio
- Innovation
- Confianza

## Contacto
- Teléfono: [número]
- Email: [correo]
- Horario: Lunes a Viernes 9:00-18:00
```

### 3.3 Mejores Prácticas para Knowledge Base

1. **Estructura Clara**
   - Usar headers H1, H2, H3
   - Párrafos cortos
   - Listas cuando sea apropiado

2. **Contenido Optimizado**
   - Respuestas directas
   - Lenguaje simple
   - Evitar jerga técnica

3. **Actualización Regular**
   - Revisar mensualmente
   - Agregar nuevas FAQs
   - Corregir información obsoleta

## 🎯 Paso 4: Configurar Comportamiento

### 4.1 Custom Instructions

```
1. SIEMPRE saluda amablemente al inicio de la conversación
2. Identifica la necesidad del cliente antes de responder
3. Proporciona respuestas claras y concisas
4. Si no sabes algo, admítelo y ofrece alternativas
5. Termina preguntando si necesita algo más
```

### 4.2 Guardrails (Restricciones en Bird.com)

**Configurar en la sección "Guardrails" de Bird.com:**

**Restricciones de Contenido** (Campo de texto):
- No discutir temas políticos o controversiales
- No proporcionar consejos médicos o legales
- No compartir información confidencial
- Mantener conversaciones profesionales

**Restricciones de Negocio** (Campo de texto):
- Solo atender consultas relacionadas con la empresa
- No procesar pagos directamente
- Escalar casos complejos a humanos
- Respetar horarios de atención para escalamiento

### 4.3 Condiciones de Abandono

**Configurar en la sección "Abandonment Rules" de Bird.com:**

Abandonar conversación cuando:
- Usuario es grosero o abusivo (después de advertencia)
- Han pasado 30 minutos sin respuesta
- Se han intentado 3 veces sin éxito entender la consulta
- Usuario solicita explícitamente terminar

## 🔧 Paso 5: Configurar Canales

### 5.1 WhatsApp Business

1. **Conectar WhatsApp**
   ```
   Channels > WhatsApp > Connect New Number
   ```

2. **Configuración (Completar campos en Bird.com)**
   - **Business Name**: Ingresar "Tu Empresa" en el campo correspondiente
   - **Category**: Seleccionar "Tu Categoría" del dropdown
   - **Description**: Escribir "Descripción del servicio" en el campo de texto
   - **AI Agent**: Seleccionar "Mi Primer AI Agent" de la lista de agentes disponibles

3. **Mensaje de Bienvenida**
   ```
   ¡Hola! 👋 Bienvenido a [Empresa].
   Soy tu asistente virtual y estoy aquí para ayudarte.
   
   ¿En qué puedo ayudarte hoy?
   ```

### 5.2 Otros Canales

Similar proceso para:
- SMS
- Email
- Web Chat
- Facebook Messenger

## 🧪 Paso 6: Testing Inicial

### 6.1 Test Interno

1. **Crear Conversación de Prueba**
   ```
   Usar número de test o sandbox
   ```

2. **Casos de Prueba Básicos** (Ejecutar manualmente en Bird.com)

   **Test 1 - Saludo:**
   - Input: "Hola"
   - Expected: Saludo amigable y opciones

   **Test 2 - FAQ:**
   - Input: "¿Cuáles son sus horarios?"
   - Expected: Información correcta de horarios

   **Test 3 - Escalamiento:**
   - Input: "Quiero hablar con un humano"
   - Expected: Proceso de escalamiento

3. **Verificar**
   - ✅ Respuestas coherentes
   - ✅ Tono apropiado
   - ✅ Información correcta
   - ✅ Escalamiento funciona

### 6.2 Ajustes Comunes

1. **Si las respuestas son muy largas**
   - Reducir Max Tokens
   - Agregar instrucción de brevedad

2. **Si el tono no es apropiado**
   - Ajustar personality settings
   - Dar ejemplos específicos

3. **Si no encuentra información**
   - Revisar Knowledge Base
   - Mejorar estructura de documentos

## 📊 Paso 7: Configurar Analytics Básico

### 7.1 Métricas Iniciales

**Configurar en el Dashboard de Bird.com:**
- Total de conversaciones
- Mensajes por conversación
- Tiempo de respuesta
- Tasa de resolución
- Tasa de escalamiento

### 7.2 Dashboard Básico

1. **Crear Dashboard**
   ```
   Analytics > Dashboards > Create New
   ```

2. **Widgets Recomendados**
   - Conversaciones por día
   - Top consultas
   - Satisfaction score
   - Escalation reasons

## 🚀 Paso 8: Go Live

### 8.1 Checklist Pre-Launch

- [ ] AI Agent configurado y testeado
- [ ] Knowledge Base completo
- [ ] Canales conectados
- [ ] Flujos de escalamiento definidos
- [ ] Equipo entrenado
- [ ] Analytics configurado

### 8.2 Soft Launch

1. **Fase 1: Grupo Piloto (1 semana)**
   - 10-50 usuarios seleccionados
   - Monitoreo intensivo
   - Feedback directo

2. **Fase 2: Launch Parcial (2 semanas)**
   - 25% del tráfico
   - Ajustes según métricas
   - Expansión gradual

3. **Fase 3: Launch Completo**
   - 100% del tráfico
   - Monitoreo continuo
   - Optimización ongoing

## 🔄 Paso 9: Optimización Continua

### 9.1 Revisión Semanal

1. **Analizar Métricas**
   - Identificar tendencias
   - Detectar problemas
   - Celebrar éxitos

2. **Actualizar Knowledge Base**
   - Agregar nuevas FAQs
   - Corregir información
   - Mejorar respuestas

3. **Ajustar Comportamiento**
   - Refinar personalidad
   - Mejorar flujos
   - Optimizar escalamiento

### 9.2 Feedback Loop

```
Clientes → Conversaciones → Analytics → Insights → Mejoras → Clientes
```

## 💡 Tips para el Éxito

### Do's ✅
1. Empezar simple y crecer gradualmente
2. Escuchar feedback de usuarios
3. Mantener Knowledge Base actualizado
4. Monitorear métricas constantemente
5. Celebrar pequeñas victorias

### Don'ts ❌
1. Intentar cubrir todo desde el inicio
2. Ignorar métricas negativas
3. Dejar el AI Agent sin supervisión
4. Olvidar el factor humano
5. Resistirse a hacer cambios

## 🎯 Próximos Pasos

Ahora que tienes tu AI Agent básico funcionando:

1. **[04-CONFIGURACION-AVANZADA.md](04-CONFIGURACION-AVANZADA.md)** - Para features avanzadas
2. **[05-PERSONALIDAD-Y-COMPORTAMIENTO.md](05-PERSONALIDAD-Y-COMPORTAMIENTO.md)** - Para refinar la personalidad
3. **[07-AI-ACTIONS.md](07-AI-ACTIONS.md)** - Para agregar acciones

---

**Recuerda**: La configuración básica es solo el comienzo. El verdadero valor viene de la optimización continua basada en datos reales y feedback de usuarios.