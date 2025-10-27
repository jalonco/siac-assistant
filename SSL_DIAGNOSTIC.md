# 🔍 SIAC Assistant - Diagnóstico Final SSL

## ✅ **ESTADO ACTUAL:**

### **Servicios Desplegados:**
- ✅ **siac-assistant** - Ejecutándose correctamente (puerto 8888)
- ✅ **siac-auth-server** - Ejecutándose correctamente (puerto 8080)  
- ✅ **siac-assistant-db** - Ejecutándose correctamente (PostgreSQL)
- ✅ **traefik** - Ejecutándose correctamente

### **DNS Configurado:**
- ✅ **api.siac-app.com** → 168.231.65.46
- ✅ **auth.siac-app.com** → 168.231.65.46

---

## ❌ **PROBLEMA DETECTADO:**

**Traefik está sirviendo el "certificado por defecto" y no genera certificados Let's Encrypt para los nuevos dominios.**

### **Causa Principal:**
Los servicios SIAC no están conectados correctamente a la red `traefik-public` o Traefik no los está detectando.

---

## 🔧 **SOLUCIONES PROPUESTAS:**

### **Opción 1: Verificar y Corregir Configuración de Traefik (RECOMENDADO)**

#### **1. Verificar configuración actual de Traefik:**
```bash
ssh -i ~/.ssh/id_ed25519 root@srv790515.hstgr.cloud "docker exec traefik cat /etc/traefik/traefik.yml"
```

#### **2. Verificar que los servicios estén en la red correcta:**
```bash
ssh -i ~/.ssh/id_ed25519 root@srv790515.hstgr.cloud "docker network inspect traefik-public | jq -r '.[0].Containers | to_entries[] | .value.Name'"
```

**Resultado esperado:** Debe mostrar `siac-assistant`, `siac-auth-server`, y `traefik`.

#### **3. Si los servicios NO están en la red, agregarlos manualmente:**
```bash
ssh -i ~/.ssh/id_ed25519 root@srv790515.hstgr.cloud "docker network connect traefik-public siac-assistant"
ssh -i ~/.ssh/id_ed25519 root@srv790515.hstgr.cloud "docker network connect traefik-public siac-auth-server"
```

#### **4. Reiniciar Traefik:**
```bash
ssh -i ~/.ssh/id_ed25519 root@srv790515.hstgr.cloud "docker restart traefik"
```

#### **5. Esperar 2-3 minutos y verificar logs:**
```bash
ssh -i ~/.ssh/id_ed25519 root@srv790515.hstgr.cloud "docker logs traefik --tail 50 | grep -i 'api.siac-app.com\\|auth.siac-app.com\\|certificate'"
```

---

### **Opción 2: Desplegar Traefik con Configuración Correcta**

El Traefik existente puede tener una configuración diferente a la que necesitamos. Voy a crear un script para configurar Traefik específicamente para SIAC:

#### **1. Subir configuración de Traefik:**
```bash
# Desde tu máquina local
scp -i ~/.ssh/id_ed25519 traefik/traefik.yml root@srv790515.hstgr.cloud:/opt/traefik/
scp -i ~/.ssh/id_ed25519 traefik/docker-compose.yml root@srv790515.hstgr.cloud:/opt/traefik/
```

#### **2. Reiniciar Traefik con nueva configuración:**
```bash
ssh -i ~/.ssh/id_ed25519 root@srv790515.hstgr.cloud "cd /opt/traefik && docker-compose down && docker-compose up -d"
```

#### **3. Redesplegar servicios SIAC:**
```bash
ssh -i ~/.ssh/id_ed25519 root@srv790515.hstgr.cloud "cd /opt/siac-assistant && docker-compose -f docker-compose.production.yml down && docker-compose -f docker-compose.production.yml up -d"
```

---

### **Opción 3: Configurar SSL Manualmente con Certbot**

Si Traefik no genera los certificados, podemos usar Certbot directamente:

```bash
# Conectar al VPS
ssh -i ~/.ssh/id_ed25519 root@srv790515.hstgr.cloud

# Instalar Certbot
apt update && apt install -y certbot

# Generar certificados (HTTP Challenge)
certbot certonly --standalone --preferred-challenges http \
  -d api.siac-app.com -d auth.siac-app.com \
  --email admin@siac-app.com --agree-tos --non-interactive

# Los certificados se guardarán en:
# /etc/letsencrypt/live/api.siac-app.com/fullchain.pem
# /etc/letsencrypt/live/api.siac-app.com/privkey.pem
```

---

## 📊 **INFORMACIÓN TÉCNICA:**

### **Configuración Requerida en Traefik:**

El `traefik.yml` debe contener:
```yaml
certificatesResolvers:
  le:
    acme:
      email: admin@siac-app.com
      storage: /letsencrypt/acme.json
      httpChallenge:
        entryPoint: web
```

### **Labels Requeridos en Docker Compose:**

Los servicios deben tener estas labels:
```yaml
labels:
  - "traefik.enable=true"
  - "traefik.http.routers.siac-assistant.rule=Host(`api.siac-app.com`)"
  - "traefik.http.routers.siac-assistant.entrypoints=websecure"
  - "traefik.http.routers.siac-assistant.tls.certresolver=le"
```

---

## 🔍 **COMANDOS DE DIAGNÓSTICO:**

### **Ver configuración actual de Traefik:**
```bash
ssh -i ~/.ssh/id_ed25519 root@srv790515.hstgr.cloud "docker exec traefik cat /etc/traefik/traefik.yml"
```

### **Ver routers detectados por Traefik:**
```bash
ssh -i ~/.ssh/id_ed25519 root@srv790515.hstgr.cloud "docker exec traefik traefik version"
```

### **Ver certificados en acme.json:**
```bash
ssh -i ~/.ssh/id_ed25519 root@srv790515.hstgr.cloud "cat /opt/traefik/letsencrypt/acme.json | jq '.le.Certificates[] | {domain: .domain.main, expires: .certificate}'"
```

### **Verificar red traefik-public:**
```bash
ssh -i ~/.ssh/id_ed25519 root@srv790515.hstgr.cloud "docker network inspect traefik-public"
```

### **Verificar labels de contenedores:**
```bash
ssh -i ~/.ssh/id_ed25519 root@srv790515.hstgr.cloud "docker inspect siac-assistant | jq '.[0].Config.Labels'"
ssh -i ~/.ssh/id_ed25519 root@srv790515.hstgr.cloud "docker inspect siac-auth-server | jq '.[0].Config.Labels'"
```

---

## ✅ **PRÓXIMOS PASOS:**

1. **Ejecutar Opción 1** (verificar y corregir red)
2. **Esperar 2-3 minutos** para generación de certificados
3. **Verificar con:** `./verify_ssl.sh`
4. **Si aún no funciona,** ejecutar Opción 2 (reconfigurar Traefik)
5. **Como último recurso,** usar Opción 3 (Certbot manual)

---

## 📞 **CONTACTO:**

Si los certificados aún no se generan después de seguir estas instrucciones, el problema puede ser:
- **Firewall bloqueando puerto 80** (necesario para HTTP Challenge)
- **DNS no propagado completamente** (esperar 24-48 horas)
- **Rate limit de Let's Encrypt** (esperar 1 semana)
- **Configuración de Traefik incompatible** con el setup existente

**Documentación Completa:** `SSL_CONFIGURATION.md`


