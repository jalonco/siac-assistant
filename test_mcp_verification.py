#!/usr/bin/env python3
"""
SIAC Assistant - Verificación del Servidor MCP
Script para probar todas las funcionalidades del servidor MCP
"""

import asyncio
import json
import sys
import os
from pathlib import Path
import httpx
from datetime import datetime

# Agregar el directorio server al path
server_path = str(Path(__file__).parent / "server")
sys.path.insert(0, server_path)

def print_header(title):
    """Imprimir encabezado con formato"""
    print(f"\n{'='*60}")
    print(f"🔍 {title}")
    print(f"{'='*60}")

def print_success(message):
    """Imprimir mensaje de éxito"""
    print(f"✅ {message}")

def print_error(message):
    """Imprimir mensaje de error"""
    print(f"❌ {message}")

def print_warning(message):
    """Imprimir mensaje de advertencia"""
    print(f"⚠️  {message}")

def print_info(message):
    """Imprimir mensaje informativo"""
    print(f"ℹ️  {message}")

async def test_server_connectivity():
    """Probar conectividad básica del servidor"""
    print_header("VERIFICACIÓN DE CONECTIVIDAD")
    
    base_url = "http://localhost:8888"
    
    async with httpx.AsyncClient(timeout=10.0) as client:
        # Test 1: Health check
        try:
            response = await client.get(f"{base_url}/health")
            if response.status_code == 200:
                print_success("Health check responde correctamente")
                print(f"   Respuesta: {response.json()}")
            else:
                print_error(f"Health check falló con código {response.status_code}")
        except Exception as e:
            print_error(f"Health check no responde: {e}")
            return False
        
        # Test 2: Root endpoint
        try:
            response = await client.get(f"{base_url}/")
            if response.status_code == 200:
                print_success("Endpoint raíz responde correctamente")
            else:
                print_error(f"Endpoint raíz falló con código {response.status_code}")
        except Exception as e:
            print_error(f"Endpoint raíz no responde: {e}")
        
        # Test 3: Auth info
        try:
            response = await client.get(f"{base_url}/auth/info")
            if response.status_code == 200:
                print_success("Endpoint de información de autenticación responde")
                auth_info = response.json()
                print(f"   OAuth issuer: {auth_info.get('issuer_url', 'N/A')}")
                print(f"   Resource server: {auth_info.get('resource_server_url', 'N/A')}")
            else:
                print_error(f"Endpoint de auth info falló con código {response.status_code}")
        except Exception as e:
            print_error(f"Endpoint de auth info no responde: {e}")
        
        # Test 4: OpenAPI spec
        try:
            response = await client.get(f"{base_url}/openapi.json")
            if response.status_code == 200:
                print_success("Especificación OpenAPI disponible")
                spec = response.json()
                print(f"   Título: {spec.get('info', {}).get('title', 'N/A')}")
                print(f"   Versión: {spec.get('info', {}).get('version', 'N/A')}")
                paths = list(spec.get('paths', {}).keys())
                print(f"   Endpoints disponibles: {len(paths)}")
            else:
                print_error(f"OpenAPI spec falló con código {response.status_code}")
        except Exception as e:
            print_error(f"OpenAPI spec no responde: {e}")
        
        return True

async def test_mcp_tools():
    """Probar herramientas MCP"""
    print_header("VERIFICACIÓN DE HERRAMIENTAS MCP")
    
    base_url = "http://localhost:8888"
    
    async with httpx.AsyncClient(timeout=10.0) as client:
        # Test 1: Listar herramientas
        try:
            mcp_request = {
                "jsonrpc": "2.0",
                "id": 1,
                "method": "tools/list",
                "params": {}
            }
            
            response = await client.post(
                f"{base_url}/mcp",
                json=mcp_request,
                headers={"Content-Type": "application/json"}
            )
            
            if response.status_code == 200:
                print_success("Endpoint MCP responde correctamente")
                mcp_response = response.json()
                
                if "result" in mcp_response and "tools" in mcp_response["result"]:
                    tools = mcp_response["result"]["tools"]
                    print(f"   Herramientas registradas: {len(tools)}")
                    
                    for tool in tools:
                        name = tool.get("name", "N/A")
                        description = tool.get("description", "Sin descripción")
                        print(f"   📋 {name}: {description[:50]}...")
                else:
                    print_warning("No se encontraron herramientas en la respuesta MCP")
                    print(f"   Respuesta: {mcp_response}")
            else:
                print_error(f"Endpoint MCP falló con código {response.status_code}")
                print(f"   Respuesta: {response.text}")
        except Exception as e:
            print_error(f"Endpoint MCP no responde: {e}")

