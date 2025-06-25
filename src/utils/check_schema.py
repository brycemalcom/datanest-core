#!/usr/bin/env python3
"""
Check database schema and test simple insertion
SECURITY: Uses secure configuration management - no hardcoded credentials
"""

import psycopg2
import sys
import os

# Add src to path for secure config
sys.path.append(os.path.join(os.path.dirname(__file__), '..'))

def check_schema():
    """Check properties table schema"""
    try:
        from config import get_db_config
        # SECURITY: Database connection loaded from secure sources only
        db_config = get_db_config()
        conn = psycopg2.connect(**db_config)
        print("✅ Database configuration loaded securely")
    except Exception as e:
        print(f"❌ SECURITY ERROR: Failed to load secure database configuration: {e}")
        print("Please set environment variables: DB_HOST, DB_USER, DB_PASSWORD, DB_NAME")
        return
    cursor = conn.cursor()
    
    print("📊 Properties Table Schema:")
    cursor.execute("""
        SELECT column_name, data_type, is_nullable 
        FROM information_schema.columns 
        WHERE table_name = 'properties' AND table_schema = 'datnest' 
        ORDER BY ordinal_position
    """)
    
    for row in cursor.fetchall():
        col_name, data_type, nullable = row
        print(f"  {col_name}: {data_type} ({'NULL' if nullable == 'YES' else 'NOT NULL'})")
    
    cursor.close()
    conn.close()

def test_minimal_insert():
    """Test inserting one minimal record"""
    try:
        from config import get_db_config
        # SECURITY: Database connection loaded from secure sources only
        db_config = get_db_config()
        conn = psycopg2.connect(**db_config)
    except Exception as e:
        print(f"❌ SECURITY ERROR: Failed to load secure database configuration: {e}")
        return
    cursor = conn.cursor()
    
    print("\n🧪 Testing minimal insert...")
    try:
        cursor.execute("""
            INSERT INTO datnest.properties (quantarium_internal_pid, apn) 
            VALUES ('TEST123', 'TEST-APN')
            ON CONFLICT (quantarium_internal_pid) DO NOTHING
        """)
        conn.commit()
        print("✅ Minimal insert successful")
        
        # Clean up test record
        cursor.execute("DELETE FROM datnest.properties WHERE quantarium_internal_pid = 'TEST123'")
        conn.commit()
        print("✅ Test record cleaned up")
        
    except Exception as e:
        print(f"❌ Insert failed: {e}")
    
    cursor.close()
    conn.close()

if __name__ == "__main__":
    print("🔍 Database Schema Check")
    print("=" * 40)
    check_schema()
    test_minimal_insert() 