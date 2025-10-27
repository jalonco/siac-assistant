# SIAC Assistant - MCP Server with OAuth 2.1

![License](https://img.shields.io/badge/license-MIT-blue.svg)
![Python](https://img.shields.io/badge/python-3.11+-blue.svg)
![FastAPI](https://img.shields.io/badge/FastAPI-0.104+-green.svg)

Sistema de integración MCP (Model Context Protocol) para SIAC con autenticación OAuth 2.1, diseñado para conectarse con ChatGPT y otros clientes MCP.

## 🚀 Características

- **OAuth 2.1 Authentication** - Servidor de autorización completo con RFC 7591 (Dynamic Client Registration)
- **MCP Protocol** - Implementación completa del protocolo MCP 2024-11-05
- **RFC 8707** - Protected Resource Metadata para descubrimiento de servicios
- **PKCE Support** - Proof Key for Code Exchange para mayor seguridad
- **FastAPI Backend** - API moderna y eficiente
- **Docker Support** - Despliegue fácil con Docker Compose
- **SSL/TLS** - Configuración completa para producción
- **Token Verification** - Sistema robusto de validación de tokens

## 📋 Requisitos

- Python 3.11+
- Docker & Docker Compose (opcional, para deployment)
- PostgreSQL (para producción)
- Node.js 18+ (para componentes web)

## 🏗️ Arquitectura

```
┌─────────────────┐
│   ChatGPT/      │
│   MCP Client    │
└────────┬────────┘
         │ HTTPS + OAuth 2.1
         ▼
┌─────────────────────────────────┐
│   SIAC Assistant MCP Server     │
│   (FastAPI + MCP Protocol)      │
│                                 │
│   ┌─────────────────────────┐  │
│   │  OAuth Authorization    │  │
│   │  Server                 │  │
│   └─────────────────────────┘  │
│                                 │
│   ┌─────────────────────────┐  │
│   │  MCP Handler            │  │
│   │  (JSON-RPC 2.0)         │  │
│   └─────────────────────────┘  │
└─────────────────────────────────┘
         │
         ▼
┌─────────────────┐
│   PostgreSQL    │
│   Database      │
└─────────────────┘
```

## 🛠️ Instalación Local

### 1. Clonar el repositorio

```bash
git clone https://github.com/tu-usuario/siac-assistant.git
cd siac-assistant
```

### 2. Configurar entorno Python

```bash
# Crear entorno virtual
python -m venv venv
source venv/bin/activate  # En Windows: venv\Scripts\activate

# Instalar dependencias del servidor
pip install -r server/requirements.txt

# Instalar dependencias del auth server
pip install -r auth_server/requirements.txt
```

### 3. Configurar variables de entorno

```bash
cp .env.example .env
# Editar .env con tus configuraciones
```

### 4. Ejecutar en desarrollo

```bash
# Terminal 1: Auth Server
cd auth_server
uvicorn main:app --reload --port 8080

# Terminal 2: MCP Server
cd server
uvicorn main:app --reload --port 8888
```

## 🐳 Despliegue con Docker

### Desarrollo

```bash
docker-compose up -d
```

### Producción

```bash
docker-compose -f docker-compose.production.yml up -d
```

## 📡 Endpoints Principales

### OAuth 2.1 Server (`auth.siac-app.com`)

- `GET /.well-known/openid-configuration` - OpenID Connect Discovery
- `POST /oauth/register` - Dynamic Client Registration (RFC 7591)
- `GET /oauth/authorize` - Authorization Endpoint
- `POST /oauth/token` - Token Endpoint
- `GET /oauth/userinfo` - UserInfo Endpoint

### MCP Server (`api.siac-app.com/mcp`)

- `GET /.well-known/oauth-protected-resource` - Protected Resource Metadata (RFC 8707)
- `POST /mcp` - MCP Protocol Handler (JSON-RPC 2.0)
  - `initialize` - Inicializar conexión
  - `tools/list` - Listar herramientas disponibles
  - `tools/call` - Ejecutar herramientas
  - `resources/list` - Listar recursos
  - `prompts/list` - Listar prompts

## 🔧 Configuración de ChatGPT

1. En ChatGPT, ir a **Settings** → **Beta Features** → **Custom GPTs & Actions**
2. Crear nuevo **Custom Action**
3. Configurar MCP Server:
   - **URL**: `https://api.siac-app.com/mcp`
   - **Authentication**: OAuth 2.1
4. ChatGPT se registrará automáticamente usando Dynamic Client Registration

## 🛡️ Seguridad

- OAuth 2.1 con PKCE obligatorio
- Tokens JWT firmados (en producción)
- HTTPS obligatorio en producción
- Rate limiting implementado
- CORS configurado apropiadamente
- Validación estricta de scopes

## 🧪 Testing

```bash
# Tests unitarios
pytest server/test_*.py

# Test de conexión MCP
python test_mcp_server.py

# Test de flujo OAuth
python test_security_flow.py
```

## 📚 Documentación Adicional

- [Guía de Conexión con ChatGPT](CHATGPT_CONNECTION_GUIDE.md)
- [Documentación del Auth Server](AUTH_SERVER_DOCUMENTATION.md)
- [Guía de Ejecución Local](LOCAL_EXECUTION_GUIDE.md)
- [Instrucciones de Deployment](DEPLOYMENT_INSTRUCTIONS.md)
- [Configuración SSL](SSL_CONFIGURATION.md)
- [Resumen de Seguridad](SECURITY_FLOW_SUMMARY.md)

## 🏗️ Estructura del Proyecto

```
siac-assistant/
├── auth_server/          # Servidor de autorización OAuth 2.1
│   ├── main.py          # Implementación del auth server
│   └── requirements.txt
├── server/              # Servidor MCP principal
│   ├── main.py         # Implementación MCP + FastAPI
│   ├── schemas.py      # Modelos Pydantic
│   └── requirements.txt
├── web/                # Componentes web (React/TypeScript)
│   └── src/
├── traefik/            # Configuración del reverse proxy
├── docker-compose.yml  # Desarrollo
└── README.md
```

## 🤝 Contribución

Las contribuciones son bienvenidas. Por favor:

1. Fork el proyecto
2. Crea una rama para tu feature (`git checkout -b feature/AmazingFeature`)
3. Commit tus cambios (`git commit -m 'Add some AmazingFeature'`)
4. Push a la rama (`git push origin feature/AmazingFeature`)
5. Abre un Pull Request

## 📝 Estándares de Código

- Seguir PEP 8 para Python
- Usar type hints en todas las funciones
- Documentar con docstrings (Google style)
- Nombres descriptivos de variables y funciones
- Tests para nuevas funcionalidades

## 📄 Licencia

Este proyecto está bajo la Licencia MIT - ver el archivo [LICENSE](LICENSE) para más detalles.

## 👥 Autores

- **SIAC Enterprise** - *Trabajo inicial*

## 🙏 Agradecimientos

- [FastAPI](https://fastapi.tiangolo.com/) - Framework web moderno
- [MCP Protocol](https://modelcontextprotocol.io/) - Protocolo de contexto de modelo
- [OAuth 2.1](https://oauth.net/2.1/) - Estándar de autorización

## 📞 Soporte

Para soporte, por favor abre un issue en GitHub o contacta al equipo de desarrollo.

---

**Nota**: Este es un proyecto en desarrollo activo. Las características y la API pueden cambiar.
