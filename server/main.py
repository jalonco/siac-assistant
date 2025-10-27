"""
SIAC Assistant - FastMCP Server with OAuth 2.1 Authentication

This module initializes the FastMCP server with Custom Auth using OAuth 2.1
for secure access to SIAC resources and protected operations.
"""

import logging
from datetime import datetime, timezone
from typing import Optional, Dict, Any, List
from uuid import UUID

from fastapi import FastAPI, HTTPException, Depends, Request, status, Response
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from fastapi.responses import JSONResponse
from pydantic import BaseModel, Field
import uvicorn

from mcp.server import Server
from mcp.server.stdio import stdio_server
from mcp.types import (
    CallToolRequest,
    CallToolResult,
    ListToolsRequest,
    ListToolsResult,
    Tool,
    TextContent,
    ImageContent,
    EmbeddedResource,
    Resource,
    ListResourcesRequest,
    ListResourcesResult,
    ReadResourceRequest,
    ReadResourceResult,
    METHOD_NOT_FOUND,
    JSONRPCError,
)

# Import schemas for enum usage
from schemas import TemplateCategory

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# ============================================================================
# OAUTH 2.1 AUTHENTICATION CONFIGURATION
# ============================================================================

class AuthSettings(BaseModel):
    """
    OAuth 2.1 authentication settings for SIAC Assistant.
    
    Attributes:
        issuer_url: OAuth 2.1 issuer URL for token validation
        resource_server_url: Resource server URL for protected endpoints
        required_scope: Required scope for accessing protected resources
        audience: Expected audience in JWT tokens
    """
    issuer_url: str = Field(default="https://auth.siac-app.com", description="OAuth 2.1 issuer URL")
    resource_server_url: str = Field(default="https://api.siac-app.com/mcp", description="Resource server URL")
    required_scope: str = Field(default="siac.user.full_access", description="Required scope for access")
    audience: str = Field(default="siac-assistant", description="Expected audience in JWT tokens")

# Global auth settings instance
auth_settings = AuthSettings()

# ============================================================================
# TOKEN VERIFICATION SYSTEM
# ============================================================================

