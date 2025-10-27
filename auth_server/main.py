# SIAC Assistant - Servidor de Autorización OAuth 2.1
# Microservicio minimalista para autenticación y autorización

from fastapi import FastAPI, HTTPException, Request, Response, Form
from fastapi.responses import JSONResponse, RedirectResponse
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import Dict, Any, Optional
import json
import logging
from datetime import datetime, timedelta
import uuid

# Configuración de logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Inicializar aplicación FastAPI
app = FastAPI(
    title="SIAC Authorization Server",
    description="Servidor de Autorización OAuth 2.1 para SIAC Assistant",
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc"
)

# Configurar CORS para ChatGPT
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "https://chatgpt.com",
        "https://chat.openai.com",
        "https://api.siac-app.com"
    ],
    allow_credentials=True,
    allow_methods=["GET", "POST", "OPTIONS"],
    allow_headers=["*"],
)

# Configuración del servidor de autorización
AUTH_SERVER_CONFIG = {
    "issuer": "https://auth.siac-app.com",
    "authorization_endpoint": "https://auth.siac-app.com/oauth/authorize",
    "token_endpoint": "https://auth.siac-app.com/oauth/token",
    "jwks_uri": "https://auth.siac-app.com/oauth/keys",
    "userinfo_endpoint": "https://auth.siac-app.com/oauth/userinfo",
    "revocation_endpoint": "https://auth.siac-app.com/oauth/revoke",
    "introspection_endpoint": "https://auth.siac-app.com/oauth/introspect"
}

# Modelos Pydantic
class TokenRequest(BaseModel):
    grant_type: str
    code: Optional[str] = None
    redirect_uri: Optional[str] = None
    client_id: Optional[str] = None
    code_verifier: Optional[str] = None
    scope: Optional[str] = None

class TokenResponse(BaseModel):
    access_token: str
    token_type: str = "Bearer"
    expires_in: int
    refresh_token: Optional[str] = None
    scope: str

class AuthorizationRequest(BaseModel):
    response_type: str
    client_id: str
    redirect_uri: str
    scope: str
    state: Optional[str] = None
    code_challenge: Optional[str] = None
    code_challenge_method: Optional[str] = None

# Endpoint de salud
@app.get("/health")
async def health_check():
    """Endpoint de verificación de salud del servidor de autorización"""
    return {
        "status": "healthy",
        "service": "SIAC Authorization Server",
        "version": "1.0.0",
        "timestamp": datetime.utcnow().isoformat(),
        "issuer": AUTH_SERVER_CONFIG["issuer"]
    }

# Endpoint de descubrimiento OpenID Connect
@app.get("/.well-known/openid-configuration")
async def openid_configuration():
    """
    Endpoint de descubrimiento OpenID Connect
    Proporciona metadatos del servidor de autorización para ChatGPT
    """
    logger.info("Solicitud de configuración OpenID Connect")
    
    configuration = {
        # Información básica del servidor
        "issuer": AUTH_SERVER_CONFIG["issuer"],
        
        # Endpoints de autorización
        "authorization_endpoint": AUTH_SERVER_CONFIG["authorization_endpoint"],
        "token_endpoint": AUTH_SERVER_CONFIG["token_endpoint"],
        "userinfo_endpoint": AUTH_SERVER_CONFIG["userinfo_endpoint"],
        "revocation_endpoint": AUTH_SERVER_CONFIG["revocation_endpoint"],
        "introspection_endpoint": AUTH_SERVER_CONFIG["introspection_endpoint"],
        
        # JWKS para verificación de tokens
        "jwks_uri": AUTH_SERVER_CONFIG["jwks_uri"],
        
        # Tipos de respuesta soportados
        "response_types_supported": ["code"],
        
        # Tipos de grant soportados
        "grant_types_supported": ["authorization_code", "refresh_token"],
        
        # Métodos de autenticación del cliente
        "token_endpoint_auth_methods_supported": ["none"],
        
        # Scopes soportados
        "scopes_supported": ["openid", "profile", "siac.user.full_access"],
        
        # Algoritmos de firma soportados
        "id_token_signing_alg_values_supported": ["RS256"],
        
        # Métodos de code challenge soportados (PKCE)
        "code_challenge_methods_supported": ["S256"],
        
        # URLs de redirección soportadas
        "redirect_uris_supported": [
            "https://chatgpt.com/oauth/callback",
            "https://chat.openai.com/oauth/callback"
        ],
        
        # Configuración adicional
        "subject_types_supported": ["public"],
        "response_modes_supported": ["query", "fragment"],
        
        # Información del servidor
        "service_documentation": "https://auth.siac-app.com/docs",
        "ui_locales_supported": ["en", "es"],
        
        # RFC 7591 Dynamic Client Registration
        "registration_endpoint": "https://auth.siac-app.com/oauth/register",
        
        # Timestamp de la configuración
        "configuration_timestamp": datetime.utcnow().isoformat()
    }
    
    logger.info(f"Configuración OpenID Connect enviada: {configuration['issuer']}")
    return configuration

