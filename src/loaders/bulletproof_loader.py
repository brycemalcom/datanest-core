#!/usr/bin/env python3
"""
Bulletproof Loader - Uses PostgreSQL COPY for maximum reliability  
SECURITY: Uses secure configuration management - no hardcoded credentials
"""

import csv
import psycopg2
import pandas as pd
import tempfile
import os
import time
import sys

# Add src to path for imports
sys.path.append(os.path.join(os.path.dirname(__file__), '..'))

# CRITICAL: Set CSV field size limit FIRST
try:
    csv.field_size_limit(2147483647)
    print(f"✅ CSV limit: {csv.field_size_limit():,} bytes")
except OverflowError:
    csv.field_size_limit(1000000000)
    print(f"✅ CSV limit: {csv.field_size_limit():,} bytes")

# SECURITY: Database connection loaded from secure sources only
# Never hardcode credentials - use environment variables or AWS Secrets Manager
try:
    from config import get_db_config
    CONN_PARAMS = get_db_config()
    print("✅ Database configuration loaded securely")
except Exception as e:
    print(f"❌ SECURITY ERROR: Failed to load secure database configuration: {e}")
    print("Please set environment variables: DB_HOST, DB_USER, DB_PASSWORD, DB_NAME")
    print("Or configure AWS Secrets Manager with 'datnest-core/db/credentials'")
    sys.exit(1)

def load_with_copy_command():
    """Use PostgreSQL COPY command - fastest and most reliable"""
    file_path = r"C:\DataNest-TSV-Files\extracted-tsv\Quantarium_OpenLien_20250414_00001.TSV"
    
    print("🚀 Bulletproof Loading with PostgreSQL COPY...")
    
    try:
        # Step 1: Read just the key fields we need
        print("📖 Reading first 1000 rows for testing...")
        
        chunk = pd.read_csv(
            file_path,
            sep='\t',
            nrows=1000,  # Test with small batch first
            dtype=str,
            encoding='utf-8',
            engine='python',
            quoting=csv.QUOTE_NONE,
            on_bad_lines='skip'
        )
        
        print(f"✅ Read {len(chunk)} rows, {len(chunk.columns)} columns")
        
        # Step 2: Create minimal clean DataFrame with just essential fields
        clean_data = pd.DataFrame()
        
        # Map only the essential fields
        field_mapping = {
            'Quantarium_Internal_PID': 'quantarium_internal_pid',
            'Assessors_Parcel_Number': 'apn',
            'FIPS_Code': 'fips_code',
            'ESTIMATED_VALUE': 'estimated_value',
            'Property_State': 'property_state'
        }
        
        for tsv_col, db_col in field_mapping.items():
            if tsv_col in chunk.columns:
                clean_data[db_col] = chunk[tsv_col]
        
        # Step 3: Clean data aggressively
        # Handle required NOT NULL fields
        clean_data['quantarium_internal_pid'] = clean_data['quantarium_internal_pid'].fillna('UNKNOWN')
        clean_data['apn'] = clean_data['apn'].fillna('UNKNOWN')
        clean_data['fips_code'] = clean_data['fips_code'].fillna('00000')
        
        # Handle optional fields - replace empty with NULL markers
        clean_data['estimated_value'] = clean_data['estimated_value'].replace(['', ' ', 'NULL'], '\\N')
        clean_data['property_state'] = clean_data['property_state'].fillna('')
        
        print(f"✅ Data cleaned: {len(clean_data)} rows")
        
        # Step 4: Create temporary file for COPY command
        with tempfile.NamedTemporaryFile(mode='w', delete=False, suffix='.csv', newline='') as tmp_file:
            # Write CSV data (PostgreSQL COPY format)
            clean_data.to_csv(tmp_file, sep='\t', header=False, index=False, na_rep='\\N')
            tmp_file_path = tmp_file.name
        
        print(f"✅ Temporary file created: {tmp_file_path}")
        
        # Step 5: Use PostgreSQL COPY command (ultra-fast)
        conn = psycopg2.connect(**CONN_PARAMS)
        cursor = conn.cursor()
        
        # Set schema path
        cursor.execute("SET search_path TO datnest, public")
        
        print("🚀 Starting COPY command...")
        start_time = time.time()
        
        with open(tmp_file_path, 'r') as f:
            cursor.copy_from(
                f,
                'properties',
                columns=('quantarium_internal_pid', 'apn', 'fips_code', 'estimated_value', 'property_state'),
                sep='\t',
                null='\\N'
            )
        
        conn.commit()
        elapsed = time.time() - start_time
        
        # Check results
        cursor.execute("SELECT COUNT(*) FROM datnest.properties")
        count = cursor.fetchone()[0]
        
        cursor.close()
        conn.close()
        
        # Cleanup
        os.unlink(tmp_file_path)
        
        print(f"🎉 COPY completed: {count:,} records in {elapsed:.1f} seconds")
        print(f"📈 Rate: {count/elapsed:.0f} records/second")
        
        return True
        
    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()
        return False

def test_simple_insert():
    """Test very simple single record insert first"""
    print("🧪 Testing simple single record insert...")
    
    try:
        conn = psycopg2.connect(**CONN_PARAMS)
        cursor = conn.cursor()
        
        # Truncate first
        cursor.execute("TRUNCATE TABLE datnest.properties RESTART IDENTITY CASCADE")
        conn.commit()
        print("✅ Table truncated")
        
        # Insert one simple record
        cursor.execute("""
            INSERT INTO datnest.properties (quantarium_internal_pid, apn, fips_code) 
            VALUES ('TEST123', 'TEST-APN', '12345')
        """)
        conn.commit()
        
        # Check it worked
        cursor.execute("SELECT COUNT(*) FROM datnest.properties")
        count = cursor.fetchone()[0]
        
        cursor.close()
        conn.close()
        
        print(f"✅ Simple insert successful: {count} record")
        return True
        
    except Exception as e:
        print(f"❌ Simple insert failed: {e}")
        return False

if __name__ == "__main__":
    print("🛡️ Bulletproof Loader")
    print("=" * 40)
    
    # Test simple insert first
    if test_simple_insert():
        print()
        # Then try COPY command
        load_with_copy_command()
    else:
        print("❌ Basic functionality test failed") 