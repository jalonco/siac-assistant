#!/bin/bash
# SIAC Assistant - Script de Verificación Completa (con Auth Server)
# Verificación completa del despliegue con OAuth 2.1

set -e

# Configuración
VPS_HOST="srv790515.hstgr.cloud"
SSH_KEY="~/.ssh/id_ed25519"
SSH_CMD="ssh -i $SSH_KEY root@$VPS_HOST"
PROJECT_NAME="siac-assistant"
DEPLOY_DIR="/opt/$PROJECT_NAME"
API_URL="https://api.siac-app.com"
AUTH_URL="https://auth.siac-app.com"

# Colores
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m'

echo -e "${BLUE}🔍 SIAC Assistant - Verificación Completa con OAuth 2.1${NC}"
echo -e "${BLUE}====================================================${NC}"
echo "Servidor: $VPS_HOST"
echo "API URL: $API_URL"
echo "Auth URL: $AUTH_URL"
echo ""

# Función para verificar endpoint
verify_endpoint() {
    local endpoint=$1
    local description=$2
    local url=$3
    
    echo -e "${BLUE}Verificando $description...${NC}"
    
    if curl -s -f "$url$endpoint" > /dev/null 2>&1; then
        echo -e "${GREEN}✅ $description: OK${NC}"
        return 0
    else
        echo -e "${RED}❌ $description: FALLO${NC}"
        return 1
    fi
}

# Función para verificar contenedores
verify_containers() {
    echo -e "${BLUE}🐳 Verificando contenedores Docker...${NC}"
    
    local containers=$($SSH_CMD "docker ps | grep siac | wc -l")
    
    if [ "$containers" -ge 3 ]; then
        echo -e "${GREEN}✅ Contenedores activos: $containers${NC}"
        $SSH_CMD "docker ps | grep siac"
    else
        echo -e "${RED}❌ Contenedores insuficientes: $containers (esperado: 3+)${NC}"
        return 1
    fi
}

# Función para verificar logs
verify_logs() {
    echo -e "${BLUE}📋 Verificando logs de los servicios...${NC}"
    
    echo "Logs del SIAC Assistant:"
    $SSH_CMD "docker logs siac-assistant --tail 10"
    
    echo ""
    echo "Logs del Auth Server:"
    $SSH_CMD "docker logs siac-auth-server --tail 10"
    
    # Verificar si hay errores críticos
    local siac_errors=$($SSH_CMD "docker logs siac-assistant 2>&1 | grep -i 'error\\|exception\\|failed' | wc -l")
    local auth_errors=$($SSH_CMD "docker logs siac-auth-server 2>&1 | grep -i 'error\\|exception\\|failed' | wc -l")
    
    if [ "$siac_errors" -gt 0 ] || [ "$auth_errors" -gt 0 ]; then
        echo -e "${YELLOW}⚠️  Se encontraron errores en los logs${NC}"
        echo "SIAC Assistant: $siac_errors errores"
        echo "Auth Server: $auth_errors errores"
    else
        echo -e "${GREEN}✅ No se encontraron errores críticos${NC}"
    fi
}

# Función para verificar SSL
verify_ssl() {
    echo -e "${BLUE}🔒 Verificando certificados SSL...${NC}"
    
    echo "Verificando SSL de SIAC Assistant:"
    local siac_ssl=$(curl -s -I "$API_URL" 2>/dev/null | grep -i "server\\|date\\|content-type" | head -3)
    
    if [ -n "$siac_ssl" ]; then
        echo -e "${GREEN}✅ SSL SIAC Assistant configurado${NC}"
        echo "$siac_ssl"
    else
        echo -e "${YELLOW}⚠️  SSL SIAC Assistant aún configurándose${NC}"
    fi
    
    echo ""
    echo "Verificando SSL de Auth Server:"
    local auth_ssl=$(curl -s -I "$AUTH_URL" 2>/dev/null | grep -i "server\\|date\\|content-type" | head -3)
    
    if [ -n "$auth_ssl" ]; then
        echo -e "${GREEN}✅ SSL Auth Server configurado${NC}"
        echo "$auth_ssl"
    else
        echo -e "${YELLOW}⚠️  SSL Auth Server aún configurándose${NC}"
    fi
}

