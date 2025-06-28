#!/usr/bin/env python3
"""
IDENTIFY MISSING 150K LOCATION
Goal: Determine if missing records are at end (Arizona) or distributed throughout
"""

import os
import sys
import csv
import pandas as pd
import psycopg2

# Add src directory to path  
sys.path.append(os.path.join(os.path.dirname(__file__), '..', 'src'))

from config import get_db_config

# Set CSV limits for large files
csv.field_size_limit(2147483647)

def identify_missing_records_location():
    """Identify where the 150K missing records are located in the file"""
    
    print("🔍 IDENTIFYING MISSING 150K RECORD LOCATIONS")
    print("🎯 Goal: Determine if missing records are at end or distributed")
    print("=" * 70)
    
    tsv_path = r"C:\DataNest-TSV-Files\extracted-tsv\Quantarium_OpenLien_20250414_00001.TSV"
    
    if not os.path.exists(tsv_path):
        print(f"❌ TSV file not found at: {tsv_path}")
        return False
    
    try:
        # Get database PID range for comparison
        conn = psycopg2.connect(**get_db_config())
        cursor = conn.cursor()
        
        cursor.execute("""
            SELECT 
                MIN(quantarium_internal_pid::int) as min_pid,
                MAX(quantarium_internal_pid::int) as max_pid,
                COUNT(*) as total_loaded
            FROM datnest.properties;
        """)
        
        min_pid, max_pid, total_loaded = cursor.fetchone()
        print(f"📊 DATABASE PID ANALYSIS:")
        print(f"   Min PID: {min_pid:,}")
        print(f"   Max PID: {max_pid:,}")
        print(f"   Total loaded: {total_loaded:,}")
        print(f"   PID range span: {max_pid - min_pid + 1:,}")
        
        cursor.close()
        conn.close()
        
        # Analyze TSV file structure by sampling different sections
        print(f"\n🔍 TSV FILE PID ANALYSIS:")
        
        sample_points = [
            (0, 10000, "Beginning"),
            (1000000, 10000, "1M mark"),
            (2000000, 10000, "2M mark (Alaska start)"),
            (3000000, 10000, "3M mark (Arizona start)"),
            (4500000, 10000, "4.5M mark"),
            (4950000, 49999, "Last 50K records")  # Check end of file
        ]
        
        tsv_pid_ranges = []
        
        for skip_rows, sample_size, label in sample_points:
            try:
                print(f"\n   📍 {label} (rows {skip_rows:,} to {skip_rows+sample_size:,}):")
                
                # Read sample
                df_sample = pd.read_csv(
                    tsv_path,
                    sep='\t',
                    skiprows=skip_rows + 1 if skip_rows > 0 else 1,  # Skip header
                    nrows=sample_size,
                    dtype=str,
                    encoding='utf-8',
                    engine='python',
                    quoting=csv.QUOTE_NONE,
                    on_bad_lines='skip',
                    header=None
                )
                
                # Get header for column mapping
                df_header = pd.read_csv(tsv_path, sep='\t', nrows=0)
                df_sample.columns = df_header.columns[:len(df_sample.columns)]
                
                if 'Quantarium_Internal_PID' in df_sample.columns:
                    # Convert PIDs to integers and analyze
                    pids = pd.to_numeric(df_sample['Quantarium_Internal_PID'], errors='coerce')
                    valid_pids = pids.dropna()
                    
                    if len(valid_pids) > 0:
                        sample_min = int(valid_pids.min())
                        sample_max = int(valid_pids.max())
                        
                        print(f"      PID range: {sample_min:,} to {sample_max:,}")
                        print(f"      Records: {len(valid_pids):,}")
                        
                        tsv_pid_ranges.append((label, sample_min, sample_max, len(valid_pids)))
                        
                        # Check if these PIDs are in database
                        if label == "Last 50K records":
                            conn = psycopg2.connect(**get_db_config())
                            cursor = conn.cursor()
                            
                            cursor.execute("""
                                SELECT COUNT(*) 
                                FROM datnest.properties 
                                WHERE quantarium_internal_pid::int BETWEEN %s AND %s;
                            """, (sample_min, sample_max))
                            
                            loaded_in_range = cursor.fetchone()[0]
                            missing_in_range = len(valid_pids) - loaded_in_range
                            
                            print(f"      📊 In database: {loaded_in_range:,}")
                            print(f"      ❌ Missing: {missing_in_range:,}")
                            
                            if missing_in_range > 0:
                                print(f"      🚨 FOUND MISSING RECORDS AT END OF FILE!")
                            
                            cursor.close()
                            conn.close()
                
                # Check state distribution for this section
                if 'FIPS_Code' in df_sample.columns:
                    fips_codes = df_sample['FIPS_Code'].fillna('UNKNOWN').str[:2]
                    state_counts = fips_codes.value_counts().head(3)
                    
                    print(f"      States in section:")
                    fips_map = {'01': 'Alabama', '02': 'Alaska', '04': 'Arizona'}
                    for fips, count in state_counts.items():
                        state_name = fips_map.get(fips, f'State {fips}')
                        pct = (count / len(df_sample)) * 100
                        print(f"         {state_name} ({fips}): {count:,} ({pct:.1f}%)")
                
            except Exception as e:
                print(f"      ❌ Error analyzing {label}: {e}")
        
        # Summary analysis
        print(f"\n🎯 MISSING RECORD LOCATION ANALYSIS:")
        print(f"   📊 TSV file total: 5,000,000 records")
        print(f"   📊 Database total: {total_loaded:,} records")
        print(f"   ❌ Missing: {5000000 - total_loaded:,} records")
        
        if tsv_pid_ranges:
            tsv_min = min(r[1] for r in tsv_pid_ranges)
            tsv_max = max(r[2] for r in tsv_pid_ranges)
            print(f"   📍 TSV PID range: {tsv_min:,} to {tsv_max:,}")
            print(f"   📍 Database PID range: {min_pid:,} to {max_pid:,}")
            
            if tsv_max > max_pid:
                print(f"   🚨 TSV has higher PIDs than database - missing records likely at end!")
            
        return True
        
    except Exception as e:
        print(f"❌ Error in analysis: {e}")
        return False

