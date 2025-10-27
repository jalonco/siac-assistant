# SIAC Authorization Server - Documentación Completa
# Servidor de Autorización OAuth 2.1 para SIAC Assistant

## 🎯 **DESCRIPCIÓN**

El **SIAC Authorization Server** es un microservicio minimalista desarrollado en FastAPI que actúa como servidor de autorización OAuth 2.1 con soporte para OpenID Connect. Este servicio proporciona los endpoints necesarios para que ChatGPT pueda autenticar y autorizar el acceso a las herramientas protegidas del SIAC Assistant.

---

## 🏗️ **ARQUITECTURA**

### **Componentes Principales:**
- **FastAPI Application**: Framework web minimalista
- **OpenID Connect Discovery**: Endpoint `/.well-known/openid-configuration`
- **OAuth 2.1 Endpoints**: Autorización, token, userinfo, revocación
- **JWKS Endpoint**: Claves públicas para verificación de tokens
- **Health Check**: Monitoreo del estado del servicio

### **Puerto y Configuración:**
- **Puerto Interno**: 8080
- **Dominio**: `auth.siac-app.com`
- **Protocolo**: HTTPS (SSL/TLS)
- **Certificado**: Let's Encrypt (via Traefik)

---

## 🔐 **ENDPOINTS OAUTH 2.1**

### **1. OpenID Connect Discovery**
```
GET /.well-known/openid-configuration
```
**Descripción:** Proporciona metadatos del servidor de autorización
**Respuesta:** Configuración JSON con todos los endpoints y capacidades

### **2. Authorization Endpoint**
```
GET /oauth/authorize
```
**Parámetros:**
- `response_type=code` (requerido)
- `client_id` (requerido)
- `redirect_uri` (requerido)
- `scope=siac.user.full_access` (requerido)
- `state` (opcional)
- `code_challenge` (PKCE)
- `code_challenge_method=S256` (PKCE)

### **3. Token Endpoint**
```
POST /oauth/token
```
**Body:**
```json
{
  "grant_type": "authorization_code",
  "code": "authorization_code",
  "redirect_uri": "https://chatgpt.com/oauth/callback",
  "client_id": "siac_assistant",
  "code_verifier": "pkce_verifier"
}
```

### **4. UserInfo Endpoint**
```
GET /oauth/userinfo
```
**Headers:** `Authorization: Bearer <access_token>`
**Respuesta:** Información del usuario autenticado

### **5. Token Revocation**
```
POST /oauth/revoke
```
**Body:** Token a revocar
**Respuesta:** Confirmación de revocación

### **6. Token Introspection**
```
POST /oauth/introspect
```
**Body:** Token a inspeccionar
**Respuesta:** Información detallada del token

### **7. JWKS Endpoint**
```
GET /oauth/keys
```
**Respuesta:** Conjunto de claves públicas para verificación JWT

---

## 🔧 **CONFIGURACIÓN**

### **Variables de Entorno:**
```bash
AUTH_SERVER_ISSUER=https://auth.siac-app.com
LOG_LEVEL=INFO
DEBUG=false
RELOAD=false
```

### **Configuración del Servidor:**
```python
AUTH_SERVER_CONFIG = {
    "issuer": "https://auth.siac-app.com",
    "authorization_endpoint": "https://auth.siac-app.com/oauth/authorize",
    "token_endpoint": "https://auth.siac-app.com/oauth/token",
    "jwks_uri": "https://auth.siac-app.com/oauth/keys",
    "userinfo_endpoint": "https://auth.siac-app.com/oauth/userinfo",
    "revocation_endpoint": "https://auth.siac-app.com/oauth/revoke",
    "introspection_endpoint": "https://auth.siac-app.com/oauth/introspect"
}
```

---

## 🚀 **DESPLIEGUE**

### **Docker Compose:**
```yaml
auth_server:
  build: ./auth_server
  container_name: siac-auth-server
  restart: unless-stopped
  environment:
    - AUTH_SERVER_ISSUER=https://auth.siac-app.com
    - LOG_LEVEL=INFO
    - DEBUG=false
    - RELOAD=false
  labels:
    - "traefik.enable=true"
    - "traefik.http.routers.siac-auth.rule=Host(`auth.siac-app.com`)"
    - "traefik.http.routers.siac-auth.entrypoints=websecure"
    - "traefik.http.routers.siac-auth.tls.certresolver=le"
    - "traefik.http.services.siac-auth.loadbalancer.server.port=8080"
  networks:
    - traefik-public
  volumes:
    - auth_logs:/app/logs
  healthcheck:
    test: ["CMD", "curl", "-f", "http://localhost:8080/health"]
    interval: 30s
    timeout: 10s
    retries: 3
    start_period: 40s
```

### **Comandos de Despliegue:**
```bash
# Despliegue completo
./deploy_complete.sh

# Verificación
./verify_complete.sh

# Gestión manual
docker-compose -f docker-compose.production.yml up -d
docker-compose -f docker-compose.production.yml restart auth_server
```

---

## 🔍 **VERIFICACIÓN**

### **Health Check:**
```bash
curl -I https://auth.siac-app.com/health
```

### **OpenID Discovery:**
```bash
curl https://auth.siac-app.com/.well-known/openid-configuration
```

### **Authorization Endpoint:**
```bash
curl "https://auth.siac-app.com/oauth/authorize?response_type=code&client_id=siac_assistant&redirect_uri=https://chatgpt.com/oauth/callback&scope=siac.user.full_access"
```

### **Token Endpoint:**
```bash
curl -X POST https://auth.siac-app.com/oauth/token \
  -H "Content-Type: application/json" \
  -d '{"grant_type":"authorization_code","code":"test_code","redirect_uri":"https://chatgpt.com/oauth/callback","client_id":"siac_assistant"}'
```

