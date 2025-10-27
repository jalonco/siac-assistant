# SIAC Assistant - Datos de Conexión para pgAdmin
# ================================================

## 📋 DATOS DE CONEXIÓN PARA PGADMIN

### Configuración Básica:
- **Host:** localhost
- **Puerto:** 5432
- **Base de datos:** siac_chatgpt
- **Usuario:** siac
- **Contraseña:** siac123

### Configuración SSL:
- **SSL Mode:** Prefer (o Disable para desarrollo local)

### Pasos para Conectar en pgAdmin:

1. **Abrir pgAdmin**
2. **Crear Nueva Conexión:**
   - Click derecho en "Servers" → "Create" → "Server..."

3. **Pestaña "General":**
   - **Name:** SIAC Assistant DB

4. **Pestaña "Connection":**
   - **Host name/address:** localhost
   - **Port:** 5432
   - **Maintenance database:** siac_chatgpt
   - **Username:** siac
   - **Password:** siac123

5. **Pestaña "SSL" (opcional):**
   - **SSL mode:** Prefer o Disable

6. **Click "Save"**

## 🔧 Configuración Adicional:

### Connection Timeout:
- **Valor:** 30 segundos

### Application Name:
- **Valor:** pgAdmin - SIAC Assistant

## 📊 Tablas Disponibles:

Una vez conectado, deberías ver las siguientes tablas:

- **users** - Usuarios del sistema
- **clients** - Clientes de SIAC
- **whatsapp_phone_numbers** - Números de WhatsApp
- **message_templates** - Plantillas de mensajes
- **campaigns** - Campañas de marketing
- **message_transactions** - Transacciones de mensajes

## 🔍 Verificación de Conexión:

### Comando psql:
```bash
psql -h localhost -p 5432 -U siac -d siac_chatgpt
```

### String de Conexión:
```
postgresql://siac:siac123@localhost:5432/siac_chatgpt
```

## 🚨 Solución de Problemas:

### Si no puedes conectar:

1. **Verificar que PostgreSQL esté ejecutándose:**
   ```bash
   ps aux | grep postgres
   brew services list | grep postgresql
   ```

2. **Verificar que el puerto 5432 esté abierto:**
   ```bash
   lsof -i :5432
   ```

3. **Verificar que el usuario 'siac' exista:**
   ```bash
   psql -h localhost -p 5432 -U postgres -c "\du"
   ```

4. **Verificar que la base de datos 'siac_chatgpt' exista:**
   ```bash
   psql -h localhost -p 5432 -U postgres -c "\l"
   ```

### Comandos Útiles:

- **Crear usuario y base de datos:** `python setup_database.py`
- **Verificar conexión:** `python check_database.py`
- **Reiniciar PostgreSQL:** `brew services restart postgresql`

## 📱 URLs Útiles:

- **Servidor MCP:** http://localhost:8888
- **Swagger UI:** http://localhost:8888/docs
- **ReDoc:** http://localhost:8888/redoc
- **OpenAPI Spec:** http://localhost:8888/openapi.json

---

**Nota:** Estos datos están configurados en el archivo `docker-compose.yml` y en el script `setup_database.py` del proyecto.



