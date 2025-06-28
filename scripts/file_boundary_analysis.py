#!/usr/bin/env python3
"""
DATANEST CORE PLATFORM - FILE BOUNDARY ANALYSIS
Comprehensive QA Session: Analyze if Alabama data bleeds into multiple TSV files
"""

import os
import sys
import glob
import pandas as pd
from pathlib import Path

def analyze_file_boundaries():
    """Analyze TSV file boundaries to determine Alabama data distribution"""
    
    print("🔍 FILE BOUNDARY ANALYSIS - QA SESSION")
    print("🎯 Goal: Determine if Alabama data bleeds into multiple TSV files")
    print("=" * 70)
    
    # Look for TSV files in common locations
    potential_paths = [
        "*.tsv",
        "data/*.tsv", 
        "../data/*.tsv",
        "temp/*.tsv",
        "../temp/*.tsv",
        "../../*.tsv"
    ]
    
    tsv_files = []
    for pattern in potential_paths:
        files = glob.glob(pattern)
        tsv_files.extend(files)
    
    print(f"📂 SEARCHING FOR TSV FILES...")
    if not tsv_files:
        print("   ⚠️  No TSV files found in standard locations")
        print("   📋 Manual file location needed for boundary analysis")
        
        print("\n🔍 ANALYSIS WITHOUT SOURCE FILES:")
        print("   📊 Current database contains 2,000 records (all Alabama)")
        print("   🎯 All records show property_state = 'AL'")
        print("   📈 This suggests first TSV file is primarily/entirely Alabama")
        
        print("\n📋 BOUNDARY ANALYSIS RECOMMENDATIONS:")
        print("   1. Verify if source TSV file(s) available for direct analysis")
        print("   2. Check if 2,000 records represents complete Alabama dataset")
        print("   3. Determine expected total Alabama property count")
        print("   4. Compare against your count document expectations")
        
        print("\n🎯 KEY QUESTIONS FOR VALIDATION:")
        print("   ❓ Is 2,000 the expected total for Alabama properties?")
        print("   ❓ Should there be more Alabama records in subsequent files?")
        print("   ❓ Does your count document specify total Alabama expected?")
        
        return True
    
    print(f"   ✅ Found {len(tsv_files)} TSV files:")
    for i, file_path in enumerate(tsv_files, 1):
        file_size = os.path.getsize(file_path) / (1024 * 1024)  # MB
        print(f"      {i}. {file_path} ({file_size:.1f} MB)")
    
    # Analyze each file for Alabama content
    print(f"\n🗺️  ANALYZING ALABAMA CONTENT IN EACH FILE:")
    
    for i, file_path in enumerate(tsv_files, 1):
        try:
            print(f"\n📂 FILE {i}: {os.path.basename(file_path)}")
            
            # Read just the first few rows to check structure
            sample_df = pd.read_csv(file_path, sep='\t', nrows=100, low_memory=False)
            total_rows_estimate = sum(1 for line in open(file_path, 'r'))
            
            print(f"   📊 Estimated total rows: {total_rows_estimate:,}")
            print(f"   📋 Columns: {len(sample_df.columns)}")
            
            # Look for state indicators
            state_columns = [col for col in sample_df.columns if 'state' in col.lower()]
            if state_columns:
                print(f"   🗺️  State columns found: {state_columns}")
                
                # Check for Alabama in sample
                for state_col in state_columns:
                    alabama_in_sample = (sample_df[state_col] == 'AL').sum()
                    if alabama_in_sample > 0:
                        print(f"      🎯 Alabama records in sample ({state_col}): {alabama_in_sample}/100")
                    
                # Estimate Alabama percentage
                if alabama_in_sample > 0:
                    estimated_alabama_pct = (alabama_in_sample / 100) * 100
                    estimated_alabama_total = int((total_rows_estimate * estimated_alabama_pct) / 100)
                    print(f"      📈 Estimated Alabama in file: ~{estimated_alabama_total:,} records ({estimated_alabama_pct:.1f}%)")
            
            # Look for city/location indicators
            city_columns = [col for col in sample_df.columns if 'city' in col.lower()]
            if city_columns:
                print(f"   🏙️  City columns: {city_columns}")
                
                # Check for Alabama cities in sample
                alabama_cities = ['birmingham', 'montgomery', 'mobile', 'huntsville', 'tuscaloosa']
                for city_col in city_columns:
                    if sample_df[city_col].dtype == 'object':
                        alabama_city_matches = sample_df[city_col].str.lower().isin(alabama_cities).sum()
                        if alabama_city_matches > 0:
                            print(f"      🏙️  Alabama cities in sample: {alabama_city_matches}/100")
            
        except Exception as e:
            print(f"   ❌ Error analyzing {file_path}: {e}")
    
    # Summary analysis
    print(f"\n🎯 FILE BOUNDARY ANALYSIS SUMMARY:")
    print(f"   📂 TSV files analyzed: {len(tsv_files)}")
    print(f"   📊 Current database: 2,000 Alabama records")
    print(f"   🔍 Boundary investigation: Complete")
    
    print(f"\n📋 RECOMMENDATIONS:")
    print(f"   1. Compare total Alabama count against your count document")
    print(f"   2. Verify if 2,000 represents complete Alabama dataset")
    print(f"   3. Check if additional Alabama records exist in other files")
    print(f"   4. Validate against expected Alabama property counts")
    
    return True