class TokenVerifier:
    """
    Token verification class for OAuth 2.1 access tokens.
    
    This class simulates the verification of JWT tokens including:
    - Issuer validation
    - Audience validation  
    - Expiration validation
    - Scope validation
    """
    
    def __init__(self, auth_settings: AuthSettings):
        """
        Initialize the token verifier with authentication settings.
        
        Args:
            auth_settings: Authentication settings containing issuer, audience, etc.
        """
        self.auth_settings = auth_settings
        self.logger = logging.getLogger(f"{__name__}.TokenVerifier")
    
    def verify_token(self, token: str) -> Dict[str, Any]:
        """
        Verify an OAuth 2.1 access token with strict validation.
        
        This method performs comprehensive token validation including:
        - Token presence and format validation
        - Issuer validation against configured issuer URL
        - Audience validation against configured audience
        - Expiration time validation
        - Required scope validation (siac.user.full_access)
        
        Args:
            token: The access token to verify
            
        Returns:
            Dict containing token claims if valid
            
        Raises:
            HTTPException: If token is invalid, expired, or lacks required scopes
        """
        if not token or token.strip() == "":
            self.logger.warning("Token verification failed: No token provided")
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Access token is required",
                headers={"WWW-Authenticate": f'Bearer realm="{self.auth_settings.resource_server_url}", scope="{self.auth_settings.required_scope}"'}
            )
        
        try:
            # Simulate token parsing and validation
            # In a real implementation, this would decode and verify the JWT
            token_claims = self._parse_token(token)
            
            # Verify issuer
            if token_claims.get("iss") != self.auth_settings.issuer_url:
                self.logger.warning(f"Token verification failed: Invalid issuer. Expected {self.auth_settings.issuer_url}, got {token_claims.get('iss')}")
                raise HTTPException(
                    status_code=status.HTTP_401_UNAUTHORIZED,
                    detail="Invalid token issuer",
                    headers={"WWW-Authenticate": f'Bearer realm="{self.auth_settings.resource_server_url}", scope="{self.auth_settings.required_scope}"'}
                )
            
            # Verify audience
            if token_claims.get("aud") != self.auth_settings.audience:
                self.logger.warning(f"Token verification failed: Invalid audience. Expected {self.auth_settings.audience}, got {token_claims.get('aud')}")
                raise HTTPException(
                    status_code=status.HTTP_401_UNAUTHORIZED,
                    detail="Invalid token audience",
                    headers={"WWW-Authenticate": f'Bearer realm="{self.auth_settings.resource_server_url}", scope="{self.auth_settings.required_scope}"'}
                )
            
            # Verify expiration
            exp_timestamp = token_claims.get("exp")
            if exp_timestamp and datetime.fromtimestamp(exp_timestamp, tz=timezone.utc) < datetime.now(timezone.utc):
                self.logger.warning("Token verification failed: Token expired")
                raise HTTPException(
                    status_code=status.HTTP_401_UNAUTHORIZED,
                    detail="Token has expired",
                    headers={"WWW-Authenticate": f'Bearer realm="{self.auth_settings.resource_server_url}", scope="{self.auth_settings.required_scope}"'}
                )
            
            # Verify required scope - STRICT VALIDATION
            token_scopes = token_claims.get("scope", "").split()
            if self.auth_settings.required_scope not in token_scopes:
                self.logger.warning(f"Token verification failed: Missing required scope. Required: {self.auth_settings.required_scope}, Available: {token_scopes}")
                raise HTTPException(
                    status_code=status.HTTP_401_UNAUTHORIZED,
                    detail=f"Missing required scope: {self.auth_settings.required_scope}",
                    headers={"WWW-Authenticate": f'Bearer realm="{self.auth_settings.resource_server_url}", scope="{self.auth_settings.required_scope}"'}
                )
            
            # Additional validation: Check token format (basic JWT structure)
            # Skip validation for mock tokens from our auth server or test scenarios
            if (token not in ["valid_token", "expired_token", "invalid_issuer", "missing_scope", "invalid_audience", "malformed_token"] and 
                not token.startswith("eyJ") and 
                not token.startswith("access_token_")):
                if not self._is_valid_token_format(token):
                    self.logger.warning("Token verification failed: Invalid token format")
                    raise HTTPException(
                        status_code=status.HTTP_401_UNAUTHORIZED,
                        detail="Invalid token format",
                        headers={"WWW-Authenticate": f'Bearer realm="{self.auth_settings.resource_server_url}", scope="{self.auth_settings.required_scope}"'}
                    )
            
            self.logger.info(f"Token verification successful for user: {token_claims.get('sub', 'unknown')} with scopes: {token_scopes}")
            return token_claims
            
        except HTTPException:
            # Re-raise HTTP exceptions
            raise
        except Exception as e:
            self.logger.error(f"Token verification failed with unexpected error: {str(e)}")
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Token verification failed",
                headers={"WWW-Authenticate": f'Bearer realm="{self.auth_settings.resource_server_url}", scope="{self.auth_settings.required_scope}"'}
            )
    
    def _parse_token(self, token: str) -> Dict[str, Any]:
        """
        Parse and simulate token claims.
        
        This is a simulation for development purposes.
        In production, this would decode and verify a real JWT.
        
        Args:
            token: The access token to parse
            
        Returns:
            Dict containing simulated token claims
        """
        # Accept tokens generated by our mock auth server (access_token_XXXXXXXX)
        if token.startswith("access_token_"):
            self.logger.info(f"Accepting mock access token: {token[:30]}...")
            return {
                "iss": self.auth_settings.issuer_url,
                "aud": self.auth_settings.audience,
                "sub": "chatgpt_user",
                "scope": self.auth_settings.required_scope,
                "exp": int(datetime.now(timezone.utc).timestamp()) + 3600,  # 1 hour from now
                "iat": int(datetime.now(timezone.utc).timestamp()),
                "client_id": token.replace("access_token_", "client_")[:20]
            }
        
        # Simulate different token scenarios for testing
        if token == "valid_token":
            return {
                "iss": self.auth_settings.issuer_url,
                "aud": self.auth_settings.audience,
                "sub": "user123",
                "scope": f"{self.auth_settings.required_scope} siac.user.read",
                "exp": int(datetime.now(timezone.utc).timestamp()) + 3600,  # 1 hour from now
                "iat": int(datetime.now(timezone.utc).timestamp()),
                "client_id": "siac-client"
            }
        elif token == "expired_token":
            return {
                "iss": self.auth_settings.issuer_url,
                "aud": self.auth_settings.audience,
                "sub": "user123",
                "scope": self.auth_settings.required_scope,
                "exp": int(datetime.now(timezone.utc).timestamp()) - 3600,  # 1 hour ago
                "iat": int(datetime.now(timezone.utc).timestamp()) - 7200,
                "client_id": "siac-client"
            }
        elif token == "invalid_issuer":
            return {
                "iss": "https://invalid-issuer.com",
                "aud": self.auth_settings.audience,
                "sub": "user123",
                "scope": self.auth_settings.required_scope,
                "exp": int(datetime.now(timezone.utc).timestamp()) + 3600,
                "iat": int(datetime.now(timezone.utc).timestamp()),
                "client_id": "siac-client"
            }
        elif token == "missing_scope":
            return {
                "iss": self.auth_settings.issuer_url,
                "aud": self.auth_settings.audience,
                "sub": "user123",
                "scope": "siac.user.read",  # Missing required scope
                "exp": int(datetime.now(timezone.utc).timestamp()) + 3600,
                "iat": int(datetime.now(timezone.utc).timestamp()),
                "client_id": "siac-client"
            }
        elif token == "invalid_audience":
            return {
                "iss": self.auth_settings.issuer_url,
                "aud": "https://wrong-audience.com",  # Wrong audience
                "sub": "user123",
                "scope": self.auth_settings.required_scope,
                "exp": int(datetime.now(timezone.utc).timestamp()) + 3600,
                "iat": int(datetime.now(timezone.utc).timestamp()),
                "client_id": "siac-client"
            }
        elif token == "malformed_token":
            # This will trigger format validation failure by raising an exception
            raise ValueError("Invalid token format")
        elif token.startswith("Bearer "):
            # Handle Bearer token format - validate the actual token part
            actual_token = token[7:]  # Remove "Bearer " prefix
            if actual_token == "valid_token":
                return self._parse_token(actual_token)
            elif actual_token.startswith("eyJ"):  # JWT format
                # For JWT format, return valid claims
                return {
                    "iss": self.auth_settings.issuer_url,
                    "aud": self.auth_settings.audience,
                    "sub": "user123",
                    "scope": f"{self.auth_settings.required_scope} siac.user.read",
                    "exp": int(datetime.now(timezone.utc).timestamp()) + 3600,
                    "iat": int(datetime.now(timezone.utc).timestamp()),
                    "client_id": "siac-client"
                }
            else:
                # For Bearer format with invalid token, validate format
                if not self._is_valid_token_format(actual_token):
                    raise ValueError("Invalid token format")
                return self._parse_token(actual_token)
        else:
            # For any other token, simulate parsing error
            raise ValueError("Invalid token format")
    
    def _is_valid_token_format(self, token: str) -> bool:
        """
        Validate basic JWT token format.
        
        Args:
            token: The token to validate
            
        Returns:
            True if token has basic JWT structure, False otherwise
        """
        if not token or not isinstance(token, str):
            return False
        
        # Basic JWT structure check: should have 3 parts separated by dots
        parts = token.split('.')
        if len(parts) != 3:
            return False
        
        # Each part should be base64-like (alphanumeric + some special chars)
        import re
        base64_pattern = re.compile(r'^[A-Za-z0-9_-]+$')
        
        for part in parts:
            if not part or not base64_pattern.match(part):
                return False
        
        return True

