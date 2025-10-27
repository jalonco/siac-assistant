# SIAC Assistant - Instrucciones de Conexión a ChatGPT
# Guía completa para configurar el conector MCP en ChatGPT

## 🎯 **CONFIGURACIÓN DEL CONECTOR EN CHATGPT**

### **📋 Información del Conector:**
- **Nombre:** SIAC Assistant
- **URL del Conector:** `https://api.siac-app.com/mcp`
- **Tipo:** MCP (Model Context Protocol)
- **Autenticación:** OAuth 2.1 con PKCE
- **Scope Requerido:** `siac.user.full_access`

---

## 🚀 **PASOS PARA CONFIGURAR EL CONECTOR**

### **Paso 1: Acceder a Configuración de Conectores**
1. Abre ChatGPT en tu navegador
2. Haz clic en tu perfil (esquina superior derecha)
3. Selecciona **"Settings"** (Configuración)
4. En el menú lateral, haz clic en **"Connectors"** (Conectores)

### **Paso 2: Crear Nuevo Conector**
1. Haz clic en **"Create Connector"** (Crear Conector)
2. Selecciona **"MCP"** como tipo de conector
3. Completa los siguientes campos:

#### **Configuración Básica:**
- **Name:** `SIAC Assistant`
- **Description:** `Asistente inteligente para gestión de campañas WhatsApp y plantillas de mensajes`
- **URL:** `https://api.siac-app.com/mcp`

#### **Configuración de Autenticación:**
- **Auth Type:** `OAuth 2.1 with PKCE`
- **Issuer URL:** `https://auth.siac-app.com`
- **Resource Server URL:** `https://api.siac-app.com/mcp`
- **Required Scope:** `siac.user.full_access`

### **Paso 3: Configurar Custom UX**
1. En la sección **"Custom UX"**, habilita **"Enable Custom UI Components"**
2. Configura la **Base URL:** `https://api.siac-app.com`
3. Los componentes se cargarán automáticamente desde:
   - `https://api.siac-app.com/web/dist/template-validation-card.js`
   - `https://api.siac-app.com/web/dist/broadcast-confirmation-card.js`
   - `https://api.siac-app.com/web/dist/campaign-metrics-widget.js`
   - `https://api.siac-app.com/web/dist/authentication-required-card.js`

### **Paso 4: Guardar y Probar**
1. Haz clic en **"Save"** (Guardar)
2. ChatGPT intentará conectarse al servidor MCP
3. Si la conexión es exitosa, verás un mensaje de confirmación

---

## 🔧 **HERRAMIENTAS DISPONIBLES**

### **🔍 Herramientas de Lectura (Read-Only):**
1. **`siac.validate_template`**
   - Valida plantillas de WhatsApp
   - Muestra preview y errores de Meta
   - **UI Widget:** TemplateValidationCard

2. **`siac.get_campaign_metrics`**
   - Obtiene métricas de campañas
   - Muestra calidad y rendimiento
   - **UI Widget:** CampaignMetricsWidget

### **✏️ Herramientas de Escritura (Requieren Autenticación):**
1. **`siac.register_template`**
   - Registra nuevas plantillas
   - Requiere OAuth 2.1
   - **UI Widget:** TemplateValidationCard (botón "Registrar Plantilla")

2. **`siac.send_broadcast`**
   - Envía campañas de difusión
   - Requiere OAuth 2.1
   - **UI Widget:** BroadcastConfirmationCard

---

## 🔐 **FLUJO DE AUTENTICACIÓN**

### **Primera Vez (Sin Autenticación):**
1. ChatGPT mostrará el componente `AuthenticationRequiredCard`
2. Haz clic en **"Conectar Cuenta SIAC"**
3. Se abrirá el flujo OAuth 2.1 con PKCE
4. Autoriza el acceso con el scope `siac.user.full_access`
5. ChatGPT guardará el token de acceso

### **Sesiones Posteriores:**
- El token se renovará automáticamente
- No necesitarás volver a autenticarte
- Las herramientas protegidas funcionarán sin interrupciones

---

## 🎨 **COMPONENTES UI DISPONIBLES**

