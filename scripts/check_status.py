#!/usr/bin/env python3
"""Quick status check"""

import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), '..', 'src'))

import psycopg2
from config import get_db_config

try:
    conn = psycopg2.connect(**get_db_config())
    cursor = conn.cursor()
    cursor.execute("SELECT COUNT(*) FROM datnest.properties")
    count = cursor.fetchone()[0]
    print(f"📊 Records loaded: {count:,}")
    
    if count > 0:
        cursor.execute("SELECT MAX(quantarium_internal_pid) FROM datnest.properties")
        max_pid = cursor.fetchone()[0]
        print(f"🔢 Max PID: {max_pid}")
        
        cursor.execute("SELECT property_state, COUNT(*) FROM datnest.properties GROUP BY property_state")
        states = cursor.fetchall()
        print(f"🗺️  States: {states}")
    
    cursor.close()
    conn.close()
    
except Exception as e:
    print(f"❌ Error: {e}") 