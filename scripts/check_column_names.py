#!/usr/bin/env python3
import sys
import psycopg2
sys.path.append('src')
from config import get_db_config

conn = psycopg2.connect(**get_db_config())
cursor = conn.cursor()

# Get columns that contain 'sale' 
cursor.execute("""
    SELECT column_name FROM information_schema.columns 
    WHERE table_name = 'properties' AND table_schema = 'datnest'
    AND column_name ILIKE '%sale%'
    ORDER BY column_name;
""")
sale_cols = [row[0] for row in cursor.fetchall()]
print(f'💰 Sale columns: {sale_cols}')

# Get columns that contain 'owner'
cursor.execute("""
    SELECT column_name FROM information_schema.columns 
    WHERE table_name = 'properties' AND table_schema = 'datnest'
    AND column_name ILIKE '%owner%'
    ORDER BY column_name;
""")
owner_cols = [row[0] for row in cursor.fetchall()]
print(f'👤 Owner columns: {owner_cols}')

cursor.close()
conn.close() 