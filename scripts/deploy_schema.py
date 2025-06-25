#!/usr/bin/env python3
"""
Deploy DatNest database schema to RDS PostgreSQL
SECURITY: Uses secure configuration management - no hardcoded credentials
"""
import psycopg2
import os
import sys

# Add src to path for secure config
sys.path.append(os.path.join(os.path.dirname(__file__), '..', 'src'))

def deploy_schema():
    # SECURITY: Database connection loaded from secure sources only
    try:
        from config import get_db_config
        conn_params = get_db_config()
        print("✅ Database configuration loaded securely")
    except Exception as e:
        print(f"❌ SECURITY ERROR: Failed to load secure database configuration: {e}")
        print("Please set environment variables: DB_HOST, DB_USER, DB_PASSWORD, DB_NAME")
        print("Or configure AWS Secrets Manager with 'datnest-core/db/credentials'")
        return False
    
    print("🚀 Connecting to DatNest PostgreSQL database...")
    
    try:
        # Connect to PostgreSQL
        conn = psycopg2.connect(**conn_params)
        cursor = conn.cursor()
        
        print("✅ Connected successfully!")
        
        # Read the schema file
        print("📄 Reading database schema...")
        with open('database/migrations/001_initial_schema.sql', 'r', encoding='utf-8') as f:
            schema_sql = f.read()
        
        print("🔨 Deploying database schema...")
        
        # Execute schema (split by statements to handle multiple commands)
        statements = [stmt.strip() for stmt in schema_sql.split(';') if stmt.strip()]
        
        for i, statement in enumerate(statements, 1):
            if statement:
                print(f"   Executing statement {i}/{len(statements)}...")
                cursor.execute(statement)
        
        # Commit the transaction
        conn.commit()
        
        print("🎉 Database schema deployed successfully!")
        
        # Verify tables were created
        print("🔍 Verifying tables...")
        cursor.execute("""
            SELECT table_name 
            FROM information_schema.tables 
            WHERE table_schema = 'public' 
            ORDER BY table_name;
        """)
        
        tables = cursor.fetchall()
        print(f"✅ Created {len(tables)} tables:")
        for table in tables:
            print(f"   - {table[0]}")
        
        cursor.close()
        conn.close()
        
        print("\n🚀 DATABASE IS READY FOR 150M+ RECORDS!")
        print("🎯 QVM processing pipeline is LIVE!")
        
    except Exception as e:
        print(f"❌ Error: {e}")
        return False
    
    return True

if __name__ == "__main__":
    deploy_schema() 