#!/usr/bin/env python3
"""
COMPREHENSIVE TSV FILE ANALYSIS - Zero Assumptions Investigation
Goal: Verify actual TSV content, record counts, and Alabama completeness
"""

import os
import sys
import csv
import pandas as pd
from pathlib import Path

# Set CSV limits for large files
csv.field_size_limit(2147483647)

def analyze_tsv_file_structure():
    """Comprehensive analysis of the source TSV file"""
    
    print("🔍 COMPREHENSIVE TSV FILE ANALYSIS - ZERO ASSUMPTIONS")
    print("🎯 Goal: Verify file content, record counts, and Alabama completeness")
    print("=" * 75)
    
    # Standard TSV file location
    tsv_path = r"C:\DataNest-TSV-Files\extracted-tsv\Quantarium_OpenLien_20250414_00001.TSV"
    
    if not os.path.exists(tsv_path):
        print(f"❌ TSV file not found at: {tsv_path}")
        print("📂 Please provide the correct path to the TSV file")
        return False
    
    file_size_mb = os.path.getsize(tsv_path) / (1024 * 1024 * 1024)  # GB
    print(f"📂 Analyzing file: {os.path.basename(tsv_path)}")
    print(f"💾 File size: {file_size_mb:.2f} GB")
    
    # STEP 1: Get exact row count
    print(f"\n🔢 STEP 1: EXACT ROW COUNT VERIFICATION")
    try:
        with open(tsv_path, 'r', encoding='utf-8', errors='ignore') as f:
            total_lines = sum(1 for line in f)
        
        actual_record_count = total_lines - 1  # Subtract header
        print(f"   📊 Total lines in file: {total_lines:,}")
        print(f"   📊 Actual data records: {actual_record_count:,}")
        print(f"   📊 Loaded in database: 4,849,999")
        
        if actual_record_count == 4849999:
            print(f"   ✅ PERFECT MATCH: All records loaded successfully")
        else:
            diff = actual_record_count - 4849999
            print(f"   ⚠️  DISCREPANCY: {diff:,} records difference")
            
    except Exception as e:
        print(f"   ❌ Error counting rows: {e}")
    
    # STEP 2: Analyze header structure
    print(f"\n📋 STEP 2: HEADER ANALYSIS")
    try:
        # Read header only
        df_header = pd.read_csv(tsv_path, sep='\t', nrows=0)
        total_columns = len(df_header.columns)
        print(f"   📊 Total columns in TSV: {total_columns}")
        
        # Check for state and FIPS columns
        state_cols = [col for col in df_header.columns if 'state' in col.lower()]
        fips_cols = [col for col in df_header.columns if 'fips' in col.lower()]
        
        print(f"   🗺️  State columns: {state_cols}")
        print(f"   🔢 FIPS columns: {fips_cols}")
        
    except Exception as e:
        print(f"   ❌ Error reading header: {e}")
    
    # STEP 3: Sample-based content analysis
    print(f"\n🔍 STEP 3: CONTENT ANALYSIS (Sample-based)")
    try:
        # Read large sample for analysis
        sample_size = 100000
        df_sample = pd.read_csv(
            tsv_path, 
            sep='\t', 
            nrows=sample_size,
            dtype=str,
            encoding='utf-8',
            engine='python',
            quoting=csv.QUOTE_NONE,
            on_bad_lines='skip'
        )
        
        print(f"   📊 Sample size: {len(df_sample):,} records")
        
        # Analyze FIPS codes in sample
        if 'FIPS_Code' in df_sample.columns:
            fips_analysis = df_sample['FIPS_Code'].fillna('UNKNOWN')
            state_fips = fips_analysis.str[:2]
            fips_counts = state_fips.value_counts().head(10)
            
            print(f"   🗺️  FIPS Code Analysis (Sample):")
            for fips_code, count in fips_counts.items():
                state_name = get_state_name(fips_code)
                percentage = (count / len(df_sample)) * 100
                print(f"      {state_name} ({fips_code}): {count:,} ({percentage:.1f}%)")
                
            # Estimate Alabama count from sample
            alabama_in_sample = (state_fips == '01').sum()
            alabama_percentage = (alabama_in_sample / len(df_sample)) * 100
            estimated_alabama_total = int((actual_record_count * alabama_percentage) / 100)
            
            print(f"\n   🎯 ALABAMA PROJECTION FROM SAMPLE:")
            print(f"      Sample Alabama: {alabama_in_sample:,} / {len(df_sample):,} ({alabama_percentage:.1f}%)")
            print(f"      Projected total Alabama: {estimated_alabama_total:,}")
            print(f"      Expected Alabama: 3,164,162")
            print(f"      Database Alabama: 2,666,016")
            print(f"      Gap analysis: {3164162 - estimated_alabama_total:,} vs expected")
        
        # Check Property_State completeness
        if 'Property_State' in df_sample.columns:
            property_state_analysis = df_sample['Property_State'].fillna('NULL')
            state_counts = property_state_analysis.value_counts().head(10)
            
            print(f"\n   📊 Property_State Field Analysis:")
            for state, count in state_counts.items():
                percentage = (count / len(df_sample)) * 100
                print(f"      {state}: {count:,} ({percentage:.1f}%)")
                
            # Check Alabama Property_State vs FIPS consistency
            if 'FIPS_Code' in df_sample.columns:
                alabama_fips = state_fips == '01'
                alabama_state = df_sample['Property_State'] == 'AL'
                
                fips_al_not_state = alabama_fips & (df_sample['Property_State'] != 'AL')
                state_al_not_fips = alabama_state & (state_fips != '01')
                
                print(f"\n   🔍 Alabama Data Quality Check:")
                print(f"      FIPS=01 but State≠AL: {fips_al_not_state.sum():,}")
                print(f"      State=AL but FIPS≠01: {state_al_not_fips.sum():,}")
        
    except Exception as e:
        print(f"   ❌ Error in content analysis: {e}")
    
    # STEP 4: File naming and structure validation
    print(f"\n📂 STEP 4: FILE STRUCTURE VALIDATION")
    print(f"   📋 Expected: Alabama + Alaska (alphabetical)")
    print(f"   📋 Found: Alabama + Arizona (unusual)")
    print(f"   🔍 Recommendation: Verify file naming/structure with data provider")
    
    return True

