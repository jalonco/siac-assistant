#!/usr/bin/env python3
"""
SIAC Assistant - Database Setup Script

This script creates the database tables based on the schemas defined in schemas.py
"""

import os
import sys
from pathlib import Path

# Add server directory to path
server_path = str(Path(__file__).parent / "server")
sys.path.insert(0, server_path)

from sqlalchemy import create_engine, text
from schemas import User, Client, WhatsAppPhoneNumber, MessageTemplate, Campaign, MessageTransaction
from sqlalchemy.orm import sessionmaker

# Database connection string
DATABASE_URL = "postgresql://siac:siac123@localhost:5432/siac_chatgpt"

def create_tables():
    """Create all database tables."""
    print("🔧 Setting up SIAC Assistant Database...")
    print("=" * 50)
    
    try:
        # Create engine
        engine = create_engine(DATABASE_URL)
        
        # Test connection
        with engine.connect() as conn:
            result = conn.execute(text("SELECT version()"))
            version = result.fetchone()[0]
            print(f"✅ Connected to PostgreSQL: {version}")
        
        # Create tables
        print("\n📋 Creating database tables...")
        
        # Create Users table
        users_table_sql = """
        CREATE TABLE IF NOT EXISTS users (
            id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
            email VARCHAR(255) UNIQUE NOT NULL,
            password_hash VARCHAR(255) NOT NULL,
            first_name VARCHAR(100) NOT NULL,
            last_name VARCHAR(100) NOT NULL,
            is_active BOOLEAN DEFAULT TRUE,
            created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
            updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
        );
        """
        
        # Create Clients table
        clients_table_sql = """
        CREATE TABLE IF NOT EXISTS clients (
            id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
            name VARCHAR(255) NOT NULL,
            billing_email VARCHAR(255) NOT NULL,
            created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
            updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
        );
        """
        
        # Create WhatsApp Phone Numbers table
        whatsapp_phones_table_sql = """
        CREATE TABLE IF NOT EXISTS whatsapp_phone_numbers (
            id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
            phone_number VARCHAR(20) UNIQUE NOT NULL,
            is_default BOOLEAN DEFAULT FALSE,
            description TEXT,
            created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
            updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
        );
        """
        
        # Create Message Templates table
        message_templates_table_sql = """
        CREATE TABLE IF NOT EXISTS message_templates (
            id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
            template_name VARCHAR(255) NOT NULL,
            body_text TEXT NOT NULL,
            category VARCHAR(50) NOT NULL CHECK (category IN ('Marketing', 'Utility', 'Authentication')),
            language_code VARCHAR(10) NOT NULL,
            status VARCHAR(20) DEFAULT 'PENDING' CHECK (status IN ('PENDING', 'APPROVED', 'REJECTED', 'PAUSED')),
            meta_template_id VARCHAR(255),
            created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
            updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
        );
        """
        
        # Create Campaigns table
        campaigns_table_sql = """
        CREATE TABLE IF NOT EXISTS campaigns (
            id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
            campaign_name VARCHAR(255) NOT NULL,
            template_id UUID REFERENCES message_templates(id),
            whatsapp_phone_number_id UUID REFERENCES whatsapp_phone_numbers(id),
            segment_name VARCHAR(255) NOT NULL,
            status VARCHAR(20) DEFAULT 'DRAFT' CHECK (status IN ('DRAFT', 'SCHEDULED', 'RUNNING', 'COMPLETED', 'PAUSED', 'CANCELLED')),
            schedule_time TIMESTAMP WITH TIME ZONE,
            total_recipients_planned INTEGER DEFAULT 0,
            created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
            updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
        );
        """
        
        # Create Message Transactions table
        message_transactions_table_sql = """
        CREATE TABLE IF NOT EXISTS message_transactions (
            id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
            campaign_id UUID REFERENCES campaigns(id),
            whatsapp_phone_number_id UUID REFERENCES whatsapp_phone_numbers(id),
            recipient_phone VARCHAR(20) NOT NULL,
            message_content TEXT NOT NULL,
            status VARCHAR(20) DEFAULT 'PENDING' CHECK (status IN ('PENDING', 'SENT', 'DELIVERED', 'READ', 'FAILED')),
            cost_unit_applied DECIMAL(10,4) DEFAULT 0.0000,
            variable_payload_json JSONB,
            sent_at TIMESTAMP WITH TIME ZONE,
            delivered_at TIMESTAMP WITH TIME ZONE,
            read_at TIMESTAMP WITH TIME ZONE,
            created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
            updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
        );
        """
        
        # Execute table creation
        with engine.connect() as conn:
            conn.execute(text(users_table_sql))
            print("✅ Created users table")
            
            conn.execute(text(clients_table_sql))
            print("✅ Created clients table")
            
            conn.execute(text(whatsapp_phones_table_sql))
            print("✅ Created whatsapp_phone_numbers table")
            
            conn.execute(text(message_templates_table_sql))
            print("✅ Created message_templates table")
            
            conn.execute(text(campaigns_table_sql))
            print("✅ Created campaigns table")
            
            conn.execute(text(message_transactions_table_sql))
            print("✅ Created message_transactions table")
            
            # Commit changes
            conn.commit()
        
        print("\n🎉 Database setup completed successfully!")
        
        # Verify tables were created
        print("\n📊 Verifying tables...")
        with engine.connect() as conn:
            result = conn.execute(text("""
                SELECT table_name 
                FROM information_schema.tables 
                WHERE table_schema = 'public' 
                ORDER BY table_name;
            """))
            tables = [row[0] for row in result.fetchall()]
            
            print(f"📋 Tables created: {', '.join(tables)}")
            
            # Show table counts
            for table in tables:
                count_result = conn.execute(text(f"SELECT COUNT(*) FROM {table};"))
                count = count_result.fetchone()[0]
                print(f"   - {table}: {count} records")
        
        return True
        
    except Exception as e:
        print(f"❌ Error setting up database: {str(e)}")
        return False

