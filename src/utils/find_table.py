#!/usr/bin/env python3
"""
Find the exact table name and schema
SECURITY: Uses secure configuration management - no hardcoded credentials
"""
import psycopg2
import sys
import os

# Add src to path for secure config
sys.path.append(os.path.join(os.path.dirname(__file__), '..'))

try:
    from config import get_db_config
    # SECURITY: Database connection loaded from secure sources only
    db_config = get_db_config()
    conn = psycopg2.connect(**db_config)
    print("✅ Database configuration loaded securely")
except Exception as e:
    print(f"❌ SECURITY ERROR: Failed to load secure database configuration: {e}")
    print("Please set environment variables: DB_HOST, DB_USER, DB_PASSWORD, DB_NAME")
    sys.exit(1)
cursor = conn.cursor()

print("🔍 Finding properties table...")

# Check all tables
cursor.execute("SELECT schemaname, tablename FROM pg_tables WHERE tablename LIKE '%properties%'")
tables = cursor.fetchall()

print("Tables found:")
for schema, table in tables:
    print(f"  {schema}.{table}")

# Check current schema
cursor.execute("SELECT current_schema()")
current_schema = cursor.fetchone()[0]
print(f"\nCurrent schema: {current_schema}")

# Test simple query
for schema, table in tables:
    try:
        full_name = f"{schema}.{table}"
        cursor.execute(f"SELECT COUNT(*) FROM {full_name}")
        count = cursor.fetchone()[0]
        print(f"✅ {full_name}: {count} records")
    except Exception as e:
        print(f"❌ {full_name}: {e}")

cursor.close()
conn.close() 