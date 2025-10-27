# 🔐 Guía de Autenticación de Usuarios - SIAC Assistant

## 📋 **Resumen**

SIAC Assistant ahora cuenta con un **sistema completo de autenticación de usuarios** que permite identificar quién accede desde ChatGPT y a qué cliente/empresa pertenece.

---

## 🎯 **Cómo Funciona**

### **Flujo de Autenticación Completo**

```
1. Usuario en ChatGPT → Intenta conectarse al MCP Server
2. ChatGPT → Redirige a login.siac-app.com
3. Usuario → Ve página de login con su navegador
4. Usuario → Ingresa email y contraseña
5. Sistema → Valida credenciales contra base de datos
6. Sistema → Genera token asociado al usuario
7. ChatGPT → Recibe token con información del usuario
8. ChatGPT → Puede usar el MCP Server con identidad real
```

---

## 👤 **Usuarios de Prueba Disponibles**

| **Email** | **Contraseña** | **Cliente** | **Rol** | **Permisos** |
|-----------|----------------|-------------|---------|--------------|
| `admin@siac.com` | `admin123` | SIAC Principal | Admin | read, write, delete |
| `usuario@cliente1.com` | `demo123` | Cliente Demo 1 | User | read |
| `manager@cliente2.com` | `manager123` | Cliente Demo 2 | Manager | read, write |

---

## 🔍 **Identificación del Usuario**

### **Información Disponible en el Token**

Cuando un usuario se autentica, el sistema captura y asocia:

```json
{
  "user_id": "user_001",
  "email": "admin@siac.com",
  "name": "Administrador SIAC",
  "client_id": "cliente_siac_principal",
  "client_name": "SIAC Principal",
  "roles": ["admin", "user"],
  "permissions": ["read", "write", "delete"],
  "scope": "siac.user.full_access"
}
```

### **En el Servidor MCP**

El endpoint `POST /mcp` ahora recibe esta información:

```python
@app.post("/mcp")
async def mcp_handler(request: Request, current_user: Dict = Depends(get_current_user)):
    # current_user contiene toda la información del usuario
    user_email = current_user.get("email")  # "admin@siac.com"
    client_name = current_user.get("client_name")  # "SIAC Principal"
    user_roles = current_user.get("roles")  # ["admin", "user"]
    
    logger.info(f"Solicitud MCP de {user_email} (Cliente: {client_name})")
```

---

## 📊 **Logs con Información del Usuario**

Los logs ahora muestran información detallada:

```
Auth Server:
INFO: Login exitoso - Usuario: admin@siac.com, Cliente: SIAC Principal
INFO: Access token generado para admin@siac.com (Cliente: SIAC Principal): access_token_abc123...

MCP Server:
INFO: Token válido para usuario: admin@siac.com (Cliente: SIAC Principal)
INFO: MCP Request from user user_001: tools/call
INFO: Token verification successful for user: user_001 with scopes: ['siac.user.full_access']
```

---

## 🔐 **Página de Login**

### **Características**

- ✅ **Diseño moderno y profesional**
- ✅ **Totalmente responsive (móvil/desktop)**
- ✅ **Muestra información del cliente que solicita acceso**
- ✅ **Credenciales de prueba visibles para desarrollo**
- ✅ **Indicador de conexión segura SSL/TLS**
- ✅ **Manejo de errores con feedback visual**

### **URL de Acceso**

```
https://auth.siac-app.com/oauth/authorize
```

---

## 🛠️ **Implementación Técnica**

### **Componentes**

| **Componente** | **Ubicación** | **Función** |
|----------------|---------------|-------------|
| **database.py** | `auth_server/database.py` | Base de datos de usuarios y tokens |
| **login.html** | `auth_server/templates/login.html` | Página de login |
| **OAuth Authorize** | `GET /oauth/authorize` | Muestra formulario de login |
| **OAuth Login** | `POST /oauth/login` | Procesa credenciales |
| **Token Info** | `POST /oauth/tokeninfo` | Valida tokens y retorna información |

### **Base de Datos de Usuarios**

Actualmente usa una **base de datos en memoria** para desarrollo. En producción debería ser PostgreSQL/MySQL.

```python
# auth_server/database.py
class UserDatabase:
    users = {
        "user_001": {
            "email": "admin@siac.com",
            "client_id": "cliente_siac_principal",
            "client_name": "SIAC Principal",
            ...
        }
    }
```

---

## 📝 **Agregar Nuevos Usuarios**

