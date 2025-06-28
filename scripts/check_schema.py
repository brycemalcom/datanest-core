#!/usr/bin/env python3
"""Check database schema for column issues"""

import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), '..', 'src'))

import psycopg2
from config import get_db_config

try:
    conn = psycopg2.connect(**get_db_config())
    cursor = conn.cursor()
    
    # Check for coordinate columns
    cursor.execute("""
        SELECT column_name 
        FROM information_schema.columns 
        WHERE table_name='properties' 
        AND table_schema='datnest' 
        AND (column_name LIKE '%longitude%' OR column_name LIKE '%latitude%')
        ORDER BY column_name
    """)
    coord_cols = [row[0] for row in cursor.fetchall()]
    print(f"🌍 Coordinate columns: {coord_cols}")
    
    # Check if basic columns exist
    test_columns = ['quantarium_internal_pid', 'apn', 'fips_code', 'estimated_value', 
                   'property_city_name', 'current_owner_name', 'lot_size_square_feet']
    
    cursor.execute("""
        SELECT column_name 
        FROM information_schema.columns 
        WHERE table_name='properties' 
        AND table_schema='datnest' 
        AND column_name = ANY(%s)
    """, (test_columns,))
    
    existing_cols = [row[0] for row in cursor.fetchall()]
    print(f"✅ Existing basic columns: {existing_cols}")
    
    missing_cols = set(test_columns) - set(existing_cols)
    if missing_cols:
        print(f"❌ Missing columns: {missing_cols}")
    
    cursor.close()
    conn.close()
    
except Exception as e:
    print(f"❌ Error: {e}") 