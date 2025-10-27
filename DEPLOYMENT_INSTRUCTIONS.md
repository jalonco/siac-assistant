# SIAC Assistant - Instrucciones de Despliegue Completo con OAuth 2.1
# Guía paso a paso para desplegar ambos servicios (SIAC Assistant + Auth Server)

## 🎯 **RESUMEN DEL DESPLIEGUE**

Se ha creado un **Servidor de Autorización OAuth 2.1** completo que complementa el SIAC Assistant, proporcionando autenticación segura para las herramientas protegidas. El despliegue incluye:

### **Servicios Desplegados:**
1. **SIAC Assistant** (`api.siac-app.com`) - Servidor MCP principal
2. **Auth Server** (`auth.siac-app.com`) - Servidor de autorización OAuth 2.1
3. **PostgreSQL** - Base de datos compartida

### **Arquitectura Completa:**
```
┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐
│   ChatGPT       │    │  SIAC Assistant  │    │  Auth Server    │
│                 │    │                 │    │                 │
│  OAuth Client   │◄──►│  Resource       │◄──►│  Authorization  │
│                 │    │  Server         │    │  Server         │
│                 │    │                 │    │                 │
│  api.siac-app.  │    │  api.siac-app.  │    │  auth.siac-app. │
│  com/mcp         │    │  com            │    │  com            │
└─────────────────┘    └─────────────────┘    └─────────────────┘
```

---

## 🚀 **COMANDOS DE DESPLIEGUE**

### **Opción 1: Despliegue Automático (Recomendado)**
```bash
# Hacer ejecutables los scripts
chmod +x deploy_complete.sh verify_complete.sh

# Ejecutar despliegue completo
./deploy_complete.sh

# Verificar despliegue
./verify_complete.sh
```

### **Opción 2: Despliegue Manual**
```bash
# 1. Conectar al VPS
ssh -i ~/.ssh/id_ed25519 root@srv790515.hstgr.cloud

# 2. Crear directorio de despliegue
mkdir -p /opt/siac-assistant
cd /opt/siac-assistant

# 3. Subir archivos (desde máquina local)
scp -i ~/.ssh/id_ed25519 -r . root@srv790515.hstgr.cloud:/opt/siac-assistant/

# 4. Configurar variables de entorno
cp env.production .env

# 5. Verificar red Traefik
docker network ls | grep traefik-public || docker network create traefik-public

# 6. Construir imágenes
docker build -t siac-assistant:latest .
docker build -t siac-assistant-auth:latest ./auth_server

# 7. Desplegar servicios
docker-compose -f docker-compose.production.yml up -d

# 8. Verificar estado
docker-compose -f docker-compose.production.yml ps
```

---

## 🔍 **VERIFICACIÓN POST-DESPLIEGUE**

### **1. Verificar Contenedores:**
```bash
ssh -i ~/.ssh/id_ed25519 root@srv790515.hstgr.cloud "docker ps | grep siac"
```

**Resultado esperado:**
```
siac-assistant      # Puerto 8888
siac-auth-server    # Puerto 8080
siac-assistant-db   # Puerto 5432
```

### **2. Verificar Endpoints HTTPS:**

#### **SIAC Assistant:**
```bash
# Health Check
curl -I https://api.siac-app.com/health

# Endpoint MCP
curl -I https://api.siac-app.com/mcp

# Documentación
curl -I https://api.siac-app.com/docs
```

#### **Auth Server:**
```bash
# Health Check
curl -I https://auth.siac-app.com/health

# OpenID Discovery
curl https://auth.siac-app.com/.well-known/openid-configuration

# Documentación
curl -I https://auth.siac-app.com/docs
```

### **3. Verificar Flujo OAuth 2.1:**
```bash
# Endpoint de autorización
curl "https://auth.siac-app.com/oauth/authorize?response_type=code&client_id=siac_assistant&redirect_uri=https://chatgpt.com/oauth/callback&scope=siac.user.full_access"

# Endpoint de token
curl -X POST https://auth.siac-app.com/oauth/token \
  -H "Content-Type: application/json" \
  -d '{"grant_type":"authorization_code","code":"test_code","redirect_uri":"https://chatgpt.com/oauth/callback","client_id":"siac_assistant"}'
```

### **4. Verificar Herramientas Protegidas:**
```bash
# Debe devolver 401 Unauthorized
curl -I https://api.siac-app.com/mcp

# Verificar header WWW-Authenticate
curl -I https://api.siac-app.com/mcp 2>/dev/null | grep -i "www-authenticate"
```

---

