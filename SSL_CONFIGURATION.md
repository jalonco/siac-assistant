# SIAC Assistant - Configuración SSL con Let's Encrypt
# Documentación completa para certificados SSL/TLS

## 🎯 **DESCRIPCIÓN**

Este documento describe el proceso completo de configuración de certificados SSL/TLS con Let's Encrypt para los dominios **api.siac-app.com** y **auth.siac-app.com** utilizando Traefik como reverse proxy.

---

## 🏗️ **ARQUITECTURA SSL**

### **Componentes:**
```
┌──────────────┐    ┌──────────────┐    ┌──────────────┐
│  Internet    │    │   Traefik    │    │    Docker    │
│              │    │              │    │  Services    │
│  HTTPS:443   │───►│  Reverse     │───►│              │
│  HTTP:80     │    │  Proxy       │    │ • SIAC       │
│              │    │              │    │ • Auth       │
│              │    │  Let's       │    │ • PostgreSQL │
│              │    │  Encrypt     │    │              │
└──────────────┘    └──────────────┘    └──────────────┘
```

### **Flujo de Certificación:**
1. **Traefik** detecta nuevos servicios via Docker labels
2. **Traefik** solicita certificado a Let's Encrypt (HTTP Challenge)
3. **Let's Encrypt** valida dominio via HTTP
4. **Traefik** almacena certificado en `/letsencrypt/acme.json`
5. **Renovación automática** cada 60 días

---

## 🚀 **CONFIGURACIÓN RÁPIDA**

### **Paso 1: Verificar DNS**
Asegúrate de que ambos dominios apunten a la IP del VPS:

```bash
dig +short api.siac-app.com
dig +short auth.siac-app.com
```

**Resultado esperado:** Ambos deben resolver a la IP del VPS `srv790515.hstgr.cloud`

### **Paso 2: Ejecutar Script de Configuración**
```bash
chmod +x setup_ssl.sh
./setup_ssl.sh
```

Este script:
- ✅ Verifica conexión al VPS
- ✅ Verifica configuración DNS
- ✅ Instala/configura Traefik si no existe
- ✅ Despliega servicios SIAC con SSL
- ✅ Espera generación de certificados
- ✅ Verifica certificados SSL

### **Paso 3: Verificar Certificados**
```bash
chmod +x verify_ssl.sh
./verify_ssl.sh
```

---

## 📋 **CONFIGURACIÓN MANUAL**

### **1. Configurar DNS**

Configurar registros A en tu proveedor DNS:

```
api.siac-app.com    →  A  →  <IP_VPS>
auth.siac-app.com   →  A  →  <IP_VPS>
```

### **2. Instalar Traefik**

```bash
# Conectar al VPS
ssh -i ~/.ssh/id_ed25519 root@srv790515.hstgr.cloud

# Crear directorio para Traefik
mkdir -p /opt/traefik/letsencrypt

# Crear archivo acme.json
touch /opt/traefik/letsencrypt/acme.json
chmod 600 /opt/traefik/letsencrypt/acme.json

# Copiar archivos de configuración
# (traefik.yml y docker-compose.yml desde carpeta traefik/)

# Iniciar Traefik
cd /opt/traefik
docker-compose up -d
```

### **3. Desplegar Servicios SIAC**

```bash
# Desplegar con docker-compose
cd /opt/siac-assistant
docker-compose -f docker-compose.production.yml up -d
```

Los servicios ya tienen las labels de Traefik configuradas para SSL automático.

### **4. Verificar Generación de Certificados**

```bash
# Ver logs de Traefik
docker logs traefik | grep -i "certificate"

# Ver certificados generados
cat /opt/traefik/letsencrypt/acme.json | jq '.le.Certificates[].domain.main'

# Verificar HTTPS
curl -I https://api.siac-app.com/health
curl -I https://auth.siac-app.com/health
```

---

## 🔧 **CONFIGURACIÓN DE TRAEFIK**

### **traefik.yml**

```yaml
# Entry Points
entryPoints:
  web:
    address: ":80"
    http:
      redirections:
        entryPoint:
          to: websecure
          scheme: https
          permanent: true

  websecure:
    address: ":443"
    http:
      tls:
        certResolver: le

# Let's Encrypt
certificatesResolvers:
  le:
    acme:
      email: admin@siac-app.com
      storage: /letsencrypt/acme.json
      httpChallenge:
        entryPoint: web
```

### **Labels en docker-compose.production.yml**

