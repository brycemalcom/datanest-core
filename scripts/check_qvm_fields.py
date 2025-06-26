#!/usr/bin/env python3
"""
Check QVM fields in current database
"""

import os
import sys

# Add src directory to path
sys.path.append(os.path.join(os.path.dirname(__file__), '..', 'src'))

import psycopg2
from config import get_db_config

def check_qvm_fields():
    """Check which QVM fields exist"""
    
    try:
        db_config = get_db_config()
        conn = psycopg2.connect(**db_config)
        cursor = conn.cursor()
        
        # Check QVM fields
        cursor.execute("""
            SELECT column_name 
            FROM information_schema.columns 
            WHERE table_name = 'properties' 
            AND table_schema = 'datnest'
            AND (column_name LIKE '%qvm%' OR column_name IN ('estimated_value', 'confidence_score', 'data_quality_score'))
            ORDER BY column_name;
        """)
        
        qvm_fields = [row[0] for row in cursor.fetchall()]
        
        print("QVM-related fields:")
        for field in qvm_fields:
            print(f"  • {field}")
        
        # Check missing ones
        expected_qvm = ['estimated_value', 'confidence_score', 'qvm_asof_date', 'data_quality_score']
        missing = [field for field in expected_qvm if field not in qvm_fields]
        
        if missing:
            print(f"\nMissing QVM fields:")
            for field in missing:
                print(f"  • {field}")
        
        conn.close()
        return qvm_fields
        
    except Exception as e:
        print(f"Error: {e}")
        return []

if __name__ == "__main__":
    check_qvm_fields() 