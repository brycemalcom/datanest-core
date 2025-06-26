#!/usr/bin/env python3
"""
RUN SINGLE MIGRATION
A dedicated script to run one specific SQL migration file.
"""

import os
import sys
import psycopg2

# Add src to path for imports
sys.path.append(os.path.join(os.path.dirname(__file__), '..', 'src'))
from config import get_db_config

def run_single_migration(file_name):
    """Executes a single SQL migration file."""
    
    migration_path = os.path.join(os.path.dirname(__file__), '..', 'database', 'migrations', file_name)
    
    print("🚀 DataNest Single Migration Runner")
    print(f"🎯 Executing: {file_name}")
    print("="*40)

    if not os.path.exists(migration_path):
        print(f"❌ ERROR: Migration file not found at {migration_path}")
        return

    try:
        db_config = get_db_config()
        conn = psycopg2.connect(**db_config)
        cursor = conn.cursor()
        
        with open(migration_path, 'r') as f:
            sql_script = f.read()
            cursor.execute(sql_script)
        
        conn.commit()
        print(f"✅ Migration '{file_name}' applied successfully!")

    except psycopg2.Error as e:
        print(f"❌ DATABASE ERROR: {e}")
    except Exception as e:
        print(f"❌ An unexpected error occurred: {e}")
    finally:
        if 'conn' in locals() and conn:
            conn.close()

if __name__ == "__main__":
    if len(sys.argv) > 1:
        migration_to_run = sys.argv[1]
        run_single_migration(migration_to_run)
    else:
        print("Usage: python scripts/run_single_migration.py <migration_file_name>")
        print("Example: python scripts/run_single_migration.py 006_complete_building_characteristics.sql") 