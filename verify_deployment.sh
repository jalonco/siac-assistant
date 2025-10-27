#!/bin/bash
# SIAC Assistant - Script de Verificación Post-Despliegue
# Verificación completa del despliegue en VPS

set -e

# Configuración
VPS_HOST="srv790515.hstgr.cloud"
SSH_KEY="~/.ssh/id_ed25519"
SSH_CMD="ssh -i $SSH_KEY root@$VPS_HOST"
PROJECT_NAME="siac-assistant"
DEPLOY_DIR="/opt/$PROJECT_NAME"
API_URL="https://api.siac-app.com"

# Colores
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m'

echo -e "${BLUE}🔍 SIAC Assistant - Verificación Post-Despliegue${NC}"
echo -e "${BLUE}===============================================${NC}"
echo "Servidor: $VPS_HOST"
echo "API URL: $API_URL"
echo ""

# Función para verificar endpoint
verify_endpoint() {
    local endpoint=$1
    local description=$2
    
    echo -e "${BLUE}Verificando $description...${NC}"
    
    if curl -s -f "$API_URL$endpoint" > /dev/null 2>&1; then
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
    
    local containers=$($SSH_CMD "docker ps | grep $PROJECT_NAME | wc -l")
    
    if [ "$containers" -gt 0 ]; then
        echo -e "${GREEN}✅ Contenedores activos: $containers${NC}"
        $SSH_CMD "docker ps | grep $PROJECT_NAME"
    else
        echo -e "${RED}❌ No hay contenedores activos${NC}"
        return 1
    fi
}

# Función para verificar logs
verify_logs() {
    echo -e "${BLUE}📋 Verificando logs del servicio...${NC}"
    
    $SSH_CMD "docker logs $PROJECT_NAME --tail 20"
    
    # Verificar si hay errores críticos
    local errors=$($SSH_CMD "docker logs $PROJECT_NAME 2>&1 | grep -i 'error\\|exception\\|failed' | wc -l")
    
    if [ "$errors" -gt 0 ]; then
        echo -e "${YELLOW}⚠️  Se encontraron $errors errores en los logs${NC}"
    else
        echo -e "${GREEN}✅ No se encontraron errores críticos${NC}"
    fi
}

# Función para verificar SSL
verify_ssl() {
    echo -e "${BLUE}🔒 Verificando certificado SSL...${NC}"
    
    local ssl_info=$(curl -s -I "$API_URL" 2>/dev/null | grep -i "server\\|date\\|content-type" | head -3)
    
    if [ -n "$ssl_info" ]; then
        echo -e "${GREEN}✅ SSL configurado correctamente${NC}"
        echo "$ssl_info"
    else
        echo -e "${YELLOW}⚠️  SSL aún configurándose o no disponible${NC}"
    fi
}

# Función para verificar base de datos
verify_database() {
    echo -e "${BLUE}🗄️  Verificando conexión a base de datos...${NC}"
    
    local db_status=$($SSH_CMD "docker exec $PROJECT_NAME-db pg_isready -U siac -d siac_chatgpt 2>/dev/null && echo 'OK' || echo 'FAIL'")
    
    if [ "$db_status" = "OK" ]; then
        echo -e "${GREEN}✅ Base de datos conectada${NC}"
        
        # Verificar tablas
        local tables=$($SSH_CMD "docker exec $PROJECT_NAME-db psql -U siac -d siac_chatgpt -c '\\dt' 2>/dev/null | grep -c 'table' || echo '0'")
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

# Función para verificar archivos estáticos
verify_static_files() {
    echo -e "${BLUE}📁 Verificando archivos estáticos...${NC}"
    
    local static_files=$($SSH_CMD "docker exec $PROJECT_NAME ls -la /app/web/dist/ 2>/dev/null | wc -l")
    
    if [ "$static_files" -gt 0 ]; then
        echo -e "${GREEN}✅ Archivos estáticos disponibles: $static_files${NC}"
        $SSH_CMD "docker exec $PROJECT_NAME ls -la /app/web/dist/"
    else
        echo -e "${RED}❌ Archivos estáticos no encontrados${NC}"
        return 1
    fi
}

# Ejecutar verificaciones
echo -e "${BLUE}🚀 Iniciando verificaciones...${NC}"
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

# Verificar endpoints
echo -e "${BLUE}🌐 Verificando endpoints HTTPS...${NC}"
verify_endpoint "/health" "Health Check"
verify_endpoint "/mcp" "Endpoint MCP"
verify_endpoint "/docs" "Documentación OpenAPI"
echo ""

# Verificar SSL
verify_ssl
echo ""

# Verificar herramientas MCP
verify_mcp_tools
echo ""

# Resumen final
echo -e "${BLUE}📊 RESUMEN DE VERIFICACIÓN${NC}"
echo -e "${BLUE}========================${NC}"
echo ""

# Contar verificaciones exitosas
local success_count=0
local total_count=7

# Verificar cada componente
verify_containers > /dev/null 2>&1 && ((success_count++))
verify_database > /dev/null 2>&1 && ((success_count++))
verify_static_files > /dev/null 2>&1 && ((success_count++))
verify_endpoint "/health" "Health Check" > /dev/null 2>&1 && ((success_count++))
verify_endpoint "/mcp" "Endpoint MCP" > /dev/null 2>&1 && ((success_count++))
verify_mcp_tools > /dev/null 2>&1 && ((success_count++))

echo -e "${BLUE}Verificaciones exitosas: $success_count/$total_count${NC}"

if [ "$success_count" -eq "$total_count" ]; then
    echo -e "${GREEN}🎉 VERIFICACIÓN COMPLETA EXITOSA${NC}"
    echo -e "${GREEN}===============================${NC}"
    echo ""
    echo -e "${BLUE}📋 Información del Despliegue:${NC}"
    echo "• URL del Conector: $API_URL/mcp"
    echo "• Health Check: $API_URL/health"
    echo "• Documentación: $API_URL/docs"
    echo "• Estado: ✅ OPERATIVO"
    echo ""
    echo -e "${GREEN}✅ El SIAC Assistant está listo para usar en ChatGPT!${NC}"
else
    echo -e "${YELLOW}⚠️  VERIFICACIÓN PARCIAL${NC}"
    echo -e "${YELLOW}=====================${NC}"
    echo ""
    echo -e "${YELLOW}Algunas verificaciones fallaron. Revisa los logs y configuración.${NC}"
    echo -e "${YELLOW}El servicio puede estar aún inicializándose.${NC}"
fi

echo ""
echo -e "${BLUE}🔧 Comandos de Diagnóstico:${NC}"
echo "• Ver logs: $SSH_CMD 'docker logs $PROJECT_NAME --tail 50'"
echo "• Estado contenedores: $SSH_CMD 'docker ps | grep $PROJECT_NAME'"
echo "• Reiniciar servicio: $SSH_CMD 'cd $DEPLOY_DIR && docker-compose -f docker-compose.production.yml restart'"
echo "• Verificar SSL: curl -I $API_URL"
echo "• Probar MCP: curl $API_URL/mcp"