def analyze_loading_options():
    """Analyze options for completing the load"""
    
    print(f"\n" + "=" * 70)
    print("🔧 LOADING COMPLETION OPTIONS")
    print("=" * 70)
    
    print("📋 OPTION 1: INCREMENTAL LOAD (Recommended)")
    print("   ✅ Pros:")
    print("      - Faster (only load missing records)")
    print("      - Preserves existing data")
    print("      - Can identify exact gaps")
    print("   ⚠️  Cons:")
    print("      - Requires gap identification")
    print("      - May miss systematic issues")
    
    print("\n📋 OPTION 2: FULL RELOAD")
    print("   ✅ Pros:")
    print("      - Guaranteed complete load")
    print("      - Identifies any systematic issues")
    print("      - Clean slate approach")
    print("   ⚠️  Cons:")
    print("      - Longer processing time (~25 minutes)")
    print("      - Overwrites existing data")
    
    print(f"\n🎯 RECOMMENDED APPROACH:")
    print("   1. 🔍 Identify if missing records are at end of file")
    print("   2. 🔧 If yes: Incremental load from last loaded PID")
    print("   3. 🔧 If distributed: Investigate systematic issue first")
    print("   4. 📊 Validate against reference counts")
    print("   5. 🔍 Investigate delta/update files from data provider")

def generate_next_steps():
    """Generate specific next steps"""
    
    print(f"\n" + "=" * 70)
    print("🎯 NEXT STEPS PLAN")
    print("=" * 70)
    
    print("📋 IMMEDIATE ACTIONS (Next 30 minutes):")
    print("   1. ✅ Complete this missing record location analysis")
    print("   2. 🔧 If records missing at end: Prepare incremental loader")
    print("   3. 📊 Run quick test load of missing section")
    print("   4. 🔍 Validate Alabama/Alaska gap percentages")
    
    print("\n📋 FOLLOW-UP ACTIONS (Next session):")
    print("   1. 🌐 Check data provider FTP for delta/update files")
    print("   2. 📊 Compare reference counts with actual data provider files")
    print("   3. 🔧 Load File 2 (remaining Arizona + next states)")
    print("   4. 📈 Establish complete loading pipeline")
    
    print(f"\n🚨 CRITICAL DECISION POINT:")
    print("   ❓ Are the gap percentages (12-16%) due to:")
    print("      A) Missing records in our files")
    print("      B) Delta/update files not yet processed")
    print("      C) Reference counts including data not in base files")
    print("   🎯 This determines our loading strategy!")

if __name__ == "__main__":
    print("🚀 STARTING MISSING RECORD LOCATION ANALYSIS")
    
    success1 = identify_missing_records_location()
    analyze_loading_options()
    generate_next_steps()
    
    overall_success = success1
    print(f"\n🎯 ANALYSIS: {'COMPLETE' if overall_success else 'FAILED'}")
    exit(0 if overall_success else 1) 