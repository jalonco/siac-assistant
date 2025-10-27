#!/bin/bash
# SIAC Assistant - Verificación del Servidor MCP
# Script para verificar que el servidor MCP está funcionando correctamente

echo "🔍 SIAC Assistant - Verificación del Servidor MCP"
echo "=================================================="

# Colores para output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Función para mostrar estado
show_status() {
    if [ $1 -eq 0 ]; then
        echo -e "${GREEN}✅ $2${NC}"
    else
        echo -e "${RED}❌ $2${NC}"
    fi
}

# Función para mostrar advertencia
show_warning() {
    echo -e "${YELLOW}⚠️  $1${NC}"
}

# Función para mostrar información
show_info() {
    echo -e "${BLUE}ℹ️  $1${NC}"
}

echo ""
echo "1. Verificando procesos del servidor..."
echo "----------------------------------------"

# Verificar si uvicorn está ejecutándose
if pgrep -f "uvicorn.*main:app" > /dev/null; then
    show_status 0 "Servidor uvicorn ejecutándose"
    echo "   Proceso: $(pgrep -f 'uvicorn.*main:app')"
else
    show_status 1 "Servidor uvicorn no encontrado"
fi

echo ""
echo "2. Verificando puerto 8888..."
echo "-----------------------------"

# Verificar si el puerto está en uso
if lsof -i :8888 > /dev/null 2>&1; then
    show_status 0 "Puerto 8888 está en uso"
    echo "   Detalles:"
    lsof -i :8888 | grep LISTEN
else
    show_status 1 "Puerto 8888 no está en uso"
fi

echo ""
echo "3. Verificando conectividad HTTP..."
echo "----------------------------------"

# Verificar endpoint de salud
if curl -s http://localhost:8888/health > /dev/null 2>&1; then
    show_status 0 "Endpoint /health responde"
    echo "   Respuesta:"
    curl -s http://localhost:8888/health | head -3
else
    show_status 1 "Endpoint /health no responde"
fi

echo ""
echo "4. Verificando endpoints MCP..."
echo "-------------------------------"

# Verificar endpoint raíz
if curl -s http://localhost:8888/ > /dev/null 2>&1; then
    show_status 0 "Endpoint raíz (/) responde"
else
    show_status 1 "Endpoint raíz (/) no responde"
fi

# Verificar información de autenticación
if curl -s http://localhost:8888/auth/info > /dev/null 2>&1; then
    show_status 0 "Endpoint /auth/info responde"
else
    show_status 1 "Endpoint /auth/info no responde"
fi

echo ""
echo "5. Verificando documentación OpenAPI..."
echo "--------------------------------------"

# Verificar Swagger UI
if curl -s http://localhost:8888/docs > /dev/null 2>&1; then
    show_status 0 "Swagger UI disponible"
    echo "   URL: http://localhost:8888/docs"
else
    show_status 1 "Swagger UI no disponible"
fi

# Verificar ReDoc
if curl -s http://localhost:8888/redoc > /dev/null 2>&1; then
    show_status 0 "ReDoc disponible"
    echo "   URL: http://localhost:8888/redoc"
else
    show_status 1 "ReDoc no disponible"
fi

# Verificar OpenAPI spec
if curl -s http://localhost:8888/openapi.json > /dev/null 2>&1; then
    show_status 0 "OpenAPI specification disponible"
    echo "   URL: http://localhost:8888/openapi.json"
else
    show_status 1 "OpenAPI specification no disponible"
fi

echo ""
echo "6. Verificando herramientas MCP..."
echo "---------------------------------"

# Verificar que el servidor responde a requests MCP
MCP_RESPONSE=$(curl -s -X POST http://localhost:8888/mcp \
    -H "Content-Type: application/json" \
    -d '{"jsonrpc": "2.0", "id": 1, "method": "tools/list", "params": {}}' 2>/dev/null)

if echo "$MCP_RESPONSE" | grep -q "jsonrpc"; then
    show_status 0 "Endpoint MCP responde correctamente"
    echo "   Herramientas registradas:"
    echo "$MCP_RESPONSE" | grep -o '"name":"[^"]*"' | sed 's/"name":"//g' | sed 's/"//g' | head -5
else
    show_status 1 "Endpoint MCP no responde correctamente"
fi

echo ""
echo "7. Verificando base de datos..."
echo "------------------------------"

# Verificar conexión a PostgreSQL
if pgrep -f "postgres" > /dev/null; then
    show_status 0 "PostgreSQL ejecutándose"
else
    show_warning "PostgreSQL no encontrado (puede estar en Docker)"
fi

# Verificar si Docker está ejecutándose
if docker ps > /dev/null 2>&1; then
    show_status 0 "Docker disponible"
    if docker ps | grep -q "siac"; then
        show_status 0 "Contenedor SIAC ejecutándose"
    else
        show_warning "Contenedor SIAC no encontrado"
    fi
else
    show_warning "Docker no disponible o no ejecutándose"
fi

echo ""
echo "8. Resumen de URLs disponibles..."
echo "--------------------------------"

show_info "URLs del servidor SIAC Assistant:"
echo "   🏠 Servidor principal: http://localhost:8888"
echo "   ❤️  Health check: http://localhost:8888/health"
echo "   🔐 Auth info: http://localhost:8888/auth/info"
echo "   📚 Swagger UI: http://localhost:8888/docs"
echo "   📖 ReDoc: http://localhost:8888/redoc"
echo "   📋 OpenAPI Spec: http://localhost:8888/openapi.json"
echo "   🔧 MCP Endpoint: http://localhost:8888/mcp"

echo ""
echo "9. Comandos útiles..."
echo "--------------------"

show_info "Para iniciar el servidor si no está ejecutándose:"
echo "   cd server && ./start.sh"

show_info "Para ver logs del servidor:"
echo "   tail -f server/logs/server.log"

show_info "Para probar herramientas MCP:"
echo "   python test_mcp_server.py"

show_info "Para verificar autenticación:"
echo "   python server/test_auth.py"

echo ""
echo "✅ Verificación completada"
echo "=========================="



