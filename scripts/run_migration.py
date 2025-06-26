#!/usr/bin/env python3
"""
Simple migration runner for DataNest schema updates
"""

import os
import sys
from datetime import datetime

# Add src directory to path
sys.path.append(os.path.join(os.path.dirname(__file__), '..', 'src'))

import psycopg2
from config import get_db_config

def run_migration_file(migration_file):
    """Run a specific migration file"""
    migration_path = os.path.join(os.path.dirname(__file__), '..', 'database', 'migrations', migration_file)
    
    if not os.path.exists(migration_path):
        print(f"❌ ERROR: Migration file {migration_file} not found")
        return False
    
    print(f"\n🔄 Running migration: {migration_file}")
    
    try:
        # Read migration SQL
        with open(migration_path, 'r') as f:
            migration_sql = f.read()
        
        # Connect to database
        db_config = get_db_config()
        conn = psycopg2.connect(**db_config)
        cursor = conn.cursor()
        
        # Execute migration
        cursor.execute(migration_sql)
        conn.commit()
        
        print(f"✅ Migration {migration_file} completed successfully")
        return True
        
    except Exception as e:
        print(f"❌ Migration {migration_file} failed: {e}")
        return False
    finally:
        if 'conn' in locals():
            conn.close()

def main():
    """Run both migration files"""
    print("🚀 DataNest Schema Migration Runner")
    print("===================================")
    print(f"Timestamp: {datetime.now().isoformat()}")
    
    success = True
    
    # Run customer priority fields migration
    if not run_migration_file('002_customer_priority_fields.sql'):
        success = False
    
    # Run land use codes population
    if success and not run_migration_file('002b_populate_land_use_codes.sql'):
        success = False
    
    print("\n" + "="*50)
    if success:
        print("🎉 ALL MIGRATIONS SUCCESSFUL!")
        print("\n✅ Enhanced Schema Features Now Available:")
        print("   • 24 customer priority fields added")
        print("   • Intelligent land use code system")
        print("   • Mortgage/lien information fields")
        print("   • Sales intelligence fields")
        print("   • Enhanced property characteristics")
        print("   • Schema versioning system")
    else:
        print("❌ MIGRATION FAILED!")
        sys.exit(1)

if __name__ == "__main__":
    main() 