# Función para verificar base de datos
verify_database() {
    echo -e "${BLUE}🗄️  Verificando conexión a base de datos...${NC}"
    
    local db_status=$($SSH_CMD "docker exec siac-assistant-db pg_isready -U siac -d siac_chatgpt 2>/dev/null && echo 'OK' || echo 'FAIL'")
    
    if [ "$db_status" = "OK" ]; then
        echo -e "${GREEN}✅ Base de datos conectada${NC}"
        
        # Verificar tablas
        local tables=$($SSH_CMD "docker exec siac-assistant-db psql -U siac -d siac_chatgpt -c '\\dt' 2>/dev/null | grep -c 'table' || echo '0'")
        echo -e "${GREEN}✅ Tablas en base de datos: $tables${NC}"
    else
        echo -e "${RED}❌ Base de datos no disponible${NC}"
        return 1
    fi
}

# Función para verificar herramientas MCP
verify_mcp_tools() {
    echo -e "${BLUE}🔧 Verificando herramientas MCP...${NC}"
    
    local mcp_response=$(curl -s "$API_URL/mcp" 2>/dev/null | head -c 100)
    
    if [ -n "$mcp_response" ]; then
        echo -e "${GREEN}✅ Endpoint MCP responde${NC}"
        echo "Respuesta: $mcp_response..."
    else
        echo -e "${RED}❌ Endpoint MCP no responde${NC}"
        return 1
    fi
}

# Función para verificar OpenID Connect Discovery
verify_openid_discovery() {
    echo -e "${BLUE}🔍 Verificando OpenID Connect Discovery...${NC}"
    
    local discovery_response=$(curl -s "$AUTH_URL/.well-known/openid-configuration" 2>/dev/null | head -c 200)
    
    if [ -n "$discovery_response" ]; then
        echo -e "${GREEN}✅ OpenID Discovery responde${NC}"
        echo "Respuesta: $discovery_response..."
    else
        echo -e "${RED}❌ OpenID Discovery no responde${NC}"
        return 1
    fi
}

# Función para verificar endpoints OAuth 2.1
verify_oauth_endpoints() {
    echo -e "${BLUE}🔐 Verificando endpoints OAuth 2.1...${NC}"
    
    # Verificar endpoint de autorización
    local auth_endpoint=$(curl -s "$AUTH_URL/oauth/authorize?response_type=code&client_id=test&redirect_uri=https://test.com&scope=siac.user.full_access" 2>/dev/null | head -c 100)
    
    if [ -n "$auth_endpoint" ]; then
        echo -e "${GREEN}✅ Endpoint de autorización responde${NC}"
    else
        echo -e "${RED}❌ Endpoint de autorización no responde${NC}"
        return 1
    fi
    
    # Verificar endpoint de token
    local token_endpoint=$(curl -s -X POST "$AUTH_URL/oauth/token" 2>/dev/null | head -c 100)
    
    if [ -n "$token_endpoint" ]; then
        echo -e "${GREEN}✅ Endpoint de token responde${NC}"
    else
        echo -e "${RED}❌ Endpoint de token no responde${NC}"
        return 1
    fi
}

# Función para verificar archivos estáticos
verify_static_files() {
    echo -e "${BLUE}📁 Verificando archivos estáticos...${NC}"
    
    local static_files=$($SSH_CMD "docker exec siac-assistant ls -la /app/web/dist/ 2>/dev/null | wc -l")
    
    if [ "$static_files" -gt 0 ]; then
        echo -e "${GREEN}✅ Archivos estáticos disponibles: $static_files${NC}"
        $SSH_CMD "docker exec siac-assistant ls -la /app/web/dist/"
    else
        echo -e "${RED}❌ Archivos estáticos no encontrados${NC}"
        return 1
    fi
}

# Ejecutar verificaciones
echo -e "${BLUE}🚀 Iniciando verificaciones completas...${NC}"
echo ""

# Verificar conexión al VPS
echo -e "${BLUE}📡 Verificando conexión al VPS...${NC}"
if $SSH_CMD "echo 'Conexión OK'"; then
    echo -e "${GREEN}✅ Conexión al VPS establecida${NC}"
else
    echo -e "${RED}❌ No se puede conectar al VPS${NC}"
    exit 1
fi

echo ""

# Verificar contenedores
verify_containers
echo ""

# Verificar logs
verify_logs
echo ""

# Verificar base de datos
verify_database
echo ""

# Verificar archivos estáticos
verify_static_files
echo ""

# Verificar endpoints SIAC Assistant
echo -e "${BLUE}🌐 Verificando endpoints SIAC Assistant...${NC}"
verify_endpoint "/health" "Health Check SIAC" "$API_URL"
verify_endpoint "/mcp" "Endpoint MCP" "$API_URL"
verify_endpoint "/docs" "Documentación SIAC" "$API_URL"
echo ""