### **1. TemplateValidationCard (Inline)**
- **Propósito:** Validar y registrar plantillas
- **Acciones:** 
  - ✅ Validación exitosa → Botón "Registrar Plantilla"
  - ❌ Validación fallida → Botón "Corregir Prompt"

### **2. BroadcastConfirmationCard (Inline)**
- **Propósito:** Confirmar envío de campañas
- **Acciones:** Botón "Ver Métricas Detalladas"

### **3. CampaignMetricsWidget (Fullscreen)**
- **Propósito:** Dashboard completo de métricas
- **Acciones:** Filtros de tiempo, navegación

### **4. AuthenticationRequiredCard (Inline)**
- **Propósito:** Activar flujo OAuth 2.1
- **Acciones:** Botón "Conectar Cuenta SIAC"

---

## 🔄 **ACTUALIZACIÓN DEL CONECTOR**

### **Cuando Cambiar Metadatos de Herramientas:**
Si modificas las herramientas en el servidor MCP:

1. Ve a **Settings → Connectors**
2. Encuentra **"SIAC Assistant"**
3. Haz clic en **"Refresh"** (Actualizar)
4. ChatGPT detectará los cambios automáticamente

### **Cuando Cambiar Componentes UI:**
Si modificas los componentes frontend:

1. Reconstruye los componentes: `npm run build` (en directorio `web/`)
2. Redespliega el servidor: `./deploy_to_vps.sh`
3. Refresca el conector en ChatGPT

---

## 🚨 **SOLUCIÓN DE PROBLEMAS**

### **Error: "No se puede conectar al servidor"**
1. Verifica que el servidor esté ejecutándose: `./verify_deployment.sh`
2. Comprueba la URL: `https://api.siac-app.com/mcp`
3. Verifica el certificado SSL

### **Error: "Autenticación requerida"**
1. Asegúrate de que el flujo OAuth 2.1 esté configurado
2. Verifica el scope: `siac.user.full_access`
3. Intenta desconectar y reconectar la cuenta

### **Error: "Componentes UI no cargan"**
1. Verifica la Base URL: `https://api.siac-app.com`
2. Comprueba que los archivos JS estén disponibles
3. Revisa la consola del navegador para errores

### **Error: "Herramientas no disponibles"**
1. Refresca el conector en ChatGPT
2. Verifica que el servidor MCP esté respondiendo
3. Comprueba los logs del servidor

---

## 📊 **VERIFICACIÓN DE FUNCIONAMIENTO**

### **Comandos de Prueba:**
```bash
# Verificar servidor
curl -I https://api.siac-app.com/health

# Verificar MCP
curl https://api.siac-app.com/mcp

# Verificar componentes UI
curl -I https://api.siac-app.com/web/dist/template-validation-card.js
```

### **Pruebas en ChatGPT:**
1. **Prueba básica:** "Valida esta plantilla de WhatsApp: 'Hola {{nombre}}, tu pedido está listo'"
2. **Prueba de métricas:** "Muéstrame las métricas de la campaña más reciente"
3. **Prueba de autenticación:** Intenta usar una herramienta protegida

---

## ✅ **CHECKLIST DE CONFIGURACIÓN**

- [ ] Servidor MCP desplegado y funcionando
- [ ] Certificado SSL configurado
- [ ] Conector creado en ChatGPT
- [ ] URL configurada: `https://api.siac-app.com/mcp`
- [ ] OAuth 2.1 configurado
- [ ] Base URL configurada: `https://api.siac-app.com`
- [ ] Componentes UI cargando correctamente
- [ ] Herramientas disponibles en ChatGPT
- [ ] Autenticación funcionando
- [ ] Pruebas básicas exitosas

---

## 🎉 **¡LISTO PARA USAR!**

Una vez completada la configuración, podrás:

- ✅ Validar plantillas de WhatsApp
- ✅ Registrar nuevas plantillas
- ✅ Enviar campañas de difusión
- ✅ Ver métricas detalladas
- ✅ Gestionar campañas desde ChatGPT

**¡El SIAC Assistant está listo para ayudarte con la gestión de campañas WhatsApp!**



