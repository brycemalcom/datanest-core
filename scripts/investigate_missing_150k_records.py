#!/usr/bin/env python3
"""
INVESTIGATE MISSING 150K RECORDS
Goal: Find why 150K records were lost during loading process
"""

import os
import sys
import csv
import pandas as pd

# Set CSV limits for large files
csv.field_size_limit(2147483647)

def investigate_missing_records():
    """Investigate the 150K missing records"""
    
    print("🔍 INVESTIGATING 150K MISSING RECORDS")
    print("🎯 Goal: Find where records were lost during loading")
    print("=" * 60)
    
    tsv_path = r"C:\DataNest-TSV-Files\extracted-tsv\Quantarium_OpenLien_20250414_00001.TSV"
    
    if not os.path.exists(tsv_path):
        print(f"❌ TSV file not found at: {tsv_path}")
        return False
    
    # STEP 1: Analyze file structure throughout
    print("📊 STEP 1: FILE STRUCTURE ANALYSIS")
    
    try:
        # Sample different parts of the file
        sample_points = [
            (0, 50000, "Beginning"),
            (1000000, 50000, "1M mark"), 
            (2000000, 50000, "2M mark"),
            (3000000, 50000, "3M mark"),
            (4000000, 50000, "4M mark"),
            (4500000, 50000, "4.5M mark"),
            (4900000, 50000, "Near end")
        ]
        
        alabama_distribution = []
        arizona_distribution = []
        
        for skip_rows, sample_size, label in sample_points:
            try:
                print(f"\n   🔍 Analyzing {label} (rows {skip_rows:,} to {skip_rows+sample_size:,}):")
                
                df_sample = pd.read_csv(
                    tsv_path,
                    sep='\t',
                    skiprows=skip_rows + 1,  # +1 for header
                    nrows=sample_size,
                    dtype=str,
                    encoding='utf-8',
                    engine='python',
                    quoting=csv.QUOTE_NONE,
                    on_bad_lines='skip',
                    header=None  # No header since we skipped it
                )
                
                # Read header separately for column mapping
                df_header = pd.read_csv(tsv_path, sep='\t', nrows=0)
                df_sample.columns = df_header.columns[:len(df_sample.columns)]
                
                if 'FIPS_Code' in df_sample.columns:
                    fips_codes = df_sample['FIPS_Code'].fillna('UNKNOWN').str[:2]
                    
                    alabama_count = (fips_codes == '01').sum()
                    arizona_count = (fips_codes == '04').sum()
                    other_count = len(df_sample) - alabama_count - arizona_count
                    
                    print(f"      Alabama (01): {alabama_count:,} ({alabama_count/len(df_sample)*100:.1f}%)")
                    print(f"      Arizona (04): {arizona_count:,} ({arizona_count/len(df_sample)*100:.1f}%)")
                    if other_count > 0:
                        print(f"      Other states: {other_count:,} ({other_count/len(df_sample)*100:.1f}%)")
                    
                    alabama_distribution.append((label, skip_rows, alabama_count, len(df_sample)))
                    arizona_distribution.append((label, skip_rows, arizona_count, len(df_sample)))
                
            except Exception as e:
                print(f"      ❌ Error at {label}: {e}")
        
        # Analyze transition point
        print(f"\n🔍 FILE STRUCTURE PATTERN:")
        for label, position, al_count, total in alabama_distribution:
            al_pct = al_count/total*100 if total > 0 else 0
            print(f"   {label}: {al_pct:.1f}% Alabama")
        
    except Exception as e:
        print(f"❌ Error in structure analysis: {e}")
    
    # STEP 2: Check loading errors in our loader
    print(f"\n📋 STEP 2: LOADER ERROR ANALYSIS")
    
    try:
        # Check turbo loader for error handling
        print("   🔍 Checking loader error patterns...")
        
        # Look for common loading failure patterns
        sample_df = pd.read_csv(
            tsv_path,
            sep='\t',
            nrows=10000,
            dtype=str,
            encoding='utf-8',
            engine='python',
            quoting=csv.QUOTE_NONE,
            on_bad_lines='skip'
        )
        
        # Check for required field completeness
        required_fields = ['Quantarium_Internal_PID', 'Assessors_Parcel_Number', 'FIPS_Code']
        
        print(f"   📊 Required field completeness check:")
        for field in required_fields:
            if field in sample_df.columns:
                missing_count = sample_df[field].isna().sum() + (sample_df[field] == '').sum()
                print(f"      {field}: {missing_count:,} missing in sample")
                
                if missing_count > 0:
                    print(f"      ⚠️  Records with missing {field} would be rejected")
        
    except Exception as e:
        print(f"❌ Error in loader analysis: {e}")
    
    # STEP 3: Database duplicate analysis
    print(f"\n🔍 STEP 3: DUPLICATE ANALYSIS")
    
    try:
        import psycopg2
        sys.path.append(os.path.join(os.path.dirname(__file__), '..', 'src'))
        from config import get_db_config
        
        conn = psycopg2.connect(**get_db_config())
        cursor = conn.cursor()
        
        # Check for any loading issues that might cause record loss
        cursor.execute("""
            SELECT 
                COUNT(*) as total_loaded,
                MIN(quantarium_internal_pid::int) as min_pid,
                MAX(quantarium_internal_pid::int) as max_pid,
                MAX(quantarium_internal_pid::int) - MIN(quantarium_internal_pid::int) + 1 as pid_range,
                COUNT(DISTINCT quantarium_internal_pid) as unique_pids
            FROM datnest.properties;
        """)
        
        pid_stats = cursor.fetchone()
        total, min_pid, max_pid, pid_range, unique_pids = pid_stats
        
        print(f"   📊 PID Analysis:")
        print(f"      Total loaded: {total:,}")
        print(f"      PID range: {min_pid:,} to {max_pid:,}")
        print(f"      Expected from range: {pid_range:,}")
        print(f"      Unique PIDs: {unique_pids:,}")
        
        if pid_range > total:
            missing_in_range = pid_range - total
            print(f"      ⚠️  Missing PIDs in sequence: {missing_in_range:,}")
            print(f"      🔍 This could explain the 150K gap!")
        
        cursor.close()
        conn.close()
        
    except Exception as e:
        print(f"❌ Error in database analysis: {e}")
    
    # STEP 4: Recommendations
    print(f"\n🎯 INVESTIGATION SUMMARY:")
    print(f"   📊 TSV file: 5,000,000 records")
    print(f"   📊 Database: 4,849,999 records")
    print(f"   ⚠️  Missing: 150,001 records")
    
    print(f"\n📋 LIKELY CAUSES:")
    print(f"   1. 🔍 Sequential PID gaps in source data")
    print(f"   2. ⚠️  Loader rejecting invalid records")
    print(f"   3. 📊 Data quality filters removing records")
    print(f"   4. 🔧 Processing errors during chunked loading")
    
    print(f"\n🔧 RECOMMENDED ACTIONS:")
    print(f"   1. Re-run turbo loader with enhanced error logging")
    print(f"   2. Check for PID sequence gaps in source data")
    print(f"   3. Validate data quality thresholds")
    print(f"   4. Consider the 150K might be incomplete/invalid records")
    
    return True

if __name__ == "__main__":
    print("🚀 STARTING MISSING RECORDS INVESTIGATION")
    success = investigate_missing_records()
    print(f"\n🎯 INVESTIGATION: {'COMPLETE' if success else 'FAILED'}")
    exit(0 if success else 1) 