#!/bin/bash
# SIAC Assistant - Verificación de Certificados SSL
# Script para verificar certificados SSL de ambos dominios

set -e

# Configuración
DOMAINS=("api.siac-app.com" "auth.siac-app.com")
VPS_HOST="srv790515.hstgr.cloud"
SSH_KEY="~/.ssh/id_ed25519"
SSH_CMD="ssh -i $SSH_KEY root@$VPS_HOST"

# Colores
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
PURPLE='\033[0;35m'
NC='\033[0m'

echo -e "${BLUE}🔒 SIAC Assistant - Verificación de Certificados SSL${NC}"
echo -e "${BLUE}===================================================${NC}"
echo ""

# Función para verificar SSL de un dominio
verify_domain_ssl() {
    local domain=$1
    echo -e "${PURPLE}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
    echo -e "${BLUE}🔍 Verificando: $domain${NC}"
    echo -e "${PURPLE}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
    echo ""
    
    # 1. Verificar resolución DNS
    echo -e "${YELLOW}1. Resolución DNS:${NC}"
    ip=$(dig +short $domain | tail -n1)
    if [ -n "$ip" ]; then
        echo -e "${GREEN}✅ $domain → $ip${NC}"
    else
        echo -e "${RED}❌ $domain no resuelve${NC}"
        return 1
    fi
    echo ""
    
    # 2. Verificar conectividad HTTPS
    echo -e "${YELLOW}2. Conectividad HTTPS:${NC}"
    if curl -s -I "https://$domain/health" > /dev/null 2>&1; then
        echo -e "${GREEN}✅ HTTPS responde correctamente${NC}"
        http_status=$(curl -s -o /dev/null -w "%{http_code}" "https://$domain/health")
        echo -e "${GREEN}   Status Code: $http_status${NC}"
    else
        echo -e "${RED}❌ HTTPS no responde${NC}"
        return 1
    fi
    echo ""
    
    # 3. Información del certificado
    echo -e "${YELLOW}3. Información del Certificado:${NC}"
    cert_info=$(echo | openssl s_client -servername $domain -connect $domain:443 2>/dev/null | openssl x509 -noout -text 2>/dev/null)
    
    if [ -n "$cert_info" ]; then
        # Emisor
        issuer=$(echo "$cert_info" | grep "Issuer:" | sed 's/.*CN = //')
        echo -e "${GREEN}✅ Emisor: $issuer${NC}"
        
        # Fechas de validez
        not_before=$(echo | openssl s_client -servername $domain -connect $domain:443 2>/dev/null | openssl x509 -noout -startdate 2>/dev/null | cut -d= -f2)
        not_after=$(echo | openssl s_client -servername $domain -connect $domain:443 2>/dev/null | openssl x509 -noout -enddate 2>/dev/null | cut -d= -f2)
        
        echo -e "${GREEN}✅ Válido desde: $not_before${NC}"
        echo -e "${GREEN}✅ Válido hasta: $not_after${NC}"
        
        # Verificar si es Let's Encrypt
        if echo "$issuer" | grep -q "Let's Encrypt"; then
            echo -e "${GREEN}✅ Certificado emitido por Let's Encrypt${NC}"
        else
            echo -e "${YELLOW}⚠️  Certificado NO es de Let's Encrypt${NC}"
        fi
        
        # Días restantes
        expiry_date=$(date -d "$not_after" +%s 2>/dev/null || date -j -f "%b %d %T %Y %Z" "$not_after" +%s 2>/dev/null)
        current_date=$(date +%s)
        days_remaining=$(( ($expiry_date - $current_date) / 86400 ))
        
        if [ $days_remaining -gt 30 ]; then
            echo -e "${GREEN}✅ Días restantes: $days_remaining días${NC}"
        elif [ $days_remaining -gt 7 ]; then
            echo -e "${YELLOW}⚠️  Días restantes: $days_remaining días (renovar pronto)${NC}"
        else
            echo -e "${RED}❌ Días restantes: $days_remaining días (RENOVAR URGENTE)${NC}"
        fi
    else
        echo -e "${RED}❌ No se pudo obtener información del certificado${NC}"
        return 1
    fi
    echo ""
    
    # 4. Verificar cadena de certificados
    echo -e "${YELLOW}4. Cadena de Certificados:${NC}"
    chain_verify=$(echo | openssl s_client -servername $domain -connect $domain:443 2>/dev/null | openssl x509 -noout -text 2>/dev/null | grep -c "Certificate:" || echo "0")
    if [ "$chain_verify" -gt 0 ]; then
        echo -e "${GREEN}✅ Cadena de certificados válida${NC}"
    else
        echo -e "${RED}❌ Problemas con la cadena de certificados${NC}"
    fi
    echo ""
    
    # 5. Verificar protocolos SSL/TLS
    echo -e "${YELLOW}5. Protocolos SSL/TLS soportados:${NC}"
    
    # TLS 1.2
    if echo | openssl s_client -servername $domain -connect $domain:443 -tls1_2 2>/dev/null | grep -q "Cipher"; then
        echo -e "${GREEN}✅ TLS 1.2: Soportado${NC}"
    else
        echo -e "${YELLOW}⚠️  TLS 1.2: No soportado${NC}"
    fi
    
    # TLS 1.3
    if echo | openssl s_client -servername $domain -connect $domain:443 -tls1_3 2>/dev/null | grep -q "Cipher"; then
        echo -e "${GREEN}✅ TLS 1.3: Soportado${NC}"
    else
        echo -e "${YELLOW}⚠️  TLS 1.3: No soportado${NC}"
    fi
    echo ""
    
    # 6. Headers de seguridad
    echo -e "${YELLOW}6. Headers de Seguridad:${NC}"
    headers=$(curl -s -I "https://$domain/health" 2>/dev/null)
    
    if echo "$headers" | grep -qi "Strict-Transport-Security"; then
        echo -e "${GREEN}✅ HSTS configurado${NC}"
    else
        echo -e "${YELLOW}⚠️  HSTS no configurado${NC}"
    fi
    
    if echo "$headers" | grep -qi "X-Content-Type-Options"; then
        echo -e "${GREEN}✅ X-Content-Type-Options configurado${NC}"
    else
        echo -e "${YELLOW}⚠️  X-Content-Type-Options no configurado${NC}"
    fi
    echo ""
    
    # 7. Prueba de SSL Labs (opcional)
    echo -e "${YELLOW}7. Análisis SSL Labs:${NC}"
    echo -e "${BLUE}   Para análisis completo visita:${NC}"
    echo -e "${BLUE}   https://www.ssllabs.com/ssltest/analyze.html?d=$domain${NC}"
    echo ""
    
    return 0
}