### **Para Desarrollo**

Editar `auth_server/database.py`:

```python
"user_004": {
    "email": "nuevo@cliente.com",
    "password": "password123",  # En producción: bcrypt hash
    "client_id": "cliente_003",
    "client_name": "Nuevo Cliente S.A.",
    "name": "Usuario Nuevo",
    "roles": ["user"],
    "permissions": ["read"],
    "active": True,
    "created_at": "2024-03-01T00:00:00Z"
}
```

### **Para Producción**

Implementar API REST para gestión de usuarios:

```python
@app.post("/admin/users")
async def create_user(user_data: UserCreate):
    # Validar permisos de admin
    # Hash de contraseña con bcrypt
    # Insertar en base de datos PostgreSQL
    # Retornar user_id
```

---

## 🔒 **Seguridad**

### **Características de Seguridad**

- ✅ **OAuth 2.1 con PKCE** - Protección contra ataques de intercepción
- ✅ **Tokens de uso único** - Los códigos de autorización expiran después de un uso
- ✅ **Expiración de tokens** - Tokens expiran después de 24 horas
- ✅ **Validación de redirect_uri** - Previene ataques de redirección
- ✅ **State parameter** - Protección CSRF
- ✅ **SSL/TLS** - Todas las comunicaciones encriptadas

### **Mejoras de Seguridad Recomendadas para Producción**

1. **Hash de Contraseñas**
   ```python
   import bcrypt
   hashed = bcrypt.hashpw(password.encode(), bcrypt.gensalt())
   ```

2. **Rate Limiting**
   ```python
   from slowapi import Limiter
   @limiter.limit("5/minute")
   async def login(...):
   ```

3. **2FA (Two-Factor Authentication)**
   - SMS o App de autenticación
   - Códigos temporales

4. **Auditoría de Accesos**
   - Log de todos los intentos de login
   - Alertas de actividad sospechosa

---

## 📱 **Experiencia del Usuario**

### **Desde ChatGPT**

1. Usuario configura MCP Server en ChatGPT
2. ChatGPT abre página de login en el navegador
3. Usuario ve: "ChatGPT (OpenAI) solicita acceso"
4. Usuario ingresa email y contraseña
5. Usuario es redirigido de vuelta a ChatGPT
6. ChatGPT puede usar el servidor con la identidad del usuario

### **Seguridad de Sesión**

- Token válido por 24 horas
- Usuario puede tener múltiples sesiones activas
- Cada sesión se registra con IP y timestamp

---

## 🧪 **Testing**

### **Probar el Login Manualmente**

```bash
# 1. Abrir en navegador
open https://auth.siac-app.com/oauth/authorize?response_type=code&client_id=test&redirect_uri=https://example.com/callback&scope=siac.user.full_access

# 2. Ingresar credenciales: admin@siac.com / admin123

# 3. Verificar redirección con código
# https://example.com/callback?code=auth_code_XXXXXXXX
```

### **Validar Token**

```bash
curl -X POST https://auth.siac-app.com/oauth/tokeninfo \
  -d "token=access_token_XXXXXXXX"
```

---

## 📊 **Monitoreo y Analytics**

### **Métricas Disponibles**

- **Usuarios activos por cliente**
- **Intentos de login fallidos**
- **Tokens generados por día**
- **Usuarios más activos**
- **Herramientas más utilizadas por cliente**

### **Ver Logs en Tiempo Real**

```bash
# Auth Server
docker logs -f siac-auth-server

# MCP Server
docker logs -f siac-assistant
```

---

## 🚀 **Próximos Pasos**

### **Implementación Recomendada**

1. ✅ **Sistema de Login** - COMPLETADO
2. ⏳ **Base de Datos PostgreSQL** - Migrar de memoria a BD real
3. ⏳ **Hash de Contraseñas** - Implementar bcrypt
4. ⏳ **API de Gestión de Usuarios** - CRUD completo
5. ⏳ **Dashboard de Administración** - Panel web para gestionar usuarios
6. ⏳ **2FA** - Autenticación de dos factores
7. ⏳ **SSO** - Single Sign-On con Google/Microsoft

---

## 🤝 **Soporte**

Para preguntas o soporte:

- **Documentación**: Este archivo
- **Logs**: Ver en servidor VPS o local
- **Issues**: GitHub repository

---

**Última actualización**: Octubre 27, 2025  
**Versión**: 2.0.0 (Con autenticación real de usuarios)

