# SIAC Assistant

Sistema de Asistencia Inteligente con Capacidades Avanzadas (SIAC Assistant) - Backend FastMCP con PostgreSQL.

## Estructura del Proyecto

```
SIAC Assistant/
├── server/                 # Backend FastMCP
│   ├── main.py            # Punto de entrada principal
│   ├── requirements.txt   # Dependencias de Python
│   ├── Dockerfile         # Configuración Docker para backend
│   ├── .dockerignore      # Archivos ignorados en Docker
│   └── venv/              # Entorno virtual de Python
├── web/                   # Frontend React/TypeScript (futuro)
└── docker-compose.yml     # Configuración de servicios Docker
```

## Servicios Docker

### Base de Datos PostgreSQL
- **Usuario**: siac
- **Contraseña**: siac123
- **Base de datos**: siac_chatgpt
- **Puerto**: 5432

### Backend FastMCP
- **Puerto**: 8000
- **Framework**: FastAPI + MCP
- **Base de datos**: PostgreSQL

## Dependencias Principales

- **FastAPI**: Framework web moderno y rápido
- **Uvicorn**: Servidor ASGI de alto rendimiento
- **MCP**: Model Context Protocol SDK
- **SQLAlchemy**: ORM para Python
- **PostgreSQL**: Base de datos relacional
- **Alembic**: Migraciones de base de datos

## Configuración del Entorno

### Desarrollo Local

1. **Activar entorno virtual**:
   ```bash
   cd server
   source venv/bin/activate
   ```

2. **Instalar dependencias**:
   ```bash
   pip install -r requirements.txt
   ```

3. **Ejecutar servidor**:
   ```bash
   python main.py
   ```

### Docker

1. **Construir y ejecutar servicios**:
   ```bash
   docker-compose up --build
   ```

2. **Ejecutar en segundo plano**:
   ```bash
   docker-compose up -d
   ```

3. **Ver logs**:
   ```bash
   docker-compose logs -f
   ```

## Endpoints Disponibles

### Endpoints Públicos (Sin Autenticación)
- `GET /`: Información básica del servicio
- `GET /health`: Verificación de salud del servicio
- `GET /auth/info`: Información de configuración OAuth 2.1

### Endpoints Protegidos (OAuth 2.1 Requerido)
- `GET /protected/user`: Información del usuario autenticado
- `GET /protected/test`: Endpoint de prueba para recursos protegidos

## Autenticación OAuth 2.1

### Configuración
- **Issuer URL**: `https://auth.siac-app.com`
- **Resource Server**: `https://api.siac-app.com/mcp`
- **Scope Requerido**: `siac.user.full_access`
- **Audience**: `siac-assistant`

### Flujo de Autenticación
1. El cliente debe obtener un access token del Authorization Server
2. Incluir el token en el header: `Authorization: Bearer <token>`
3. El servidor valida: issuer, audience, expiración y scopes
4. Si falla la validación, retorna `401 Unauthorized` con header `WWW-Authenticate`

### Testing
```bash
# Ejecutar tests de autenticación
python test_auth.py

# Ejecutar tests de herramientas read-only
python test_readonly_tools.py

# Ejecutar tests de herramientas write-action
python test_write_tools.py
```

## Herramientas MCP Disponibles

### Herramientas de Solo Lectura (Read-Only)

#### siac.validate_template
- **Propósito**: Validar plantillas de WhatsApp para cumplimiento, calidad y estado de aprobación
- **Parámetros**:
  - `template_name` (string): Nombre de la plantilla
  - `body_text` (string): Contenido del texto de la plantilla
  - `category` (string): Categoría (Marketing, Utility, Authentication)
  - `language_code` (string): Código de idioma (ej. 'es_ES')
- **UI Widget**: `TemplateValidationCard.html`
- **readOnlyHint**: `true`

#### siac.get_campaign_metrics
- **Propósito**: Obtener métricas detalladas y datos de rendimiento de campañas específicas
- **Parámetros**:
  - `campaign_id` (string): UUID de la campaña a consultar
- **UI Widget**: `CampaignMetricsWidget.html`
- **readOnlyHint**: `true`

### Herramientas de Escritura (Write Actions)

#### siac.register_template
- **Propósito**: Registrar una plantilla validada en SIAC y enviarla a Meta para aprobación final
- **Parámetros**:
  - `template_id` (string): UUID de la plantilla a registrar
  - `meta_template_id` (string): ID de Meta después de la subida
  - `client_id` (string): UUID del cliente para trazabilidad
- **Widget Accessible**: `true` (TemplateValidationCard puede invocar esta herramienta)
- **Autenticación**: OAuth 2.1 requerido
- **Confirmación**: Requiere confirmación explícita del usuario

#### siac.send_broadcast
- **Propósito**: Programar y enviar una campaña de difusión a un segmento específico de clientes
- **Parámetros**:
  - `template_id` (string): UUID de la plantilla aprobada
  - `segment_name` (string): Nombre del segmento de clientes (ej. 'clientes_recurrentes')
  - `schedule_time_utc` (string): Fecha y hora programada en UTC (ISO 8601)
- **UI Widget**: `BroadcastConfirmationCard.html`
- **Autenticación**: OAuth 2.1 requerido
- **Confirmación**: Requiere confirmación explícita del usuario

### Herramientas Generales
- `get_user_info`: Información del usuario actual
- `test_protected_action`: Acción protegida de prueba

## Próximos Pasos

1. Configuración de modelos de base de datos
2. Implementación de endpoints MCP
3. Desarrollo del frontend React/TypeScript
4. Configuración de autenticación y autorización
5. Implementación de funcionalidades de IA