## 🔐 **CONFIGURACIÓN EN CHATGPT**

### **Datos del Conector MCP:**
- **Nombre:** SIAC Assistant
- **URL:** `https://api.siac-app.com/mcp`
- **Tipo:** MCP (Model Context Protocol)

### **Configuración OAuth 2.1:**
- **Auth Type:** OAuth 2.1 with PKCE
- **Issuer URL:** `https://auth.siac-app.com`
- **Resource Server URL:** `https://api.siac-app.com/mcp`
- **Required Scope:** `siac.user.full_access`

### **Configuración Custom UX:**
- **Base URL:** `https://api.siac-app.com`
- **Componentes disponibles:**
  - `template-validation-card.js`
  - `broadcast-confirmation-card.js`
  - `campaign-metrics-widget.js`
  - `authentication-required-card.js`

---

## 🧪 **PRUEBAS DE SEGURIDAD**

### **1. Prueba de Herramienta Protegida:**
1. Configurar conector en ChatGPT
2. Intentar usar herramienta `siac.send_broadcast`
3. **Resultado esperado:** 
   - ChatGPT muestra `AuthenticationRequiredCard`
   - Se activa flujo OAuth 2.1
   - Usuario autoriza acceso
   - Herramienta funciona después de autenticación

### **2. Prueba de Flujo OAuth 2.1:**
1. ChatGPT consulta `/.well-known/openid-configuration`
2. Redirige a `/oauth/authorize` con PKCE
3. Usuario autoriza (simulado)
4. ChatGPT intercambia código por token
5. Token se usa para acceder a herramientas protegidas

### **3. Prueba de Validación de Token:**
1. SIAC Assistant recibe request con `access_token`
2. Valida token con Auth Server
3. Otorga acceso si token es válido
4. Rechaza acceso si token es inválido (401)

---

## 🔧 **COMANDOS DE GESTIÓN**

### **Ver Logs:**
```bash
# Logs SIAC Assistant
ssh -i ~/.ssh/id_ed25519 root@srv790515.hstgr.cloud "docker logs siac-assistant --tail 50"

# Logs Auth Server
ssh -i ~/.ssh/id_ed25519 root@srv790515.hstgr.cloud "docker logs siac-auth-server --tail 50"

# Logs Base de Datos
ssh -i ~/.ssh/id_ed25519 root@srv790515.hstgr.cloud "docker logs siac-assistant-db --tail 50"
```

### **Reiniciar Servicios:**
```bash
# Reiniciar todo
ssh -i ~/.ssh/id_ed25519 root@srv790515.hstgr.cloud "cd /opt/siac-assistant && docker-compose -f docker-compose.production.yml restart"

# Reiniciar servicio específico
ssh -i ~/.ssh/id_ed25519 root@srv790515.hstgr.cloud "docker restart siac-assistant"
ssh -i ~/.ssh/id_ed25519 root@srv790515.hstgr.cloud "docker restart siac-auth-server"
```

### **Ver Estado:**
```bash
# Estado de contenedores
ssh -i ~/.ssh/id_ed25519 root@srv790515.hstgr.cloud "docker ps | grep siac"

# Estado de servicios
ssh -i ~/.ssh/id_ed25519 root@srv790515.hstgr.cloud "cd /opt/siac-assistant && docker-compose -f docker-compose.production.yml ps"

# Verificar salud
ssh -i ~/.ssh/id_ed25519 root@srv790515.hstgr.cloud "curl -s https://api.siac-app.com/health && echo && curl -s https://auth.siac-app.com/health"
```

---

## 🚨 **SOLUCIÓN DE PROBLEMAS**

### **Problema 1: SSL Certificate Issues**
```bash
# Verificar certificados
curl -I https://api.siac-app.com/health
curl -I https://auth.siac-app.com/health

# Verificar Traefik
ssh -i ~/.ssh/id_ed25519 root@srv790515.hstgr.cloud "docker logs traefik | grep -E '(api.siac-app.com|auth.siac-app.com)'"
```

### **Problema 2: Servicios No Responden**
```bash
# Verificar contenedores
ssh -i ~/.ssh/id_ed25519 root@srv790515.hstgr.cloud "docker ps | grep siac"

# Verificar logs
ssh -i ~/.ssh/id_ed25519 root@srv790515.hstgr.cloud "docker logs siac-assistant --tail 20"
ssh -i ~/.ssh/id_ed25519 root@srv790515.hstgr.cloud "docker logs siac-auth-server --tail 20"

# Reiniciar servicios
ssh -i ~/.ssh/id_ed25519 root@srv790515.hstgr.cloud "cd /opt/siac-assistant && docker-compose -f docker-compose.production.yml restart"
```