# Endpoint de registro dinámico de clientes (RFC 7591)
@app.post("/oauth/register")
async def register_client(request: Request):
    """
    Endpoint de registro dinámico de clientes RFC 7591
    Permite a clientes como ChatGPT registrarse automáticamente
    """
    logger.info("Solicitud de registro dinámico de cliente recibida")
    
    try:
        # Leer el cuerpo de la solicitud
        client_metadata = await request.json()
        
        # Generar credenciales del cliente
        client_id = f"siac_client_{uuid.uuid4().hex[:16]}"
        client_secret = f"secret_{uuid.uuid4().hex[:32]}"
        
        # Extraer información del cliente
        redirect_uris = client_metadata.get("redirect_uris", [])
        client_name = client_metadata.get("client_name", "SIAC MCP Client")
        grant_types = client_metadata.get("grant_types", ["authorization_code", "refresh_token"])
        response_types = client_metadata.get("response_types", ["code"])
        token_endpoint_auth_method = client_metadata.get("token_endpoint_auth_method", "none")
        
        # Respuesta de registro según RFC 7591
        registration_response = {
            # Credenciales del cliente
            "client_id": client_id,
            "client_secret": client_secret,
            "client_id_issued_at": int(datetime.utcnow().timestamp()),
            "client_secret_expires_at": 0,  # No expira
            
            # Metadatos del cliente
            "client_name": client_name,
            "redirect_uris": redirect_uris,
            "grant_types": grant_types,
            "response_types": response_types,
            "token_endpoint_auth_method": token_endpoint_auth_method,
            
            # URLs adicionales
            "registration_client_uri": f"https://auth.siac-app.com/oauth/register/{client_id}",
            "registration_access_token": f"reg_token_{uuid.uuid4().hex[:32]}",
            
            # Información del servidor
            "issuer": AUTH_SERVER_CONFIG["issuer"]
        }
        
        logger.info(f"Cliente registrado exitosamente: {client_id}")
        logger.info(f"Redirect URIs: {redirect_uris}")
        
        return registration_response
        
    except Exception as e:
        logger.error(f"Error en registro de cliente: {str(e)}")
        raise HTTPException(
            status_code=400,
            detail=f"Error en registro de cliente: {str(e)}"
        )

