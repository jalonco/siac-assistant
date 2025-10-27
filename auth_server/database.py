"""
SIAC Assistant - Database Models for User Authentication
"""

from typing import Dict, Optional
import uuid
from datetime import datetime, timedelta

# Simulación de base de datos en memoria (para desarrollo)
# En producción, esto debería ser PostgreSQL/MySQL

class UserDatabase:
    """
    Simulación de base de datos de usuarios.
    En producción, reemplazar con SQLAlchemy + PostgreSQL.
    """
    
    def __init__(self):
        # Usuarios simulados con estructura:
        # {user_id: {email, password_hash, client_id, client_name, roles}}
        self.users: Dict[str, Dict] = {
            "user_001": {
                "email": "admin@siac.com",
                "password": "admin123",  # En producción: bcrypt hash
                "client_id": "cliente_siac_principal",
                "client_name": "SIAC Principal",
                "name": "Administrador SIAC",
                "roles": ["admin", "user"],
                "permissions": ["read", "write", "delete"],
                "active": True,
                "created_at": "2024-01-01T00:00:00Z"
            },
            "user_002": {
                "email": "usuario@cliente1.com",
                "password": "demo123",  # En producción: bcrypt hash
                "client_id": "cliente_001",
                "client_name": "Cliente Demo 1",
                "name": "Usuario Demo 1",
                "roles": ["user"],
                "permissions": ["read"],
                "active": True,
                "created_at": "2024-01-15T00:00:00Z"
            },
            "user_003": {
                "email": "manager@cliente2.com",
                "password": "manager123",  # En producción: bcrypt hash
                "client_id": "cliente_002",
                "client_name": "Cliente Demo 2",
                "name": "Manager Demo 2",
                "roles": ["manager", "user"],
                "permissions": ["read", "write"],
                "active": True,
                "created_at": "2024-02-01T00:00:00Z"
            }
        }
        
        # Authorization codes pendientes
        # {code: {user_id, client_id, redirect_uri, scope, expires_at}}
        self.authorization_codes: Dict[str, Dict] = {}
        
        # Tokens activos
        # {token: {user_id, client_id, scope, expires_at}}
        self.active_tokens: Dict[str, Dict] = {}
    
    def authenticate_user(self, email: str, password: str) -> Optional[Dict]:
        """
        Autentica un usuario por email y contraseña.
        
        Args:
            email: Email del usuario
            password: Contraseña del usuario
            
        Returns:
            Diccionario con información del usuario si es válido, None si no
        """
        # Buscar usuario por email
        for user_id, user_data in self.users.items():
            if user_data["email"] == email and user_data["password"] == password:
                if user_data["active"]:
                    return {
                        "user_id": user_id,
                        **user_data
                    }
                else:
                    return None  # Usuario inactivo
        
        return None  # Credenciales inválidas
    
    def get_user_by_id(self, user_id: str) -> Optional[Dict]:
        """Obtiene un usuario por su ID."""
        user_data = self.users.get(user_id)
        if user_data:
            return {
                "user_id": user_id,
                **user_data
            }
        return None
    
    def store_authorization_code(
        self, 
        code: str, 
        user_id: str, 
        client_id: str, 
        redirect_uri: str, 
        scope: str,
        code_challenge: Optional[str] = None
    ):
        """Almacena un código de autorización asociado a un usuario."""
        self.authorization_codes[code] = {
            "user_id": user_id,
            "client_id": client_id,
            "redirect_uri": redirect_uri,
            "scope": scope,
            "code_challenge": code_challenge,
            "created_at": datetime.utcnow().isoformat(),
            "expires_at": (datetime.utcnow() + timedelta(minutes=10)).isoformat()
        }
    
    def get_authorization_code(self, code: str) -> Optional[Dict]:
        """Obtiene y elimina un código de autorización (uso único)."""
        code_data = self.authorization_codes.pop(code, None)
        if code_data:
            # Verificar expiración
            expires_at = datetime.fromisoformat(code_data["expires_at"])
            if datetime.utcnow() > expires_at:
                return None  # Código expirado
        return code_data
    
    def store_token(self, token: str, user_id: str, client_id: str, scope: str):
        """Almacena un token activo asociado a un usuario."""
        self.active_tokens[token] = {
            "user_id": user_id,
            "client_id": client_id,
            "scope": scope,
            "created_at": datetime.utcnow().isoformat(),
            "expires_at": (datetime.utcnow() + timedelta(hours=24)).isoformat()
        }
    
    def get_token_info(self, token: str) -> Optional[Dict]:
        """Obtiene información de un token activo."""
        token_data = self.active_tokens.get(token)
        if token_data:
            # Verificar expiración
            expires_at = datetime.fromisoformat(token_data["expires_at"])
            if datetime.utcnow() > expires_at:
                # Token expirado, eliminarlo
                self.active_tokens.pop(token, None)
                return None
            
            # Agregar información del usuario
            user_info = self.get_user_by_id(token_data["user_id"])
            if user_info:
                return {
                    **token_data,
                    "user": user_info
                }
        return None
    
    def revoke_token(self, token: str):
        """Revoca un token activo."""
        self.active_tokens.pop(token, None)


# Instancia global de la base de datos
user_db = UserDatabase()