---

## 🔐 **FLUJO OAUTH 2.1 CON PKCE**

### **1. Discovery Phase:**
1. ChatGPT consulta `/.well-known/openid-configuration`
2. Obtiene metadatos del servidor de autorización
3. Identifica endpoints y capacidades soportadas

### **2. Authorization Phase:**
1. ChatGPT genera `code_challenge` (PKCE)
2. Redirige al usuario a `/oauth/authorize`
3. Usuario autoriza el acceso
4. Servidor redirige con `authorization_code`

### **3. Token Exchange:**
1. ChatGPT envía `authorization_code` + `code_verifier` a `/oauth/token`
2. Servidor valida el código y verifica PKCE
3. Servidor devuelve `access_token` y `refresh_token`

### **4. Resource Access:**
1. ChatGPT incluye `access_token` en requests a SIAC Assistant
2. SIAC Assistant valida el token con el Auth Server
3. Se otorga acceso a herramientas protegidas

---

## 🛡️ **SEGURIDAD**

### **Características de Seguridad:**
- **HTTPS Obligatorio**: Todos los endpoints requieren SSL/TLS
- **PKCE Support**: Protección contra ataques de interceptación
- **CORS Configurado**: Solo dominios autorizados
- **Token Expiration**: Tokens con tiempo de vida limitado
- **Scope Validation**: Validación estricta de scopes
- **State Parameter**: Protección contra CSRF

### **Scopes Soportados:**
- `openid`: Identificación básica
- `profile`: Información del perfil
- `siac.user.full_access`: Acceso completo a SIAC Assistant

### **Grant Types Soportados:**
- `authorization_code`: Flujo estándar con PKCE
- `refresh_token`: Renovación de tokens

---

## 📊 **MONITOREO**

### **Logs:**
```bash
# Ver logs del Auth Server
docker logs siac-auth-server --tail 50

# Ver logs en tiempo real
docker logs siac-auth-server -f
```

### **Métricas:**
- **Health Check**: `/health`
- **Request Logging**: Middleware de logging automático
- **Error Tracking**: Manejo global de errores HTTP

### **Health Check:**
```json
{
  "status": "healthy",
  "service": "SIAC Authorization Server",
  "version": "1.0.0",
  "timestamp": "2024-01-01T00:00:00Z",
  "issuer": "https://auth.siac-app.com"
}
```

---

## 🔧 **MANTENIMIENTO**

### **Comandos Útiles:**
```bash
# Reiniciar servicio
docker restart siac-auth-server

# Ver estado
docker ps | grep siac-auth-server

# Ver logs
docker logs siac-auth-server --tail 100

# Acceder al contenedor
docker exec -it siac-auth-server /bin/bash

# Verificar configuración
curl https://auth.siac-app.com/.well-known/openid-configuration | jq
```

### **Actualizaciones:**
1. Modificar código en `auth_server/main.py`
2. Reconstruir imagen: `docker build -t siac-assistant-auth:latest ./auth_server`
3. Reiniciar servicio: `docker restart siac-auth-server`

---

## 🚨 **SOLUCIÓN DE PROBLEMAS**

### **Problemas Comunes:**

#### **1. SSL Certificate Issues:**
```bash
# Verificar certificado
curl -I https://auth.siac-app.com/health

# Verificar Traefik
docker logs traefik | grep auth.siac-app.com
```

#### **2. Service Not Responding:**
```bash
# Verificar contenedor
docker ps | grep siac-auth-server

# Verificar logs
docker logs siac-auth-server --tail 50

# Reiniciar servicio
docker restart siac-auth-server
```

#### **3. OAuth Flow Issues:**
```bash
# Verificar discovery
curl https://auth.siac-app.com/.well-known/openid-configuration

# Verificar endpoints
curl https://auth.siac-app.com/oauth/authorize?response_type=code&client_id=test&redirect_uri=https://test.com&scope=siac.user.full_access
```

---

## 📚 **REFERENCIAS**

### **Estándares Implementados:**
- **OAuth 2.1**: RFC 6749 + Security Best Practices
- **OpenID Connect**: OpenID Connect Core 1.0
- **PKCE**: RFC 7636
- **JWKS**: RFC 7517

### **Documentación Externa:**
- [OAuth 2.1 Security Best Practices](https://tools.ietf.org/html/draft-ietf-oauth-security-topics)
- [OpenID Connect Discovery](https://openid.net/specs/openid-connect-discovery-1_0.html)
- [PKCE RFC 7636](https://tools.ietf.org/html/rfc7636)

---

## ✅ **CHECKLIST DE IMPLEMENTACIÓN**

- [x] **FastAPI Application** creada
- [x] **OpenID Connect Discovery** implementado
- [x] **OAuth 2.1 Endpoints** implementados
- [x] **PKCE Support** configurado
- [x] **JWKS Endpoint** implementado
- [x] **Health Check** configurado
- [x] **Dockerfile** creado
- [x] **Docker Compose** configurado
- [x] **Traefik Labels** configurados
- [x] **SSL/HTTPS** configurado
- [x] **CORS** configurado
- [x] **Logging** implementado
- [x] **Error Handling** implementado
- [x] **Documentación** completa

---

## 🎉 **ESTADO ACTUAL**

**✅ COMPLETAMENTE IMPLEMENTADO Y OPERATIVO**

El SIAC Authorization Server está completamente desplegado y listo para proporcionar autenticación OAuth 2.1 para el SIAC Assistant. Todos los endpoints están funcionando correctamente y el flujo de autenticación está completamente integrado con ChatGPT.

**URL del Servidor:** `https://auth.siac-app.com`
**Estado:** ✅ OPERATIVO
**Versión:** 1.0.0



