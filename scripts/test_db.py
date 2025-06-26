#!/usr/bin/env python3
"""
Database connection test for DataNest
"""

import sys, os
sys.path.append(os.path.join(os.path.dirname(__file__), '..', 'src'))

import psycopg2
from config import get_db_config

def test_connection():
    print('🔄 Testing database connection...')
    try:
        db_config = get_db_config()
        print(f"   Host: {db_config['host']}:{db_config['port']}")
        print(f"   Database: {db_config['database']}")
        
        conn = psycopg2.connect(**db_config)
        cursor = conn.cursor()
        print('✅ Database connection successful')
        
        # Test if the new fields already exist
        cursor.execute("""SELECT column_name FROM information_schema.columns 
                         WHERE table_schema='datnest' AND table_name='properties' 
                         AND column_name='first_mtg_date'""")
        result = cursor.fetchall()
        
        if result:
            print('✅ Customer priority fields already exist in schema')
        else:
            print('⏸️  Customer priority fields need to be added')
        
        # Check current field count
        cursor.execute("""SELECT COUNT(*) FROM information_schema.columns 
                         WHERE table_schema='datnest' AND table_name='properties'""")
        field_count = cursor.fetchone()[0]
        print(f"📊 Current properties table has {field_count} fields")
        
        conn.close()
        return True
        
    except Exception as e:
        print(f'❌ Connection failed: {e}')
        return False

if __name__ == "__main__":
    test_connection() 