def insert_sample_data():
    """Insert sample data for testing."""
    print("\n🌱 Inserting sample data...")
    
    try:
        engine = create_engine(DATABASE_URL)
        
        with engine.connect() as conn:
            # Insert sample users
            conn.execute(text("""
                INSERT INTO users (email, password_hash, first_name, last_name) 
                VALUES 
                    ('admin@siac.com', 'hashed_password_123', 'Admin', 'User'),
                    ('user@siac.com', 'hashed_password_456', 'Test', 'User')
                ON CONFLICT (email) DO NOTHING;
            """))
            
            # Insert sample clients
            conn.execute(text("""
                INSERT INTO clients (name, billing_email) 
                VALUES 
                    ('SIAC Enterprise', 'billing@siac.com'),
                    ('Test Client', 'test@client.com')
                ON CONFLICT DO NOTHING;
            """))
            
            # Insert sample WhatsApp phone numbers
            conn.execute(text("""
                INSERT INTO whatsapp_phone_numbers (phone_number, is_default, description) 
                VALUES 
                    ('+1234567890', TRUE, 'Primary business number'),
                    ('+0987654321', FALSE, 'Secondary number')
                ON CONFLICT (phone_number) DO NOTHING;
            """))
            
            # Insert sample message templates
            conn.execute(text("""
                INSERT INTO message_templates (template_name, body_text, category, language_code, status) 
                VALUES 
                    ('Welcome Message', 'Welcome to our service! Your account {{1}} is ready.', 'Marketing', 'es_ES', 'APPROVED'),
                    ('Order Confirmation', 'Your order {{1}} has been confirmed. Total: {{2}}', 'Utility', 'es_ES', 'APPROVED')
                ON CONFLICT DO NOTHING;
            """))
            
            conn.commit()
            print("✅ Sample data inserted successfully")
            
    except Exception as e:
        print(f"❌ Error inserting sample data: {str(e)}")

def main():
    """Main function."""
    print("SIAC Assistant - Database Setup")
    print("=" * 50)
    
    # Check if database is accessible
    try:
        engine = create_engine(DATABASE_URL)
        with engine.connect() as conn:
            result = conn.execute(text("SELECT 1"))
            print("✅ Database connection successful")
    except Exception as e:
        print(f"❌ Cannot connect to database: {str(e)}")
        print("Please ensure PostgreSQL is running and the database 'siac_chatgpt' exists.")
        return False
    
    # Create tables
    if not create_tables():
        return False
    
    # Insert sample data
    insert_sample_data()
    
    print("\n🎉 Database setup completed!")
    print("\nNext steps:")
    print("1. Start the MCP server: cd server && ./start.sh")
    print("2. Test the connection with: python test_auth.py")
    print("3. Run the security flow tests: python test_security_flow.py")
    
    return True

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)