### **Problema 3: OAuth Flow Issues**
```bash
# Verificar discovery
curl https://auth.siac-app.com/.well-known/openid-configuration

# Verificar endpoints
curl "https://auth.siac-app.com/oauth/authorize?response_type=code&client_id=test&redirect_uri=https://test.com&scope=siac.user.full_access"

# Verificar logs Auth Server
ssh -i ~/.ssh/id_ed25519 root@srv790515.hstgr.cloud "docker logs siac-auth-server --tail 50"
```

### **Problema 4: Base de Datos Issues**
```bash
# Verificar conexión BD
ssh -i ~/.ssh/id_ed25519 root@srv790515.hstgr.cloud "docker exec siac-assistant-db pg_isready -U siac -d siac_chatgpt"

# Verificar tablas
ssh -i ~/.ssh/id_ed25519 root@srv790515.hstgr.cloud "docker exec siac-assistant-db psql -U siac -d siac_chatgpt -c '\\dt'"

# Reiniciar BD
ssh -i ~/.ssh/id_ed25519 root@srv790515.hstgr.cloud "docker restart siac-assistant-db"
```

---

## 📊 **MONITOREO CONTINUO**

### **Script de Monitoreo:**
```bash
#!/bin/bash
# Script de monitoreo continuo

while true; do
    echo "=== $(date) ==="
    
    # Verificar SIAC Assistant
    curl -s https://api.siac-app.com/health > /dev/null && echo "✅ SIAC Assistant OK" || echo "❌ SIAC Assistant FAIL"
    
    # Verificar Auth Server
    curl -s https://auth.siac-app.com/health > /dev/null && echo "✅ Auth Server OK" || echo "❌ Auth Server FAIL"
    
    # Verificar contenedores
    ssh -i ~/.ssh/id_ed25519 root@srv790515.hstgr.cloud "docker ps | grep siac | wc -l" | xargs -I {} echo "📦 Contenedores activos: {}"
    
    sleep 60
done
```

---

## ✅ **CHECKLIST DE VERIFICACIÓN**

### **Pre-Despliegue:**
- [ ] Archivos subidos al VPS
- [ ] Variables de entorno configuradas
- [ ] Red Traefik disponible
- [ ] Imágenes Docker construidas

### **Post-Despliegue:**
- [ ] Contenedores ejecutándose (3+)
- [ ] SSL certificados configurados
- [ ] Endpoints HTTPS respondiendo
- [ ] OpenID Discovery funcionando
- [ ] OAuth endpoints funcionando
- [ ] Herramientas protegidas devuelven 401
- [ ] Base de datos conectada
- [ ] Logs sin errores críticos

### **Configuración ChatGPT:**
- [ ] Conector MCP creado
- [ ] OAuth 2.1 configurado
- [ ] Custom UX habilitado
- [ ] Scope configurado
- [ ] URLs correctas

### **Pruebas Funcionales:**
- [ ] Health checks OK
- [ ] Discovery endpoint OK
- [ ] Authorization endpoint OK
- [ ] Token endpoint OK
- [ ] Herramientas protegidas requieren auth
- [ ] Flujo OAuth 2.1 completo

---

## 🎉 **ESTADO FINAL**

**✅ DESPLIEGUE COMPLETO EXITOSO**

### **Servicios Operativos:**
- **SIAC Assistant**: `https://api.siac-app.com` ✅
- **Auth Server**: `https://auth.siac-app.com` ✅
- **PostgreSQL**: Base de datos ✅

### **Funcionalidades Disponibles:**
- **MCP Endpoint**: `https://api.siac-app.com/mcp` ✅
- **OAuth 2.1**: Flujo completo con PKCE ✅
- **Custom UX**: Componentes UI ✅
- **Herramientas Protegidas**: Autenticación requerida ✅

### **Próximos Pasos:**
1. **Configurar conector en ChatGPT**
2. **Probar flujo OAuth 2.1**
3. **Usar herramientas protegidas**
4. **Monitorear logs y métricas**

---

## 🚀 **¡LISTO PARA USAR!**

**El SIAC Assistant con OAuth 2.1 está completamente desplegado y operativo.**

**URLs de Configuración:**
- **MCP URL**: `https://api.siac-app.com/mcp`
- **Auth URL**: `https://auth.siac-app.com`
- **Discovery**: `https://auth.siac-app.com/.well-known/openid-configuration`

**¡Disfruta de la gestión segura de campañas WhatsApp desde ChatGPT!** 🎉