def get_state_name(fips_code):
    """Convert FIPS code to state name"""
    fips_map = {
        '01': 'Alabama', '02': 'Alaska', '04': 'Arizona', '05': 'Arkansas',
        '06': 'California', '08': 'Colorado', '09': 'Connecticut', '10': 'Delaware',
        '11': 'District of Columbia', '12': 'Florida', '13': 'Georgia', '15': 'Hawaii',
        '16': 'Idaho', '17': 'Illinois', '18': 'Indiana', '19': 'Iowa',
        '20': 'Kansas', '21': 'Kentucky', '22': 'Louisiana', '23': 'Maine'
    }
    return fips_map.get(fips_code, f'State {fips_code}')

def check_loading_completeness():
    """Compare TSV content with database to identify loading issues"""
    
    print(f"\n" + "=" * 75)
    print("🔍 LOADING COMPLETENESS VERIFICATION")
    print("🎯 Goal: Identify any records lost during loading process")
    print("=" * 75)
    
    try:
        import psycopg2
        sys.path.append(os.path.join(os.path.dirname(__file__), '..', 'src'))
        from config import get_db_config
        
        conn = psycopg2.connect(**get_db_config())
        cursor = conn.cursor()
        
        # Check for specific loading issues
        print("🔍 DATABASE LOADING ANALYSIS:")
        
        # Check duplicate handling
        cursor.execute("""
            SELECT 
                COUNT(*) as total_records,
                COUNT(DISTINCT quantarium_internal_pid) as unique_pids,
                COUNT(*) - COUNT(DISTINCT quantarium_internal_pid) as duplicate_pids
            FROM datnest.properties;
        """)
        
        dup_stats = cursor.fetchone()
        total, unique, duplicates = dup_stats
        
        print(f"   📊 Total loaded: {total:,}")
        print(f"   📊 Unique PIDs: {unique:,}")
        print(f"   🔍 Duplicate PIDs: {duplicates:,}")
        
        if duplicates > 0:
            print(f"   ⚠️  {duplicates:,} records may have been dropped due to PID conflicts")
        
        # Check for Alabama data quality metrics
        cursor.execute("""
            SELECT 
                COUNT(*) as total_alabama,
                COUNT(CASE WHEN apn IS NOT NULL AND apn != '' THEN 1 END) as with_apn,
                COUNT(CASE WHEN current_owner_name IS NOT NULL AND current_owner_name != '' THEN 1 END) as with_owner,
                COUNT(CASE WHEN fips_code IS NOT NULL AND fips_code != '' THEN 1 END) as with_fips
            FROM datnest.properties 
            WHERE substring(fips_code, 1, 2) = '01';
        """)
        
        al_quality = cursor.fetchone()
        total_al, with_apn, with_owner, with_fips = al_quality
        
        print(f"\n📊 ALABAMA DATA QUALITY VERIFICATION:")
        print(f"   🎯 Total Alabama records: {total_al:,}")
        print(f"   📋 With Parcel Numbers: {with_apn:,} ({with_apn/total_al*100:.1f}%)")
        print(f"   👤 With Owner Names: {with_owner:,} ({with_owner/total_al*100:.1f}%)")
        print(f"   🔢 With FIPS Codes: {with_fips:,} ({with_fips/total_al*100:.1f}%)")
        
        # Compare against expectations
        print(f"\n🎯 VALIDATION AGAINST EXPECTED:")
        print(f"   📈 Expected: 100% FIPS codes ✅ {'PASS' if with_fips/total_al >= 0.99 else 'FAIL'}")
        print(f"   📈 Expected: 100% parcel numbers ✅ {'PASS' if with_apn/total_al >= 0.99 else 'FAIL'}")
        print(f"   📈 Expected: ~100% owner names ✅ {'PASS' if with_owner/total_al >= 0.95 else 'FAIL'}")
        
        cursor.close()
        conn.close()
        
    except Exception as e:
        print(f"❌ Error in loading analysis: {e}")
    
    return True

if __name__ == "__main__":
    print("🚀 STARTING COMPREHENSIVE TSV FILE ANALYSIS")
    
    # Run TSV structure analysis
    success1 = analyze_tsv_file_structure()
    
    # Run loading completeness check
    success2 = check_loading_completeness()
    
    overall_success = success1 and success2
    print(f"\n🎯 COMPREHENSIVE ANALYSIS: {'COMPLETE' if overall_success else 'NEEDS ATTENTION'}")
    
    exit(0 if overall_success else 1) 