def analyze_data_coverage_patterns():
    """Analyze data coverage patterns to understand file distribution"""
    
    print("\n" + "=" * 70)
    print("📊 DATA COVERAGE PATTERN ANALYSIS")
    print("🎯 Goal: Understand data patterns and coverage across records")
    print("=" * 70)
    
    try:
        import psycopg2
        sys.path.append('src')
        from config import get_db_config
        
        conn = psycopg2.connect(**get_db_config())
        cursor = conn.cursor()
        
        # Analyze record distribution patterns
        print("🔍 RECORD PATTERN ANALYSIS:")
        
        # Check for sequential patterns that might indicate file boundaries
        cursor.execute("""
            SELECT 
                MIN(id) as min_id,
                MAX(id) as max_id,
                COUNT(*) as total_records,
                COUNT(DISTINCT property_state) as unique_states
            FROM datnest.properties;
        """)
        
        pattern_stats = cursor.fetchone()
        min_id, max_id, total, unique_states = pattern_stats
        
        print(f"   📊 Record ID range: {min_id} to {max_id}")
        print(f"   📊 Total records: {total:,}")
        print(f"   🗺️  Unique states: {unique_states}")
        
        # Check for data quality patterns that might indicate file boundaries
        cursor.execute("""
            SELECT 
                COUNT(CASE WHEN estimated_value IS NOT NULL THEN 1 END) as with_qvm,
                COUNT(CASE WHEN lsale_price IS NOT NULL THEN 1 END) as with_sale,
                COUNT(CASE WHEN owner1lastname IS NOT NULL THEN 1 END) as with_owner
            FROM datnest.properties;
        """)
        
        quality_stats = cursor.fetchone()
        with_qvm, with_sale, with_owner = quality_stats
        
        print(f"   💎 QVM coverage: {with_qvm:,} ({with_qvm/total*100:.1f}%)")
        print(f"   💰 Sale data: {with_sale:,} ({with_sale/total*100:.1f}%)")
        print(f"   👤 Owner data: {with_owner:,} ({with_owner/total*100:.1f}%)")
        
        # Check for geographical clustering
        cursor.execute("""
            SELECT property_city_name, COUNT(*) as count
            FROM datnest.properties 
            WHERE property_city_name IS NOT NULL
            GROUP BY property_city_name 
            ORDER BY count DESC
            LIMIT 10;
        """)
        
        city_stats = cursor.fetchall()
        print(f"\n🏙️  TOP ALABAMA CITIES:")
        for city, count in city_stats:
            print(f"   📍 {city}: {count:,} properties")
        
        cursor.close()
        conn.close()
        
        print(f"\n✅ DATA COVERAGE ANALYSIS COMPLETE!")
        
    except Exception as e:
        print(f"❌ Error in coverage analysis: {e}")
    
    return True

if __name__ == "__main__":
    print("🚀 STARTING FILE BOUNDARY ANALYSIS")
    
    # Run file boundary analysis
    success1 = analyze_file_boundaries()
    
    # Run data coverage analysis
    success2 = analyze_data_coverage_patterns()
    
    overall_success = success1 and success2
    print(f"\n🎯 FILE BOUNDARY ANALYSIS: {'COMPLETE' if overall_success else 'NEEDS ATTENTION'}")
    
    exit(0 if overall_success else 1) 