# Global token verifier instance
token_verifier = TokenVerifier(auth_settings)

# ============================================================================
# FASTAPI APPLICATION WITH OAUTH 2.1 PROTECTION
# ============================================================================

# Initialize FastAPI application
app = FastAPI(
    title="SIAC Assistant",
    version="1.0.0",
    description="SIAC Assistant FastMCP Server with OAuth 2.1 Authentication",
    docs_url="/docs",
    redoc_url="/redoc"
)

# HTTP Bearer token security scheme
security = HTTPBearer()

def get_current_user(credentials: HTTPAuthorizationCredentials = Depends(security)) -> Dict[str, Any]:
    """
    Dependency to get the current authenticated user from the access token.
    
    Args:
        credentials: HTTP Bearer credentials containing the access token
        
    Returns:
        Dict containing user information from token claims
        
    Raises:
        HTTPException: If authentication fails
    """
    token = credentials.credentials
    return token_verifier.verify_token(token)

# ============================================================================
# PUBLIC ENDPOINTS (NO AUTHENTICATION REQUIRED)
# ============================================================================

@app.get("/")
async def root():
    """
    Root endpoint providing basic server information.
    
    Returns:
        Dict containing server status and authentication information
    """
    return {
        "message": "SIAC Assistant FastMCP Server is running",
        "version": "1.0.0",
        "authentication": "OAuth 2.1 Custom Auth",
        "issuer": auth_settings.issuer_url,
        "required_scope": auth_settings.required_scope,
        "docs": "/docs"
    }

@app.get("/health")
async def health_check():
    """
    Health check endpoint for monitoring.
    
    Returns:
        Dict containing health status
    """
    return {
        "status": "healthy",
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "service": "siac-assistant-mcp"
    }

@app.get("/auth/info")
async def auth_info():
    """
    Authentication information endpoint.
    
    Returns:
        Dict containing OAuth 2.1 configuration information
    """
    return {
        "issuer_url": auth_settings.issuer_url,
        "resource_server_url": auth_settings.resource_server_url,
        "required_scope": auth_settings.required_scope,
        "audience": auth_settings.audience,
        "auth_type": "OAuth 2.1 Custom Auth"
    }

@app.get("/.well-known/oauth-authorization-server")
async def oauth_authorization_server():
    """
    OAuth Authorization Server Metadata endpoint.
    
    This endpoint provides OAuth 2.1 server metadata for MCP clients like ChatGPT.
    
    Returns:
        Dict containing OAuth 2.1 authorization server metadata
    """
    return {
        "issuer": auth_settings.issuer_url,
        "authorization_endpoint": f"{auth_settings.issuer_url}/oauth/authorize",
        "token_endpoint": f"{auth_settings.issuer_url}/oauth/token",
        "registration_endpoint": f"{auth_settings.issuer_url}/oauth/register",
        "jwks_uri": f"{auth_settings.issuer_url}/oauth/keys",
        "response_types_supported": ["code"],
        "grant_types_supported": ["authorization_code", "refresh_token"],
        "token_endpoint_auth_methods_supported": ["none"],
        "scopes_supported": ["openid", "profile", "siac.user.full_access"],
        "code_challenge_methods_supported": ["S256"],
        "service_documentation": f"{auth_settings.issuer_url}/docs"
    }

@app.get("/.well-known/oauth-protected-resource")
async def oauth_protected_resource():
    """
    OAuth 2.0 Protected Resource Metadata endpoint (RFC 8707).
    
    This endpoint provides information about the protected resource server
    and its authorization requirements.
    
    Returns:
        Dict containing protected resource metadata
    """
    return {
        "resource": auth_settings.resource_server_url,
        "authorization_servers": [auth_settings.issuer_url],
        "scopes_supported": ["siac.user.full_access"],
        "bearer_methods_supported": ["header"],
        "resource_signing_alg_values_supported": ["RS256"],
        "resource_documentation": f"{auth_settings.resource_server_url}/docs",
        "resource_policy_uri": f"{auth_settings.resource_server_url}/policy"
    }

@app.get("/mcp")
async def mcp_info():
    """
    MCP Server information endpoint.
    
    Returns:
        Dict containing MCP server information and OAuth configuration
    """
    return {
        "name": "SIAC Assistant MCP Server",
        "version": "1.0.0",
        "protocol": "mcp",
        "oauth": {
            "issuer": auth_settings.issuer_url,
            "authorization_endpoint": f"{auth_settings.issuer_url}/oauth/authorize",
            "token_endpoint": f"{auth_settings.issuer_url}/oauth/token",
            "scopes": ["siac.user.full_access"],
            "authorization_server_metadata_url": "https://api.siac-app.com/.well-known/oauth-authorization-server"
        },
        "endpoints": {
            "health": "/health",
            "auth_info": "/auth/info",
            "oauth_metadata": "/.well-known/oauth-authorization-server",
            "protected_resource_metadata": "/.well-known/oauth-protected-resource"
        }
    }

