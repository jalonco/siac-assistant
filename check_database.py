#!/usr/bin/env python3
"""
SIAC Assistant - Verificación de Conexión a Base de Datos
Script para verificar la conexión a PostgreSQL y mostrar información para pgAdmin
"""

import os
import sys
from pathlib import Path
import psycopg2
from psycopg2 import sql
from dotenv import load_dotenv

# Cargar variables de entorno
load_dotenv()

def print_header(title):
    """Imprimir encabezado con formato"""
    print(f"\n{'='*60}")
    print(f"🗄️  {title}")
    print(f"{'='*60}")

def print_success(message):
    """Imprimir mensaje de éxito"""
    print(f"✅ {message}")

def print_error(message):
    """Imprimir mensaje de error"""
    print(f"❌ {message}")

def print_info(message):
    """Imprimir mensaje informativo"""
    print(f"ℹ️  {message}")

def get_db_config():
    """Obtener configuración de la base de datos"""
    return {
        'host': os.getenv('DB_HOST', 'localhost'),
        'port': os.getenv('DB_PORT', '5432'),
        'database': os.getenv('DB_NAME', 'siac_chatgpt'),
        'user': os.getenv('DB_USER', 'siac'),
        'password': os.getenv('DB_PASSWORD', 'siac123')
    }

def test_connection():
    """Probar conexión a la base de datos"""
    print_header("VERIFICACIÓN DE CONEXIÓN A BASE DE DATOS")
    
    config = get_db_config()
    
    print_info("Configuración de conexión:")
    print(f"   Host: {config['host']}")
    print(f"   Puerto: {config['port']}")
    print(f"   Base de datos: {config['database']}")
    print(f"   Usuario: {config['user']}")
    print(f"   Contraseña: {'*' * len(config['password'])}")
    
    try:
        # Intentar conexión
        conn = psycopg2.connect(**config)
        print_success("Conexión exitosa a PostgreSQL")
        
        # Obtener información del servidor
        cursor = conn.cursor()
        cursor.execute("SELECT version();")
        version = cursor.fetchone()[0]
        print(f"   Versión PostgreSQL: {version}")
        
        # Verificar tablas
        cursor.execute("""
            SELECT table_name 
            FROM information_schema.tables 
            WHERE table_schema = 'public'
            ORDER BY table_name;
        """)
        tables = cursor.fetchall()
        
        if tables:
            print_success(f"Tablas encontradas: {len(tables)}")
            for table in tables:
                print(f"   📋 {table[0]}")
        else:
            print_info("No se encontraron tablas en la base de datos")
        
        # Verificar datos de muestra
        cursor.execute("SELECT COUNT(*) FROM users;")
        user_count = cursor.fetchone()[0]
        print(f"   👥 Usuarios: {user_count}")
        
        cursor.execute("SELECT COUNT(*) FROM clients;")
        client_count = cursor.fetchone()[0]
        print(f"   🏢 Clientes: {client_count}")
        
        cursor.execute("SELECT COUNT(*) FROM message_templates;")
        template_count = cursor.fetchone()[0]
        print(f"   📝 Plantillas: {template_count}")
        
        cursor.close()
        conn.close()
        
        return True
        
    except psycopg2.OperationalError as e:
        print_error(f"Error de conexión: {e}")
        return False
    except Exception as e:
        print_error(f"Error inesperado: {e}")
        return False

def print_pgadmin_instructions():
    """Imprimir instrucciones para pgAdmin"""
    print_header("INSTRUCCIONES PARA PGADMIN")
    
    config = get_db_config()
    
    print_info("Datos de conexión para pgAdmin:")
    print(f"   🏠 Host: {config['host']}")
    print(f"   🔌 Puerto: {config['port']}")
    print(f"   🗄️  Base de datos: {config['database']}")
    print(f"   👤 Usuario: {config['user']}")
    print(f"   🔑 Contraseña: {config['password']}")
    
    print("\n📋 Pasos para conectar en pgAdmin:")
    print("   1. Abrir pgAdmin")
    print("   2. Click derecho en 'Servers' → 'Create' → 'Server...'")
    print("   3. En la pestaña 'General':")
    print("      • Name: SIAC Assistant DB")
    print("   4. En la pestaña 'Connection':")
    print(f"      • Host name/address: {config['host']}")
    print(f"      • Port: {config['port']}")
    print(f"      • Maintenance database: {config['database']}")
    print(f"      • Username: {config['user']}")
    print(f"      • Password: {config['password']}")
    print("   5. En la pestaña 'SSL' (opcional):")
    print("      • SSL mode: Prefer o Disable")
    print("   6. Click 'Save'")
    
    print("\n🔧 Configuración adicional:")
    print("   • Connection Timeout: 30 segundos")
    print("   • Application Name: pgAdmin - SIAC Assistant")
    print("   • SSL Mode: Prefer (para desarrollo local puede ser Disable)")

def print_connection_strings():
    """Imprimir strings de conexión para diferentes herramientas"""
    print_header("STRINGS DE CONEXIÓN")
    
    config = get_db_config()
    
    # String de conexión estándar
    conn_string = f"postgresql://{config['user']}:{config['password']}@{config['host']}:{config['port']}/{config['database']}"
    
    print_info("String de conexión PostgreSQL:")
    print(f"   {conn_string}")
    
    print_info("String de conexión para psql:")
    print(f"   psql -h {config['host']} -p {config['port']} -U {config['user']} -d {config['database']}")
    
    print_info("String de conexión para Python (psycopg2):")
    print(f"   conn = psycopg2.connect(host='{config['host']}', port='{config['port']}', database='{config['database']}', user='{config['user']}', password='{config['password']}')")
    
    print_info("String de conexión para SQLAlchemy:")
    print(f"   DATABASE_URL = '{conn_string}'")

def print_troubleshooting():
    """Imprimir información de solución de problemas"""
    print_header("SOLUCIÓN DE PROBLEMAS")
    
    print_info("Si no puedes conectar:")
    print("   1. Verificar que PostgreSQL esté ejecutándose:")
    print("      • ps aux | grep postgres")
    print("      • brew services list | grep postgresql")
    print("   2. Verificar que el puerto 5432 esté abierto:")
    print("      • lsof -i :5432")
    print("   3. Verificar que el usuario 'siac' exista:")
    print("      • psql -h localhost -p 5432 -U postgres -c \"\\du\"")
    print("   4. Verificar que la base de datos 'siac_chatgpt' exista:")
    print("      • psql -h localhost -p 5432 -U postgres -c \"\\l\"")
    
    print("\n🔧 Comandos útiles:")
    print("   • Crear usuario: python setup_database.py")
    print("   • Verificar conexión: python test_mcp_verification.py")
    print("   • Reiniciar PostgreSQL: brew services restart postgresql")

def main():
    """Función principal"""
    print("🗄️  SIAC Assistant - Verificación de Base de Datos")
    
    # Probar conexión
    connection_ok = test_connection()
    
    if connection_ok:
        print_pgadmin_instructions()
        print_connection_strings()
    else:
        print_troubleshooting()
    
    print(f"\n✅ Verificación completada")

if __name__ == "__main__":
    main()