# Verificar endpoints Auth Server
echo -e "${BLUE}🔐 Verificando endpoints Auth Server...${NC}"
verify_endpoint "/health" "Health Check Auth" "$AUTH_URL"
verify_endpoint "/.well-known/openid-configuration" "OpenID Discovery" "$AUTH_URL"
verify_endpoint "/docs" "Documentación Auth" "$AUTH_URL"
echo ""

# Verificar SSL
verify_ssl
echo ""

# Verificar herramientas MCP
verify_mcp_tools
echo ""

# Verificar OpenID Discovery
verify_openid_discovery
echo ""

# Verificar endpoints OAuth 2.1
verify_oauth_endpoints
echo ""

# Resumen final
echo -e "${BLUE}📊 RESUMEN DE VERIFICACIÓN COMPLETA${NC}"
echo -e "${BLUE}===================================${NC}"
echo ""

# Contar verificaciones exitosas
local success_count=0
local total_count=10

# Verificar cada componente
verify_containers > /dev/null 2>&1 && ((success_count++))
verify_database > /dev/null 2>&1 && ((success_count++))
verify_static_files > /dev/null 2>&1 && ((success_count++))
verify_endpoint "/health" "Health Check SIAC" "$API_URL" > /dev/null 2>&1 && ((success_count++))
verify_endpoint "/mcp" "Endpoint MCP" "$API_URL" > /dev/null 2>&1 && ((success_count++))
verify_endpoint "/health" "Health Check Auth" "$AUTH_URL" > /dev/null 2>&1 && ((success_count++))
verify_endpoint "/.well-known/openid-configuration" "OpenID Discovery" "$AUTH_URL" > /dev/null 2>&1 && ((success_count++))
verify_mcp_tools > /dev/null 2>&1 && ((success_count++))
verify_openid_discovery > /dev/null 2>&1 && ((success_count++))
verify_oauth_endpoints > /dev/null 2>&1 && ((success_count++))

echo -e "${BLUE}Verificaciones exitosas: $success_count/$total_count${NC}"

if [ "$success_count" -eq "$total_count" ]; then
    echo -e "${GREEN}🎉 VERIFICACIÓN COMPLETA EXITOSA${NC}"
    echo -e "${GREEN}================================${NC}"
    echo ""
    echo -e "${BLUE}📋 Información del Despliegue:${NC}"
    echo "• URL del Conector MCP: $API_URL/mcp"
    echo "• URL del Auth Server: $AUTH_URL"
    echo "• Health Check SIAC: $API_URL/health"
    echo "• Health Check Auth: $AUTH_URL/health"
    echo "• OpenID Discovery: $AUTH_URL/.well-known/openid-configuration"
    echo "• Estado: ✅ COMPLETAMENTE OPERATIVO"
    echo ""
    echo -e "${GREEN}✅ El SIAC Assistant con OAuth 2.1 está listo para usar en ChatGPT!${NC}"
    echo ""
    echo -e "${BLUE}🔐 Configuración OAuth 2.1 para ChatGPT:${NC}"
    echo "• Issuer URL: $AUTH_URL"
    echo "• Authorization Endpoint: $AUTH_URL/oauth/authorize"
    echo "• Token Endpoint: $AUTH_URL/oauth/token"
    echo "• JWKS URI: $AUTH_URL/oauth/keys"
    echo "• Required Scope: siac.user.full_access"
else
    echo -e "${YELLOW}⚠️  VERIFICACIÓN PARCIAL${NC}"
    echo -e "${YELLOW}=====================${NC}"
    echo ""
    echo -e "${YELLOW}Algunas verificaciones fallaron. Revisa los logs y configuración.${NC}"
    echo -e "${YELLOW}Los servicios pueden estar aún inicializándose.${NC}"
fi

echo ""
echo -e "${BLUE}🔧 Comandos de Diagnóstico:${NC}"
echo "• Ver logs SIAC: $SSH_CMD 'docker logs siac-assistant --tail 50'"
echo "• Ver logs Auth: $SSH_CMD 'docker logs siac-auth-server --tail 50'"
echo "• Estado contenedores: $SSH_CMD 'docker ps | grep siac'"
echo "• Reiniciar servicios: $SSH_CMD 'cd $DEPLOY_DIR && docker-compose -f docker-compose.production.yml restart'"
echo "• Verificar SSL SIAC: curl -I $API_URL"
echo "• Verificar SSL Auth: curl -I $AUTH_URL"
echo "• Probar MCP: curl $API_URL/mcp"
echo "• Probar Discovery: curl $AUTH_URL/.well-known/openid-configuration"