@app.post("/mcp")
async def mcp_handler(request: Request, current_user: Dict[str, Any] = Depends(get_current_user)):
    """
    MCP Server request handler (JSON-RPC 2.0).
    
    This endpoint handles MCP protocol requests from authenticated clients.
    Requires OAuth 2.1 authentication.
    
    Args:
        request: HTTP request containing JSON-RPC 2.0 payload
        current_user: Authenticated user from OAuth token
        
    Returns:
        JSON-RPC 2.0 response
    """
    try:
        # Parse JSON-RPC request
        json_rpc_request = await request.json()
        method = json_rpc_request.get("method")
        request_id = json_rpc_request.get("id")
        
        logger.info(f"MCP Request from user {current_user.get('sub')}: {method}")
        
        # Handle different MCP methods
        if method == "initialize":
            # Initialize response with server capabilities
            return {
                "jsonrpc": "2.0",
                "id": request_id,
                "result": {
                    "protocolVersion": "2024-11-05",
                    "capabilities": {
                        "tools": {
                            "listChanged": True
                        },
                        "resources": {
                            "subscribe": True,
                            "listChanged": True
                        },
                        "prompts": {
                            "listChanged": True
                        }
                    },
                    "serverInfo": {
                        "name": "SIAC Assistant MCP Server",
                        "version": "1.0.0"
                    }
                }
            }
        
        elif method == "tools/list":
            # List available tools
            return {
                "jsonrpc": "2.0",
                "id": request_id,
                "result": {
                    "tools": [
                        {
                            "name": "get_system_info",
                            "description": "Obtiene información del sistema SIAC",
                            "inputSchema": {
                                "type": "object",
                                "properties": {},
                                "required": []
                            }
                        },
                        {
                            "name": "query_database",
                            "description": "Realiza consultas a la base de datos SIAC",
                            "inputSchema": {
                                "type": "object",
                                "properties": {
                                    "query": {
                                        "type": "string",
                                        "description": "Consulta SQL a ejecutar"
                                    }
                                },
                                "required": ["query"]
                            }
                        }
                    ]
                }
            }
        
        elif method == "resources/list":
            # List available resources
            return {
                "jsonrpc": "2.0",
                "id": request_id,
                "result": {
                    "resources": [
                        {
                            "uri": "siac://system/status",
                            "name": "Estado del Sistema",
                            "description": "Estado actual del sistema SIAC",
                            "mimeType": "application/json"
                        }
                    ]
                }
            }
        
        elif method == "prompts/list":
            # List available prompts
            return {
                "jsonrpc": "2.0",
                "id": request_id,
                "result": {
                    "prompts": [
                        {
                            "name": "siac_help",
                            "description": "Ayuda y documentación del sistema SIAC"
                        }
                    ]
                }
            }
        
        elif method == "tools/call":
            # Execute a tool
            params = json_rpc_request.get("params", {})
            tool_name = params.get("name")
            
            logger.info(f"Tool call: {tool_name}")
            
            return {
                "jsonrpc": "2.0",
                "id": request_id,
                "result": {
                    "content": [
                        {
                            "type": "text",
                            "text": f"Herramienta {tool_name} ejecutada exitosamente. Sistema SIAC operativo."
                        }
                    ]
                }
            }
        
        elif method == "notifications/initialized":
            # Client notification that initialization is complete
            # This is a notification (no id), so we don't send a response
            logger.info("Client initialization complete notification received")
            # For notifications, we return None or an empty response
            return Response(status_code=200)
        
        elif method.startswith("notifications/"):
            # Handle other notifications
            logger.info(f"Notification received: {method}")
            return Response(status_code=200)
        
        elif method == "ping":
            # Ping/pong for connection keep-alive
            return {
                "jsonrpc": "2.0",
                "id": request_id,
                "result": {}
            }
        
        else:
            # Unknown method
            logger.warning(f"Unknown MCP method: {method}")
            return {
                "jsonrpc": "2.0",
                "id": request_id,
                "error": {
                    "code": -32601,
                    "message": f"Method not found: {method}"
                }
            }
        
    except Exception as e:
        logger.error(f"Error processing MCP request: {str(e)}")
        return {
            "jsonrpc": "2.0",
            "id": json_rpc_request.get("id") if 'json_rpc_request' in locals() else None,
            "error": {
                "code": -32603,
                "message": "Internal error",
                "data": str(e)
            }
        }

# ============================================================================
# PROTECTED ENDPOINTS (OAUTH 2.1 AUTHENTICATION REQUIRED)
# ============================================================================

@app.get("/protected/user")
async def get_current_user_info(current_user: Dict[str, Any] = Depends(get_current_user)):
    """
    Get current user information from the authenticated token.
    
    Args:
        current_user: Current authenticated user from token
        
    Returns:
        Dict containing user information
    """
    return {
        "user_id": current_user.get("sub"),
        "client_id": current_user.get("client_id"),
        "scopes": current_user.get("scope", "").split(),
        "authenticated_at": datetime.now(timezone.utc).isoformat()
    }

@app.get("/protected/test")
async def protected_test(current_user: Dict[str, Any] = Depends(get_current_user)):
    """
    Test endpoint for protected resources.
    
    Args:
        current_user: Current authenticated user from token
        
    Returns:
        Dict confirming successful authentication
    """
    return {
        "message": "Successfully accessed protected resource",
        "user": current_user.get("sub"),
        "timestamp": datetime.now(timezone.utc).isoformat()
    }

# ============================================================================
# MCP SERVER INTEGRATION
# ============================================================================

# Initialize MCP server
mcp_server = Server("siac-assistant")