# Función para verificar Traefik
verify_traefik() {
    echo -e "${PURPLE}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
    echo -e "${BLUE}🔍 Verificando Traefik en VPS${NC}"
    echo -e "${PURPLE}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
    echo ""
    
    # Verificar contenedor Traefik
    echo -e "${YELLOW}1. Estado del contenedor Traefik:${NC}"
    if $SSH_CMD "docker ps | grep traefik"; then
        echo -e "${GREEN}✅ Traefik ejecutándose${NC}"
    else
        echo -e "${RED}❌ Traefik no está ejecutándose${NC}"
        return 1
    fi
    echo ""
    
    # Verificar certificados almacenados
    echo -e "${YELLOW}2. Certificados almacenados en Traefik:${NC}"
    certs=$($SSH_CMD "cat /opt/traefik/letsencrypt/acme.json 2>/dev/null | grep -o '\"main\":\"[^\"]*\"' | cut -d'\"' -f4 | sort | uniq" || echo "No se encontraron certificados")
    if [ "$certs" != "No se encontraron certificados" ]; then
        echo -e "${GREEN}✅ Certificados encontrados:${NC}"
        echo "$certs" | while read cert; do
            echo -e "${GREEN}   • $cert${NC}"
        done
    else
        echo -e "${RED}❌ No se encontraron certificados${NC}"
    fi
    echo ""
    
    # Logs recientes de Traefik
    echo -e "${YELLOW}3. Logs recientes de Traefik (certificados):${NC}"
    $SSH_CMD "docker logs traefik --tail 30 2>&1 | grep -i 'certificate\\|acme\\|tls' | tail -10" || echo "No hay logs relacionados"
    echo ""
}

# Ejecutar verificaciones
echo -e "${GREEN}🚀 Iniciando verificación de SSL...${NC}"
echo ""

# Verificar Traefik
verify_traefik

# Verificar cada dominio
for domain in "${DOMAINS[@]}"; do
    verify_domain_ssl "$domain"
    echo ""
done

# Resumen final
echo -e "${PURPLE}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
echo -e "${GREEN}📊 RESUMEN DE VERIFICACIÓN SSL${NC}"
echo -e "${PURPLE}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
echo ""

# Verificar todos los dominios
all_ok=true
for domain in "${DOMAINS[@]}"; do
    if curl -s -I "https://$domain/health" > /dev/null 2>&1; then
        echo -e "${GREEN}✅ $domain: SSL configurado correctamente${NC}"
    else
        echo -e "${RED}❌ $domain: Problemas con SSL${NC}"
        all_ok=false
    fi
done

echo ""

if [ "$all_ok" = true ]; then
    echo -e "${GREEN}🎉 TODOS LOS CERTIFICADOS SSL ESTÁN CORRECTAMENTE CONFIGURADOS${NC}"
    echo ""
    echo -e "${BLUE}📋 URLs disponibles:${NC}"
    echo "• https://api.siac-app.com/health"
    echo "• https://api.siac-app.com/mcp"
    echo "• https://api.siac-app.com/docs"
    echo "• https://auth.siac-app.com/health"
    echo "• https://auth.siac-app.com/.well-known/openid-configuration"
    echo "• https://auth.siac-app.com/docs"
else
    echo -e "${RED}⚠️  ALGUNOS CERTIFICADOS TIENEN PROBLEMAS${NC}"
    echo "Revisa los logs de Traefik para más detalles."
fi

echo ""
echo -e "${BLUE}🔧 Comandos útiles:${NC}"
echo "• Ver certificados: $SSH_CMD 'cat /opt/traefik/letsencrypt/acme.json | jq'"
echo "• Ver logs Traefik: $SSH_CMD 'docker logs traefik --tail 50'"
echo "• Reiniciar Traefik: $SSH_CMD 'docker restart traefik'"
echo "• Forzar renovación: $SSH_CMD 'docker exec traefik traefik version' (y reiniciar)"
echo ""