# Endpoint de autorización (Mock)
@app.get("/oauth/authorize")
async def authorize(request: Request):
    """
    Endpoint de autorización OAuth 2.1
    En un entorno real, aquí se mostraría la página de login
    """
    logger.info("Solicitud de autorización recibida")
    
    # Extraer parámetros de la query
    params = dict(request.query_params)
    
    # Validar parámetros requeridos (scope es opcional)
    required_params = ["response_type", "client_id", "redirect_uri"]
    for param in required_params:
        if param not in params:
            raise HTTPException(
                status_code=400,
                detail=f"Parámetro requerido faltante: {param}"
            )
    
    # Validar response_type
    if params["response_type"] != "code":
        raise HTTPException(
            status_code=400,
            detail="response_type debe ser 'code'"
        )
    
    # Si no se proporciona scope, usar el scope por defecto
    scope = params.get("scope", "siac.user.full_access")
    params["scope"] = scope
    
    logger.info(f"Solicitud de autorización - Client ID: {params['client_id']}, Scope: {scope}")
    
    # En un entorno real, aquí se mostraría la página de login
    # Por ahora, simulamos una autorización exitosa
    authorization_code = f"auth_code_{uuid.uuid4().hex[:16]}"
    
    # Construir URL de redirección con el código de autorización
    redirect_uri = params["redirect_uri"]
    state = params.get("state", "")
    
    redirect_url = f"{redirect_uri}?code={authorization_code}"
    if state:
        redirect_url += f"&state={state}"
    
    logger.info(f"Código de autorización generado: {authorization_code}")
    logger.info(f"Redirección a: {redirect_url}")
    
    # Redirigir al usuario al redirect_uri con el código de autorización
    return RedirectResponse(url=redirect_url, status_code=302)

# Endpoint de token (Mock)
@app.post("/oauth/token")
async def token(
    grant_type: str = Form(...),
    code: str = Form(None),
    redirect_uri: str = Form(None),
    client_id: str = Form(None),
    code_verifier: str = Form(None),
    refresh_token: str = Form(None),
    scope: str = Form(None)
):
    """
    Endpoint de token OAuth 2.1
    Intercambia el código de autorización por un access token
    Acepta application/x-www-form-urlencoded
    Soporta grant_type: authorization_code y refresh_token
    """
    logger.info(f"Solicitud de token recibida - grant_type: {grant_type}, code: {code[:20] if code else 'None'}..., client_id: {client_id}")
    
    # Validar grant_type
    if grant_type not in ["authorization_code", "refresh_token"]:
        raise HTTPException(
            status_code=400,
            detail="grant_type debe ser 'authorization_code' o 'refresh_token'"
        )
    
    # Validar parámetros según el grant_type
    if grant_type == "authorization_code":
        if not code:
            raise HTTPException(
                status_code=400,
                detail="Código de autorización requerido"
            )
        
        if not redirect_uri:
            raise HTTPException(
                status_code=400,
                detail="redirect_uri requerido"
            )
    
    elif grant_type == "refresh_token":
        if not refresh_token:
            raise HTTPException(
                status_code=400,
                detail="refresh_token requerido"
            )
    
    # En un entorno real, aquí se validaría el código de autorización y el code_verifier (PKCE)
    # Por ahora, simulamos la generación de un token
    access_token = f"access_token_{uuid.uuid4().hex[:32]}"
    new_refresh_token = f"refresh_token_{uuid.uuid4().hex[:32]}"
    
    # Configurar expiración del token (1 hora)
    expires_in = 3600
    
    logger.info(f"Access token generado para client {client_id}: {access_token[:20]}...")
    
    return TokenResponse(
        access_token=access_token,
        token_type="Bearer",
        expires_in=expires_in,
        refresh_token=new_refresh_token,
        scope=scope or "siac.user.full_access"
    )

# Endpoint de información del usuario (Mock)
@app.get("/oauth/userinfo")
async def userinfo(request: Request):
    """
    Endpoint de información del usuario
    Devuelve información del usuario autenticado
    """
    logger.info("Solicitud de información del usuario")
    
    # En un entorno real, aquí se validaría el access token
    # Por ahora, simulamos información del usuario
    user_info = {
        "sub": "siac_user_12345",
        "name": "Usuario SIAC",
        "email": "usuario@siac-app.com",
        "preferred_username": "siac_user",
        "given_name": "Usuario",
        "family_name": "SIAC",
        "locale": "es",
        "zoneinfo": "America/Bogota",
        "updated_at": datetime.utcnow().isoformat()
    }
    
    logger.info(f"Información del usuario enviada: {user_info['sub']}")
    return user_info