@mcp_server.list_tools()
async def list_tools() -> List[Tool]:
    """
    List available MCP tools.
    
    Returns:
        List of available tools
    """
    return [
        Tool(
            name="get_user_info",
            description="Get current user information",
            inputSchema={
                "type": "object",
                "properties": {},
                "required": []
            }
        ),
        Tool(
            name="test_protected_action",
            description="Test a protected action requiring authentication",
            inputSchema={
                "type": "object",
                "properties": {
                    "action": {
                        "type": "string",
                        "description": "Action to perform"
                    }
                },
                "required": ["action"]
            }
        ),
        Tool(
            name="siac.validate_template",
            description="Use this when you need to validate a WhatsApp message template for compliance, quality, and approval status before sending campaigns.",
            inputSchema={
                "type": "object",
                "properties": {
                    "template_name": {
                        "type": "string",
                        "description": "Name of the template to validate"
                    },
                    "body_text": {
                        "type": "string",
                        "description": "The body text content of the template"
                    },
                    "category": {
                        "type": "string",
                        "enum": ["Marketing", "Utility", "Authentication"],
                        "description": "Template category (Marketing, Utility, or Authentication)"
                    },
                    "language_code": {
                        "type": "string",
                        "description": "Language code for the template (e.g., 'es_ES', 'en_US')"
                    }
                },
                "required": ["template_name", "body_text", "category", "language_code"]
            },
            readOnlyHint=True,
            _meta={
                "openai/outputTemplate": "ui://widget/TemplateValidationCard.html"
            }
        ),
        Tool(
            name="siac.get_campaign_metrics",
            description="Use this when you need to retrieve detailed metrics and performance data for a specific campaign to analyze delivery rates, status, and quality scores.",
            inputSchema={
                "type": "object",
                "properties": {
                    "campaign_id": {
                        "type": "string",
                        "description": "UUID string identifier of the campaign to query"
                    }
                },
                "required": ["campaign_id"]
            },
            readOnlyHint=True,
            _meta={
                "openai/outputTemplate": "ui://widget/CampaignMetricsWidget.html"
            }
        ),
        Tool(
            name="siac.register_template",
            description="Use this when you need to register a validated template in the SIAC system and submit it to Meta for final approval. This action requires user confirmation.",
            inputSchema={
                "type": "object",
                "properties": {
                    "template_id": {
                        "type": "string",
                        "description": "UUID string identifier of the template to register"
                    },
                    "meta_template_id": {
                        "type": "string",
                        "description": "Meta template ID after upload to Meta system"
                    },
                    "client_id": {
                        "type": "string",
                        "description": "UUID string identifier of the client for traceability"
                    }
                },
                "required": ["template_id", "meta_template_id", "client_id"]
            },
            securitySchemes=["oauth2"],
            _meta={
                "openai/widgetAccessible": True,
                "openai/toolInvocation/invoking": "Registering template in SIAC and Meta systems...",
                "openai/toolInvocation/invoked": "Template registered and submitted for final Meta review.",
                "mcp/www_authenticate": f'Bearer realm="{auth_settings.resource_server_url}", scope="{auth_settings.required_scope}"'
            }
        ),
        Tool(
            name="siac.send_broadcast",
            description="Use this when you need to schedule and send a broadcast campaign to a specific customer segment using an approved template. This action requires user confirmation.",
            inputSchema={
                "type": "object",
                "properties": {
                    "template_id": {
                        "type": "string",
                        "description": "UUID string identifier of the approved template to send"
                    },
                    "segment_name": {
                        "type": "string",
                        "description": "Name of the customer segment to target (e.g., 'clientes_recurrentes')"
                    },
                    "schedule_time_utc": {
                        "type": "string",
                        "description": "Scheduled date and time for sending in UTC format (ISO 8601)"
                    }
                },
                "required": ["template_id", "segment_name", "schedule_time_utc"]
            },
            securitySchemes=["oauth2"],
            _meta={
                "openai/outputTemplate": "ui://widget/BroadcastConfirmationCard.html",
                "openai/toolInvocation/invoking": "Validating audience and scheduling broadcast...",
                "openai/toolInvocation/invoked": "Broadcast successfully scheduled.",
                "mcp/www_authenticate": f'Bearer realm="{auth_settings.resource_server_url}", scope="{auth_settings.required_scope}"'
            }
        )
    ]

@mcp_server.call_tool()
async def call_tool(name: str, arguments: Dict[str, Any], request: Request = None) -> List[TextContent]:
    """
    Call an MCP tool with authentication verification.
    
    This function implements the complete security flow:
    1. Identifies protected tools that require authentication
    2. Extracts and validates access tokens from request headers
    3. Returns 401 Unauthorized with WWW-Authenticate header for authentication failures
    4. Executes tools only after successful authentication
    
    Args:
        name: Name of the tool to call
        arguments: Arguments for the tool
        request: FastAPI Request object containing headers
        
    Returns:
        List of text content results
        
    Raises:
        JSONRPCError: If tool call fails or authentication is required
        HTTPException: If authentication fails (401 Unauthorized)
    """
    # Define protected tools that require authentication
    protected_tools = {
        "siac.register_template",
        "siac.send_broadcast"
    }
    
    # Check if this is a protected tool
    if name in protected_tools:
        try:
            # Extract authorization header
            auth_header = None
            if request and hasattr(request, 'headers'):
                auth_header = request.headers.get('Authorization')
            
            if not auth_header:
                logger.warning(f"Authentication required for protected tool '{name}' but no Authorization header provided")
                raise HTTPException(
                    status_code=status.HTTP_401_UNAUTHORIZED,
                    detail=f"Authentication required for tool '{name}'",
                    headers={"WWW-Authenticate": f'Bearer realm="{auth_settings.resource_server_url}", scope="{auth_settings.required_scope}"'}
                )
            
            # Extract token from Bearer format
            if not auth_header.startswith('Bearer '):
                logger.warning(f"Invalid authorization header format for tool '{name}': {auth_header}")
                raise HTTPException(
                    status_code=status.HTTP_401_UNAUTHORIZED,
                    detail="Invalid authorization header format",
                    headers={"WWW-Authenticate": f'Bearer realm="{auth_settings.resource_server_url}", scope="{auth_settings.required_scope}"'}
                )
            
            token = auth_header[7:]  # Remove "Bearer " prefix
            
            # Verify token using TokenVerifier
            try:
                token_claims = token_verifier.verify_token(token)
                logger.info(f"Authentication successful for tool '{name}' with user: {token_claims.get('sub', 'unknown')}")
            except HTTPException as auth_error:
                # Re-raise authentication errors with proper headers
                logger.warning(f"Authentication failed for tool '{name}': {auth_error.detail}")
                raise auth_error
            
        except HTTPException:
            # Re-raise HTTP exceptions (authentication failures)
            raise
        except Exception as e:
            logger.error(f"Unexpected error during authentication for tool '{name}': {str(e)}")
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Authentication verification failed",
                headers={"WWW-Authenticate": f'Bearer realm="{auth_settings.resource_server_url}", scope="{auth_settings.required_scope}"'}
            )
    
    # Execute the requested tool
    if name == "get_user_info":
        return [TextContent(
            type="text",
            text="User information retrieved successfully"
        )]
    elif name == "test_protected_action":
        action = arguments.get("action", "unknown")
        return [TextContent(
            type="text",
            text=f"Protected action '{action}' executed successfully"
        )]
    elif name == "siac.validate_template":
        return await handle_validate_template(arguments)
    elif name == "siac.get_campaign_metrics":
        return await handle_get_campaign_metrics(arguments)
    elif name == "siac.register_template":
        return await handle_register_template(arguments)
    elif name == "siac.send_broadcast":
        return await handle_send_broadcast(arguments)
    else:
        raise JSONRPCError(
            METHOD_NOT_FOUND,
            f"Unknown tool: {name}"
        )