async def test_readonly_tools():
    """Probar herramientas de solo lectura"""
    print_header("VERIFICACIÓN DE HERRAMIENTAS DE SOLO LECTURA")
    
    base_url = "http://localhost:8888"
    
    async with httpx.AsyncClient(timeout=10.0) as client:
        # Test 1: siac.validate_template
        try:
            mcp_request = {
                "jsonrpc": "2.0",
                "id": 2,
                "method": "tools/call",
                "params": {
                    "name": "siac.validate_template",
                    "arguments": {
                        "template_content": "Hola {{1}}, tu pedido {{2}} está listo para recoger.",
                        "template_name": "Pedido Listo",
                        "category": "UTILITY",
                        "language_code": "es"
                    }
                }
            }
            
            response = await client.post(
                f"{base_url}/mcp",
                json=mcp_request,
                headers={"Content-Type": "application/json"}
            )
            
            if response.status_code == 200:
                print_success("siac.validate_template responde correctamente")
                mcp_response = response.json()
                if "result" in mcp_response:
                    result = mcp_response["result"]
                    print(f"   Estado de validación: {result.get('content', {}).get('validation_status', 'N/A')}")
            else:
                print_error(f"siac.validate_template falló con código {response.status_code}")
        except Exception as e:
            print_error(f"siac.validate_template no responde: {e}")
        
        # Test 2: siac.get_campaign_metrics
        try:
            mcp_request = {
                "jsonrpc": "2.0",
                "id": 3,
                "method": "tools/call",
                "params": {
                    "name": "siac.get_campaign_metrics",
                    "arguments": {
                        "campaign_id": "test-campaign-123"
                    }
                }
            }
            
            response = await client.post(
                f"{base_url}/mcp",
                json=mcp_request,
                headers={"Content-Type": "application/json"}
            )
            
            if response.status_code == 200:
                print_success("siac.get_campaign_metrics responde correctamente")
                mcp_response = response.json()
                if "result" in mcp_response:
                    result = mcp_response["result"]
                    print(f"   ID de campaña: {result.get('content', {}).get('campaign_id', 'N/A')}")
            else:
                print_error(f"siac.get_campaign_metrics falló con código {response.status_code}")
        except Exception as e:
            print_error(f"siac.get_campaign_metrics no responde: {e}")

async def test_protected_tools():
    """Probar herramientas protegidas (requieren autenticación)"""
    print_header("VERIFICACIÓN DE HERRAMIENTAS PROTEGIDAS")
    
    base_url = "http://localhost:8888"
    
    async with httpx.AsyncClient(timeout=10.0) as client:
        # Test 1: siac.register_template (sin token - debe fallar)
        try:
            mcp_request = {
                "jsonrpc": "2.0",
                "id": 4,
                "method": "tools/call",
                "params": {
                    "name": "siac.register_template",
                    "arguments": {
                        "template_id": "test-template-123",
                        "meta_template_id": "meta-123",
                        "client_id": "test-client-123"
                    }
                }
            }
            
            response = await client.post(
                f"{base_url}/mcp",
                json=mcp_request,
                headers={"Content-Type": "application/json"}
            )
            
            if response.status_code == 401:
                print_success("siac.register_template correctamente protegida (401 Unauthorized)")
            else:
                print_warning(f"siac.register_template no está protegida (código {response.status_code})")
        except Exception as e:
            print_error(f"Error probando siac.register_template: {e}")
        
        # Test 2: siac.send_broadcast (sin token - debe fallar)
        try:
            mcp_request = {
                "jsonrpc": "2.0",
                "id": 5,
                "method": "tools/call",
                "params": {
                    "name": "siac.send_broadcast",
                    "arguments": {
                        "template_id": "test-template-123",
                        "client_segment": "test-segment",
                        "scheduled_time": "2024-01-01T10:00:00Z"
                    }
                }
            }
            
            response = await client.post(
                f"{base_url}/mcp",
                json=mcp_request,
                headers={"Content-Type": "application/json"}
            )
            
            if response.status_code == 401:
                print_success("siac.send_broadcast correctamente protegida (401 Unauthorized)")
            else:
                print_warning(f"siac.send_broadcast no está protegida (código {response.status_code})")
        except Exception as e:
            print_error(f"Error probando siac.send_broadcast: {e}")

def print_summary():
    """Imprimir resumen de URLs disponibles"""
    print_header("RESUMEN DE URLs DISPONIBLES")
    
    urls = [
        ("🏠 Servidor principal", "http://localhost:8888"),
        ("❤️ Health check", "http://localhost:8888/health"),
        ("🔐 Auth info", "http://localhost:8888/auth/info"),
        ("📚 Swagger UI", "http://localhost:8888/docs"),
        ("📖 ReDoc", "http://localhost:8888/redoc"),
        ("📋 OpenAPI Spec", "http://localhost:8888/openapi.json"),
        ("🔧 MCP Endpoint", "http://localhost:8888/mcp")
    ]
    
    for name, url in urls:
        print(f"   {name}: {url}")
    
    print("\n📋 Comandos útiles:")
    print("   • Iniciar servidor: cd server && ./start.sh")
    print("   • Ver logs: tail -f server/logs/server.log")
    print("   • Probar autenticación: python server/test_auth.py")
    print("   • Probar herramientas: python server/test_readonly_tools.py")

async def main():
    """Función principal"""
    print("🚀 SIAC Assistant - Verificación Completa del Servidor MCP")
    print(f"⏰ Iniciado: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    
    # Ejecutar todas las pruebas
    server_ok = await test_server_connectivity()
    
    if server_ok:
        await test_mcp_tools()
        await test_readonly_tools()
        await test_protected_tools()
    else:
        print_error("Servidor no disponible - saltando pruebas MCP")
    
    print_summary()
    
    print(f"\n✅ Verificación completada: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")

if __name__ == "__main__":
    asyncio.run(main())