```yaml
services:
  siac_assistant:
    labels:
      - "traefik.enable=true"
      - "traefik.http.routers.siac-assistant.rule=Host(`api.siac-app.com`)"
      - "traefik.http.routers.siac-assistant.entrypoints=websecure"
      - "traefik.http.routers.siac-assistant.tls.certresolver=le"
      - "traefik.http.services.siac-assistant.loadbalancer.server.port=8888"

  auth_server:
    labels:
      - "traefik.enable=true"
      - "traefik.http.routers.siac-auth.rule=Host(`auth.siac-app.com`)"
      - "traefik.http.routers.siac-auth.entrypoints=websecure"
      - "traefik.http.routers.siac-auth.tls.certresolver=le"
      - "traefik.http.services.siac-auth.loadbalancer.server.port=8080"
```

---

## 🔍 **VERIFICACIÓN SSL**

### **Verificación Básica:**

```bash
# Verificar certificado con curl
curl -vI https://api.siac-app.com/health 2>&1 | grep -i "SSL\\|certificate"

# Verificar certificado con openssl
echo | openssl s_client -servername api.siac-app.com -connect api.siac-app.com:443 2>/dev/null | openssl x509 -noout -text

# Verificar emisor
echo | openssl s_client -servername api.siac-app.com -connect api.siac-app.com:443 2>/dev/null | openssl x509 -noout -issuer

# Verificar fechas de validez
echo | openssl s_client -servername api.siac-app.com -connect api.siac-app.com:443 2>/dev/null | openssl x509 -noout -dates
```

### **Verificación Avanzada:**

```bash
# Usar script de verificación
./verify_ssl.sh

# SSL Labs (análisis completo)
# Visita: https://www.ssllabs.com/ssltest/analyze.html?d=api.siac-app.com

# Verificar cadena de certificados
openssl s_client -showcerts -servername api.siac-app.com -connect api.siac-app.com:443 </dev/null 2>/dev/null | openssl x509 -text
```

---

## 🔄 **RENOVACIÓN AUTOMÁTICA**

### **Configuración:**

Let's Encrypt emite certificados válidos por **90 días**. Traefik renueva automáticamente los certificados cuando quedan **30 días** o menos.

### **Verificación de Renovación:**

```bash
# Ver logs de renovación
docker logs traefik | grep -i "renew"

# Forzar verificación (opcional)
docker restart traefik
```

### **Monitoreo:**

```bash
# Ver días restantes
echo | openssl s_client -servername api.siac-app.com -connect api.siac-app.com:443 2>/dev/null | openssl x509 -noout -enddate

# Script de monitoreo (agregar a cron)
#!/bin/bash
EXPIRY=$(echo | openssl s_client -servername api.siac-app.com -connect api.siac-app.com:443 2>/dev/null | openssl x509 -noout -enddate | cut -d= -f2)
DAYS=$(( ($(date -d "$EXPIRY" +%s) - $(date +%s)) / 86400 ))
echo "Días restantes: $DAYS"
if [ $DAYS -lt 7 ]; then
    echo "¡ALERTA! Certificado expira pronto"
fi
```

---

## 🚨 **SOLUCIÓN DE PROBLEMAS**

### **Problema 1: Certificados No se Generan**

**Síntomas:**
- HTTPS no funciona
- Error "certificate unknown"

**Solución:**
```bash
# 1. Verificar DNS
dig +short api.siac-app.com

# 2. Verificar puertos abiertos
ssh -i ~/.ssh/id_ed25519 root@srv790515.hstgr.cloud "netstat -tulpn | grep -E '80|443'"

# 3. Ver logs de Traefik
docker logs traefik | grep -i "acme\\|error"

# 4. Reiniciar Traefik
docker restart traefik

# 5. Limpiar y regenerar (último recurso)
ssh -i ~/.ssh/id_ed25519 root@srv790515.hstgr.cloud "rm /opt/traefik/letsencrypt/acme.json && touch /opt/traefik/letsencrypt/acme.json && chmod 600 /opt/traefik/letsencrypt/acme.json && docker restart traefik"
```

### **Problema 2: Rate Limit de Let's Encrypt**

**Síntomas:**
- Error "too many certificates already issued"

**Solución:**
```bash
# Usar ambiente de staging mientras pruebas
# En traefik.yml, cambiar:
certificatesResolvers:
  le:
    acme:
      caServer: https://acme-staging-v02.api.letsencrypt.org/directory
      # ... resto de config
```

**Límites de Let's Encrypt:**
- 50 certificados por dominio registrado por semana
- 5 certificados duplicados por semana

### **Problema 3: Certificado Expirado**

**Síntomas:**
- Error "certificate has expired"

**Solución:**
```bash
# Forzar renovación
docker restart traefik

# Esperar 2-3 minutos y verificar
./verify_ssl.sh
```