# ============================================================================
# READ-ONLY TOOL HANDLERS
# ============================================================================

async def handle_validate_template(arguments: Dict[str, Any]) -> List[TextContent]:
    """
    Mock handler for siac.validate_template tool.
    
    This handler properly separates data between structuredContent (visible to model)
    and _meta (hidden from model, only for UI components).
    
    Args:
        arguments: Tool arguments containing template_name, body_text, category, language_code
        
    Returns:
        List of TextContent with structured validation results
    """
    template_name = arguments.get("template_name", "Unknown Template")
    body_text = arguments.get("body_text", "")
    category = arguments.get("category", "Marketing")
    language_code = arguments.get("language_code", "es_ES")
    
    # Mock validation logic with detailed error detection
    validation_status = "SUCCESS"
    passed_internal_checks = True
    detailed_errors = []
    
    # Simulate Meta validation rules
    if len(body_text) < 10:
        validation_status = "FAILED"
        passed_internal_checks = False
        detailed_errors.append({
            "field": "body_text",
            "message": "Template body too short for Meta requirements",
            "severity": "error",
            "suggestion": "Add more descriptive content to meet minimum length requirements"
        })
    elif "spam" in body_text.lower() or "urgent" in body_text.lower():
        validation_status = "FAILED"
        passed_internal_checks = False
        detailed_errors.append({
            "field": "body_text",
            "message": "Contains prohibited promotional language",
            "severity": "error",
            "suggestion": "Remove promotional keywords and use professional tone"
        })
    elif "{{" in body_text and "}}" not in body_text:
        validation_status = "FAILED"
        passed_internal_checks = False
        detailed_errors.append({
            "field": "body_text",
            "message": "Mismatched curly braces in template variables",
            "severity": "error",
            "suggestion": "Ensure all {{variable}} placeholders are properly closed"
        })
    elif body_text.startswith("{{") or body_text.endswith("}}"):
        validation_status = "FAILED"
        passed_internal_checks = False
        detailed_errors.append({
            "field": "body_text",
            "message": "Template cannot start or end with a parameter",
            "severity": "error",
            "suggestion": "Add descriptive text before the first parameter and after the last parameter"
        })
    elif category == "Marketing" and len(body_text) > 1000:
        validation_status = "SUCCESS"
        passed_internal_checks = True
        detailed_errors.append({
            "field": "body_text",
            "message": "Marketing template exceeds recommended length",
            "severity": "warning",
            "suggestion": "Consider shortening the message for better engagement"
        })
    
    # Generate client ID for tracking
    client_id = f"client_{hash(template_name) % 10000:04d}"
    
    # STRUCTURED CONTENT (Visible to Model) - Concise for reasoning
    structured_content = {
        "validation_status": validation_status,
        "template_name": template_name,
        "passed_internal_checks": passed_internal_checks,
        "category": category,
        "language_code": language_code,
        "client_id": client_id
    }
    
    # CONTENT (Visible to Model) - Conversational summary
    if validation_status == "SUCCESS":
        content_message = f"Template '{template_name}' validation completed successfully. The template passed all Meta compliance checks and is ready for registration."
    else:
        content_message = f"Template '{template_name}' validation failed. The template requires corrections before it can be submitted to Meta for approval."
    
    # _META (Hidden from Model) - Detailed data for TemplateValidationCard UI
    detailed_meta = {
        "raw_payload_for_preview": {
            "template_name": template_name,
            "body_text": body_text,
            "category": category,
            "language_code": language_code,
            "validation_rules_applied": [
                "Minimum length check",
                "Spam content detection", 
                "Variable syntax validation",
                "Parameter placement validation",
                "Category-specific length limits"
            ],
            "validation_timestamp": datetime.now(timezone.utc).isoformat(),
            "estimated_review_time": "24-48 hours"
        },
        "template_html_mockup": f"""
        <div class="whatsapp-template-preview">
            <div class="template-header">
                <span class="template-name">{template_name}</span>
                <span class="category-badge">{category}</span>
            </div>
            <div class="template-body">
                {body_text.replace('{{1}}', '<span class="variable">John</span>').replace('{{2}}', '<span class="variable">Premium</span>')}
            </div>
            <div class="template-footer">
                <span class="language-badge">{language_code}</span>
            </div>
        </div>
        """,
        "raw_validation_errors": {
            "errors": detailed_errors,
            "overall_status": validation_status
        }
    }
    
    return [TextContent(
        type="text",
        text=f"{content_message}\n\nStructured Data: {structured_content}\n\nMeta Data: {detailed_meta}"
    )]

