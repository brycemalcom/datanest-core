#!/usr/bin/env python3
"""Check database schema and tables"""

import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), '..', 'src'))

import psycopg2
from config import get_db_config

try:
    conn = psycopg2.connect(**get_db_config())
    cursor = conn.cursor()
    
    print("📊 Checking database schema...")
    
    # Check schemas
    cursor.execute("SELECT schema_name FROM information_schema.schemata")
    schemas = cursor.fetchall()
    print(f"🗂️  Available schemas: {[s[0] for s in schemas]}")
    
    # Check tables in datnest schema
    cursor.execute("SELECT table_name FROM information_schema.tables WHERE table_schema = 'datnest'")
    tables = cursor.fetchall()
    print(f"📋 Tables in datnest schema: {[t[0] for t in tables]}")
    
    # If properties table exists, check its structure
    if any(t[0] == 'properties' for t in tables):
        cursor.execute("SELECT column_name FROM information_schema.columns WHERE table_schema = 'datnest' AND table_name = 'properties'")
        columns = cursor.fetchall()
        print(f"🔧 Properties table columns: {len([c[0] for c in columns])} columns")
        print("✅ Properties table exists!")
    else:
        print("❌ Properties table NOT found")
        print("💡 Need to create database schema")
    
    cursor.close()
    conn.close()
    
except Exception as e:
    print(f"❌ Error: {e}")