#!/usr/bin/env python3
"""
FIX OTHER_ROOMS SCHEMA ISSUE
Change other_rooms column from INTEGER to VARCHAR to preserve Y/N values
"""

import os
import sys

# Add src directory to path
sys.path.append(os.path.join(os.path.dirname(__file__), '..', 'src'))

import psycopg2
from config import get_db_config

def fix_other_rooms_schema():
    """Fix other_rooms column type to preserve Y/N values"""
    
    print("🔧 FIXING OTHER_ROOMS SCHEMA ISSUE")
    print("🎯 Converting column from INTEGER to VARCHAR(10)")
    print("=" * 50)
    
    try:
        db_config = get_db_config()
        conn = psycopg2.connect(**db_config)
        cursor = conn.cursor()
        cursor.execute("SET search_path TO datnest, public")
        
        # Check current column type
        cursor.execute("""
            SELECT data_type, character_maximum_length 
            FROM information_schema.columns 
            WHERE table_name = 'properties' 
            AND table_schema = 'datnest'
            AND column_name = 'other_rooms';
        """)
        
        result = cursor.fetchone()
        if result:
            current_type, max_length = result
            print(f"📊 Current other_rooms type: {current_type}")
            if max_length:
                print(f"   Max length: {max_length}")
        else:
            print("❌ other_rooms column not found")
            return False
        
        # Fix the column type
        print("🔧 Converting other_rooms to VARCHAR(10)...")
        
        # Clear any existing data first (since we're changing types)
        cursor.execute("UPDATE properties SET other_rooms = NULL WHERE other_rooms IS NOT NULL")
        conn.commit()
        print("   ✅ Cleared existing integer data")
        
        # Change column type
        cursor.execute("ALTER TABLE properties ALTER COLUMN other_rooms TYPE VARCHAR(10)")
        conn.commit()
        print("   ✅ Column type changed to VARCHAR(10)")
        
        # Verify the change
        cursor.execute("""
            SELECT data_type, character_maximum_length 
            FROM information_schema.columns 
            WHERE table_name = 'properties' 
            AND table_schema = 'datnest'
            AND column_name = 'other_rooms';
        """)
        
        result = cursor.fetchone()
        if result:
            new_type, max_length = result
            print(f"✅ New other_rooms type: {new_type}")
            if max_length:
                print(f"   Max length: {max_length}")
            
            if new_type.lower() == 'character varying':
                print("🎉 SUCCESS: other_rooms can now store Y/N values!")
                success = True
            else:
                print("⚠️  Warning: Type conversion may not be complete")
                success = False
        else:
            print("❌ Could not verify column change")
            success = False
        
        cursor.close()
        conn.close()
        
        return success
        
    except Exception as e:
        print(f"❌ Schema fix failed: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    success = fix_other_rooms_schema()
    
    if success:
        print(f"\n🎉 OTHER_ROOMS SCHEMA FIX: COMPLETE!")
        print(f"✅ Y/N values can now be preserved correctly")
        print(f"🚀 Ready for QA validation test")
    else:
        print(f"\n❌ Schema fix needs attention") 