async def handle_get_campaign_metrics(arguments: Dict[str, Any]) -> List[TextContent]:
    """
    Mock handler for siac.get_campaign_metrics tool.
    
    This handler properly separates data between structuredContent (visible to model)
    and _meta (hidden from model, only for CampaignMetricsWidget UI).
    
    Args:
        arguments: Tool arguments containing campaign_id
        
    Returns:
        List of TextContent with structured campaign metrics
    """
    campaign_id = arguments.get("campaign_id", "unknown")
    
    # Mock campaign metrics with realistic scenarios
    delivery_rate = 0.95
    status = "COMPLETED"
    quality_score = "GREEN"
    template_pacing_active = False
    meta_errors = []
    
    # Simulate different scenarios based on campaign_id
    if "test" in campaign_id.lower():
        delivery_rate = 0.87
        status = "RUNNING"
        quality_score = "YELLOW"
        template_pacing_active = True
    elif "demo" in campaign_id.lower():
        delivery_rate = 0.99
        status = "COMPLETED"
        quality_score = "GREEN"
    elif "error" in campaign_id.lower():
        delivery_rate = 0.45
        status = "FAILED"
        quality_score = "RED"
        meta_errors = [
            {
                "error_code": 131049,
                "error_message": "Marketing message limit per user exceeded",
                "count": 150
            },
            {
                "error_code": 131026,
                "error_message": "Message failed to send",
                "count": 125
            }
        ]
    elif "pacing" in campaign_id.lower():
        delivery_rate = 0.92
        status = "RUNNING"
        quality_score = "YELLOW"
        template_pacing_active = True
    
    # Calculate derived metrics
    total_sent = 1250
    delivered = int(total_sent * delivery_rate)
    failed = total_sent - delivered
    
    # STRUCTURED CONTENT (Visible to Model) - High-level metrics for reasoning
    structured_content = {
        "campaign_id": campaign_id,
        "delivery_rate": delivery_rate,
        "status": status,
        "quality_score": quality_score,
        "total_sent": total_sent,
        "delivered": delivered,
        "failed": failed
    }
    
    # CONTENT (Visible to Model) - Conversational summary
    content_message = f"Campaign {campaign_id} metrics retrieved. Status: {status}, Delivery Rate: {delivery_rate:.1%}, Quality Score: {quality_score}."
    
    if status == "COMPLETED":
        content_message += " The campaign has finished successfully with excellent performance."
    elif status == "RUNNING":
        content_message += " The campaign is currently active and performing well."
    elif status == "FAILED":
        content_message += " The campaign encountered issues and may need attention."
    
    # _META (Hidden from Model) - Detailed data for CampaignMetricsWidget UI
    detailed_meta = {
        "campaign_id": campaign_id,
        "delivery_rate": delivery_rate,
        "status": status,
        "quality_score": quality_score,
        "total_sent": total_sent,
        "delivered": delivered,
        "failed": failed,
        "performance_metrics": {
            "delivery_rate": delivery_rate,
            "open_rate": 0.23 if quality_score == "GREEN" else 0.15 if quality_score == "YELLOW" else 0.08,
            "click_rate": 0.05 if quality_score == "GREEN" else 0.03 if quality_score == "YELLOW" else 0.01,
            "response_rate": 0.02 if quality_score == "GREEN" else 0.015 if quality_score == "YELLOW" else 0.005
        },
        "quality_metrics": {
            "quality_score": quality_score,
            "spam_score": 0.01 if quality_score == "GREEN" else 0.06 if quality_score == "YELLOW" else 0.15,
            "engagement_score": 0.15 if quality_score == "GREEN" else 0.12 if quality_score == "YELLOW" else 0.03
        },
        "timeline": {
            "started_at": "2024-01-20T10:00:00Z",
            "completed_at": "2024-01-20T18:30:00Z" if status == "COMPLETED" else None,
            "duration_hours": 8.5 if status == "COMPLETED" else None
        },
        "cost_analysis": {
            "total_cost": round(total_sent * 0.015, 2),
            "cost_per_message": 0.015,
            "cost_per_delivery": round(0.015 / delivery_rate, 4) if delivery_rate > 0 else 0.015
        },
        "pacing_status": {
            "template_pacing_active": template_pacing_active,
            "held_messages": 45 if template_pacing_active else 0,
            "pacing_reason": "Evaluación de calidad por Meta" if template_pacing_active else None
        },
        "meta_errors": meta_errors
    }
    
    return [TextContent(
        type="text",
        text=f"{content_message}\n\nStructured Data: {structured_content}\n\nMeta Data: {detailed_meta}"
    )]

# ============================================================================
# WRITE ACTION TOOL HANDLERS
# ============================================================================

async def handle_register_template(arguments: Dict[str, Any]) -> List[TextContent]:
    """
    Mock handler for siac.register_template tool.
    
    This handler simulates the registration of a validated template in SIAC
    and submission to Meta for final approval.
    
    Args:
        arguments: Tool arguments containing template_id, meta_template_id, client_id
        
    Returns:
        List of TextContent with structured registration results
    """
    template_id = arguments.get("template_id", "unknown")
    meta_template_id = arguments.get("meta_template_id", "unknown")
    client_id = arguments.get("client_id", "unknown")
    
    # Mock registration process
    registration_status = "REGISTRATION_COMPLETE"
    
    # Simulate different scenarios based on template_id
    if "invalid" in template_id.lower():
        registration_status = "REGISTRATION_FAILED"
    elif "pending" in template_id.lower():
        registration_status = "PENDING_META_REVIEW"
    
    # Structured content for model reasoning
    structured_content = {
        "status": registration_status,
        "template_id": template_id,
        "meta_template_id": meta_template_id,
        "client_id": client_id,
        "registration_timestamp": datetime.now(timezone.utc).isoformat(),
        "meta_review_status": "SUBMITTED" if registration_status == "REGISTRATION_COMPLETE" else "FAILED"
    }
    
    # Conversational summary
    if registration_status == "REGISTRATION_COMPLETE":
        content_message = f"Template {template_id} has been successfully registered in SIAC and submitted to Meta for final review. Meta Template ID: {meta_template_id}"
    elif registration_status == "PENDING_META_REVIEW":
        content_message = f"Template {template_id} registration is in progress. Meta review is pending."
    else:
        content_message = f"Template {template_id} registration failed. Please check the template data and try again."
    
    # Detailed metadata for audit trail
    detailed_meta = {
        "registration_details": {
            "template_id": template_id,
            "meta_template_id": meta_template_id,
            "client_id": client_id,
            "registration_method": "API",
            "submitted_by": "system",
            "estimated_meta_review_time": "24-72 hours"
        },
        "next_steps": [
            "Monitor Meta review status",
            "Update template status in SIAC",
            "Notify stakeholders of submission"
        ],
        "audit_trail": {
            "created_at": datetime.now(timezone.utc).isoformat(),
            "action": "template_registration",
            "client_id": client_id
        }
    }
    
    return [TextContent(
        type="text",
        text=f"{content_message}\n\nStructured Data: {structured_content}\n\nRegistration Details: {detailed_meta}"
    )]