# Endpoint de revocación de token (Mock)
@app.post("/oauth/revoke")
async def revoke_token(request: Request):
    """
    Endpoint de revocación de token
    Revoca un access token o refresh token
    """
    logger.info("Solicitud de revocación de token")
    
    # En un entorno real, aquí se revocaría el token
    # Por ahora, simulamos la revocación exitosa
    return {
        "message": "Token revocado exitosamente",
        "timestamp": datetime.utcnow().isoformat()
    }

# Endpoint de introspección de token (Mock)
@app.post("/oauth/introspect")
async def introspect_token(request: Request):
    """
    Endpoint de introspección de token
    Proporciona información sobre un token
    """
    logger.info("Solicitud de introspección de token")
    
    # En un entorno real, aquí se validaría el token
    # Por ahora, simulamos información del token
    token_info = {
        "active": True,
        "scope": "siac.user.full_access",
        "client_id": "siac_assistant",
        "username": "siac_user",
        "exp": int((datetime.utcnow() + timedelta(hours=1)).timestamp()),
        "iat": int(datetime.utcnow().timestamp()),
        "sub": "siac_user_12345",
        "aud": "siac_assistant",
        "iss": AUTH_SERVER_CONFIG["issuer"]
    }
    
    logger.info(f"Información del token enviada: {token_info['sub']}")
    return token_info

# Endpoint de JWKS (Mock)
@app.get("/oauth/keys")
async def jwks():
    """
    Endpoint de JWKS (JSON Web Key Set)
    Proporciona las claves públicas para verificar tokens JWT
    """
    logger.info("Solicitud de JWKS")
    
    # En un entorno real, aquí se devolverían las claves públicas reales
    # Por ahora, simulamos un conjunto de claves
    jwks = {
        "keys": [
            {
                "kty": "RSA",
                "kid": "siac_key_1",
                "use": "sig",
                "alg": "RS256",
                "n": "mock_public_key_modulus",
                "e": "AQAB"
            }
        ]
    }
    
    logger.info("JWKS enviado")
    return jwks

# Endpoint de documentación personalizada
@app.get("/docs")
async def custom_docs():
    """
    Endpoint de documentación personalizada del servidor de autorización
    """
    return {
        "title": "SIAC Authorization Server",
        "description": "Servidor de Autorización OAuth 2.1 para SIAC Assistant",
        "version": "1.0.0",
        "endpoints": {
            "discovery": "/.well-known/openid-configuration",
            "authorization": "/oauth/authorize",
            "token": "/oauth/token",
            "userinfo": "/oauth/userinfo",
            "revoke": "/oauth/revoke",
            "introspect": "/oauth/introspect",
            "jwks": "/oauth/keys"
        },
        "supported_scopes": ["openid", "profile", "siac.user.full_access"],
        "supported_grant_types": ["authorization_code", "refresh_token"],
        "issuer": AUTH_SERVER_CONFIG["issuer"]
    }

# Manejo de errores global
@app.exception_handler(HTTPException)
async def http_exception_handler(request: Request, exc: HTTPException):
    """Manejador global de errores HTTP"""
    logger.error(f"Error HTTP {exc.status_code}: {exc.detail}")
    return JSONResponse(
        status_code=exc.status_code,
        content={
            "error": exc.detail,
            "status_code": exc.status_code,
            "timestamp": datetime.utcnow().isoformat()
        }
    )

# Middleware de logging
@app.middleware("http")
async def log_requests(request: Request, call_next):
    """Middleware para logging de requests"""
    start_time = datetime.utcnow()
    
    # Log de request
    logger.info(f"Request: {request.method} {request.url}")
    
    # Procesar request
    response = await call_next(request)
    
    # Log de response
    process_time = (datetime.utcnow() - start_time).total_seconds()
    logger.info(f"Response: {response.status_code} - {process_time:.3f}s")
    
    return response

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "main:app",
        host="0.0.0.0",
        port=8080,
        reload=False,
        log_level="info"
    )



