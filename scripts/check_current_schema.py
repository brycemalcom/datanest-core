#!/usr/bin/env python3
"""
Check current database schema for properties table
"""

import os
import sys

# Add src directory to path
sys.path.append(os.path.join(os.path.dirname(__file__), '..', 'src'))

import psycopg2
from config import get_db_config

def check_current_schema():
    """Check current properties table schema"""
    
    try:
        db_config = get_db_config()
        conn = psycopg2.connect(**db_config)
        cursor = conn.cursor()
        
        # Get all columns
        cursor.execute("""
            SELECT column_name, data_type, character_maximum_length
            FROM information_schema.columns 
            WHERE table_name = 'properties' 
            AND table_schema = 'datnest'
            ORDER BY column_name;
        """)
        
        columns = cursor.fetchall()
        
        print(f"Current properties table has {len(columns)} columns:")
        print()
        
        # Show owner-related columns
        owner_columns = [col for col in columns if 'owner' in col[0].lower()]
        print(f"Owner-related columns ({len(owner_columns)}):")
        for col in owner_columns:
            print(f"  • {col[0]} ({col[1]})")
        
        print()
        
        # Show location-related columns  
        location_columns = [col for col in columns if any(x in col[0].lower() for x in ['property_', 'pa_', 'location', 'match'])]
        print(f"Location-related columns ({len(location_columns)}):")
        for col in location_columns:
            print(f"  • {col[0]} ({col[1]})")
        
        conn.close()
        return True
        
    except Exception as e:
        print(f"Error: {e}")
        return False

if __name__ == "__main__":
    check_current_schema() 