async def handle_send_broadcast(arguments: Dict[str, Any]) -> List[TextContent]:
    """
    Mock handler for siac.send_broadcast tool.
    
    This handler simulates the scheduling and sending of a broadcast campaign
    to a specific customer segment.
    
    Args:
        arguments: Tool arguments containing template_id, segment_name, schedule_time_utc
        
    Returns:
        List of TextContent with structured broadcast confirmation
    """
    template_id = arguments.get("template_id", "unknown")
    segment_name = arguments.get("segment_name", "unknown")
    schedule_time_utc = arguments.get("schedule_time_utc", "unknown")
    
    # Generate campaign ID for traceability
    campaign_id = f"campaign_{template_id}_{int(datetime.now(timezone.utc).timestamp())}"
    
    # Mock broadcast scheduling
    broadcast_status = "SCHEDULED"
    estimated_recipients = 1000
    
    # Simulate different scenarios based on segment_name
    if "test" in segment_name.lower():
        estimated_recipients = 50
        broadcast_status = "SCHEDULED_TEST"
    elif "premium" in segment_name.lower():
        estimated_recipients = 5000
    elif "invalid" in segment_name.lower():
        broadcast_status = "SCHEDULING_FAILED"
        estimated_recipients = 0
    
    # Structured content for model reasoning
    structured_content = {
        "campaign_id": campaign_id,
        "template_id": template_id,
        "segment_name": segment_name,
        "schedule_time_utc": schedule_time_utc,
        "status": broadcast_status,
        "estimated_recipients": estimated_recipients,
        "scheduled_at": datetime.now(timezone.utc).isoformat()
    }
    
    # Conversational summary
    if broadcast_status == "SCHEDULED":
        content_message = f"Broadcast campaign {campaign_id} has been successfully scheduled for {schedule_time_utc}. Target segment: {segment_name}, Estimated recipients: {estimated_recipients}"
    elif broadcast_status == "SCHEDULED_TEST":
        content_message = f"Test broadcast campaign {campaign_id} scheduled for {schedule_time_utc}. This is a test segment with {estimated_recipients} recipients."
    else:
        content_message = f"Broadcast scheduling failed for template {template_id}. Please verify the segment name and schedule time."
    
    # Detailed metadata for UI widget
    detailed_meta = {
        "campaign_details": {
            "campaign_id": campaign_id,
            "template_id": template_id,
            "segment_name": segment_name,
            "schedule_time_utc": schedule_time_utc,
            "estimated_recipients": estimated_recipients,
            "status": broadcast_status
        },
        "segment_analysis": {
            "segment_name": segment_name,
            "total_customers": estimated_recipients,
            "delivery_estimate": f"{estimated_recipients * 0.95:.0f}",
            "cost_estimate": f"{estimated_recipients * 0.015:.2f}",
            "expected_completion": "2-4 hours"
        },
        "scheduling_info": {
            "scheduled_at": datetime.now(timezone.utc).isoformat(),
            "schedule_time_utc": schedule_time_utc,
            "timezone": "UTC",
            "status": broadcast_status
        },
        "monitoring": {
            "tracking_enabled": True,
            "metrics_available": True,
            "real_time_updates": True
        }
    }
    
    return [TextContent(
        type="text",
        text=f"{content_message}\n\nStructured Data: {structured_content}\n\nCampaign Details: {detailed_meta}"
    )]

# ============================================================================
# ERROR HANDLING
# ============================================================================

@app.exception_handler(HTTPException)
async def http_exception_handler(request: Request, exc: HTTPException):
    """
    Custom HTTP exception handler for authentication failures.
    
    Args:
        request: The HTTP request
        exc: The HTTP exception
        
    Returns:
        JSONResponse with proper authentication headers
    """
    if exc.status_code == status.HTTP_401_UNAUTHORIZED:
        return JSONResponse(
            status_code=exc.status_code,
            content={"detail": exc.detail},
            headers=exc.headers
        )
    return JSONResponse(
        status_code=exc.status_code,
        content={"detail": exc.detail}
    )

# ============================================================================
# SERVER STARTUP
# ============================================================================

@app.on_event("startup")
async def startup_event():
    """
    Application startup event handler.
    """
    logger.info("Starting SIAC Assistant FastMCP Server")
    logger.info(f"OAuth 2.1 Issuer: {auth_settings.issuer_url}")
    logger.info(f"Resource Server: {auth_settings.resource_server_url}")
    logger.info(f"Required Scope: {auth_settings.required_scope}")
    logger.info("Server startup completed")

@app.on_event("shutdown")
async def shutdown_event():
    """
    Application shutdown event handler.
    """
    logger.info("Shutting down SIAC Assistant FastMCP Server")

if __name__ == "__main__":
    uvicorn.run(
        app,
        host="0.0.0.0",
        port=8000,
        log_level="info"
    )