### **Problema 4: Mixed Content (HTTP en HTTPS)**

**Síntomas:**
- Algunos recursos se cargan por HTTP

**Solución:**
Agregar middleware de redirección en docker-compose:
```yaml
labels:
  - "traefik.http.middlewares.redirect-to-https.redirectscheme.scheme=https"
  - "traefik.http.routers.siac-assistant.middlewares=redirect-to-https"
```

---

## 📊 **MONITOREO Y MANTENIMIENTO**

### **Comandos de Monitoreo:**

```bash
# Estado de Traefik
docker ps | grep traefik

# Logs en tiempo real
docker logs traefik -f

# Certificados almacenados
ssh -i ~/.ssh/id_ed25519 root@srv790515.hstgr.cloud "cat /opt/traefik/letsencrypt/acme.json | jq '.le.Certificates[] | {domain: .domain.main, expires: .certificate}'"

# Verificación programada
crontab -e
# Agregar: 0 0 * * * /path/to/verify_ssl.sh > /var/log/ssl-check.log 2>&1
```

### **Dashboard de Traefik:**

```bash
# Acceder al dashboard (solo desde VPS)
ssh -i ~/.ssh/id_ed25519 -L 8080:localhost:8080 root@srv790515.hstgr.cloud

# En navegador local:
http://localhost:8080
```

---

## 🔐 **SEGURIDAD ADICIONAL**

### **1. Headers de Seguridad:**

Agregar middleware en docker-compose:
```yaml
labels:
  - "traefik.http.middlewares.security-headers.headers.stsSeconds=31536000"
  - "traefik.http.middlewares.security-headers.headers.stsIncludeSubdomains=true"
  - "traefik.http.middlewares.security-headers.headers.stsPreload=true"
  - "traefik.http.middlewares.security-headers.headers.contentTypeNosniff=true"
  - "traefik.http.middlewares.security-headers.headers.browserXssFilter=true"
  - "traefik.http.routers.siac-assistant.middlewares=security-headers"
```

### **2. TLS Configuration:**

En traefik.yml:
```yaml
entryPoints:
  websecure:
    address: ":443"
    http:
      tls:
        certResolver: le
        options: default

tls:
  options:
    default:
      minVersion: VersionTLS12
      cipherSuites:
        - TLS_ECDHE_RSA_WITH_AES_128_GCM_SHA256
        - TLS_ECDHE_RSA_WITH_AES_256_GCM_SHA384
        - TLS_ECDHE_RSA_WITH_CHACHA20_POLY1305
```

---

## ✅ **CHECKLIST DE CONFIGURACIÓN**

- [ ] **DNS configurado** para ambos dominios
- [ ] **Puertos 80 y 443** abiertos en VPS
- [ ] **Traefik instalado** y ejecutándose
- [ ] **Red traefik-public** creada
- [ ] **Servicios SIAC desplegados** con labels Traefik
- [ ] **Certificados generados** por Let's Encrypt
- [ ] **HTTPS funcionando** para ambos dominios
- [ ] **Redirección HTTP → HTTPS** configurada
- [ ] **Headers de seguridad** configurados (opcional)
- [ ] **Renovación automática** verificada
- [ ] **Monitoreo configurado** (opcional)

---

## 📚 **REFERENCIAS**

### **Documentación Oficial:**
- [Let's Encrypt](https://letsencrypt.org/docs/)
- [Traefik Documentation](https://doc.traefik.io/traefik/)
- [Traefik & Let's Encrypt](https://doc.traefik.io/traefik/https/acme/)

### **Herramientas de Verificación:**
- [SSL Labs](https://www.ssllabs.com/ssltest/)
- [SSL Checker](https://www.sslshopper.com/ssl-checker.html)
- [Let's Encrypt Rate Limits](https://letsencrypt.org/docs/rate-limits/)

---

## 🎉 **ESTADO FINAL**

**✅ CERTIFICADOS SSL COMPLETAMENTE CONFIGURADOS**

### **Dominios Protegidos:**
- ✅ **api.siac-app.com** - Certificado Let's Encrypt válido
- ✅ **auth.siac-app.com** - Certificado Let's Encrypt válido

### **Características:**
- ✅ SSL/TLS con Let's Encrypt
- ✅ Redirección HTTP → HTTPS automática
- ✅ Renovación automática de certificados
- ✅ TLS 1.2 y TLS 1.3 soportados
- ✅ Traefik como reverse proxy
- ✅ Monitoreo y verificación disponibles

**¡Los dominios están completamente protegidos con SSL/TLS!** 🔒


