#!/usr/bin/env python3
"""
Add Evidence-Based Database Columns
Adds the 7 new columns needed for evidence-based field mapping
"""

import psycopg2
import sys
import os

# Add src to path for imports
sys.path.append(os.path.join(os.path.dirname(__file__), '..'))

from src.config import get_db_config

def add_evidence_based_columns():
    """Add missing columns for evidence-based fields"""
    
    print("🔧 ADDING EVIDENCE-BASED DATABASE COLUMNS")
    print("=" * 50)
    
    # Define the columns we need
    columns_to_add = [
        ("standardized_land_use_code", "VARCHAR(10)", "Property classification code"),
        ("style", "VARCHAR(100)", "Architectural style"),
        ("zoning", "VARCHAR(100)", "Zoning classification"),
        ("owner_occupied", "VARCHAR(10)", "Owner occupancy status"),
        ("current_owner_name", "VARCHAR(200)", "Current owner name"),
        ("building_quality", "VARCHAR(50)", "Building quality rating"),
        ("building_condition", "VARCHAR(50)", "Building condition rating")
    ]
    
    try:
        conn = psycopg2.connect(**get_db_config())
        cursor = conn.cursor()
        cursor.execute("SET search_path TO datnest, public")
        
        # Check existing columns first
        cursor.execute("""
            SELECT column_name 
            FROM information_schema.columns 
            WHERE table_name = 'properties' AND table_schema = 'datnest'
        """)
        existing_columns = {row[0] for row in cursor.fetchall()}
        
        print(f"📊 Current table has {len(existing_columns)} columns")
        
        # Add missing columns
        added_count = 0
        for col_name, col_type, description in columns_to_add:
            if col_name not in existing_columns:
                try:
                    sql = f"ALTER TABLE properties ADD COLUMN {col_name} {col_type}"
                    cursor.execute(sql)
                    print(f"✅ Added: {col_name} ({col_type}) - {description}")
                    added_count += 1
                except Exception as e:
                    print(f"❌ Failed to add {col_name}: {e}")
            else:
                print(f"⏭️  Exists: {col_name}")
        
        conn.commit()
        
        # Verify final state
        cursor.execute("""
            SELECT column_name 
            FROM information_schema.columns 
            WHERE table_name = 'properties' AND table_schema = 'datnest'
        """)
        final_columns = {row[0] for row in cursor.fetchall()}
        
        print(f"\n🎉 COLUMN ADDITION COMPLETE")
        print(f"📊 Table now has {len(final_columns)} columns")
        print(f"✅ Added {added_count} new columns")
        
        # Verify our target columns exist
        target_columns = [col[0] for col in columns_to_add]
        missing = [col for col in target_columns if col not in final_columns]
        
        if missing:
            print(f"⚠️  Still missing: {missing}")
        else:
            print("✅ All evidence-based columns are now available!")
        
        cursor.close()
        conn.close()
        
        return len(missing) == 0
        
    except Exception as e:
        print(f"❌ Error: {e}")
        return False

if __name__ == "__main__":
    success = add_evidence_based_columns()
    if success:
        print("\n🚀 Ready to test evidence-based field mapping!")
    else:
        print("\n❌ Column addition failed - check database connection and permissions") 