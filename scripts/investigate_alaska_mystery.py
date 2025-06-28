#!/usr/bin/env python3
"""
INVESTIGATE ALASKA MYSTERY
Goal: Find why Alaska (FIPS 02) is missing from database despite being in TSV
"""

import os
import sys
import psycopg2

# Add src directory to path  
sys.path.append(os.path.join(os.path.dirname(__file__), '..', 'src'))

from config import get_db_config

def investigate_alaska_mystery():
    """Investigate the missing Alaska records"""
    
    print("🔍 INVESTIGATING ALASKA MYSTERY")
    print("🎯 Goal: Find why Alaska (FIPS 02) missing from database")
    print("=" * 60)
    
    try:
        conn = psycopg2.connect(**get_db_config())
        cursor = conn.cursor()
        
        # Check for Alaska specifically
        print("📊 CHECKING FOR ALASKA IN DATABASE:")
        cursor.execute("""
            SELECT 
                substring(fips_code, 1, 2) as state_fips,
                COUNT(*) as count
            FROM datnest.properties 
            WHERE substring(fips_code, 1, 2) IN ('01', '02', '04')
            GROUP BY substring(fips_code, 1, 2)
            ORDER BY state_fips;
        """)
        
        fips_map = {'01': 'Alabama', '02': 'Alaska', '04': 'Arizona'}
        alaska_found = False
        
        results = cursor.fetchall()
        print("   Target states in database:")
        for fips, count in results:
            state_name = fips_map.get(fips, f'State {fips}')
            print(f"      {state_name} ({fips}): {count:,} records")
            if fips == '02':
                alaska_found = True
        
        if not alaska_found:
            print("   ❌ Alaska (FIPS 02) NOT FOUND in database!")
        
        # Check all FIPS codes
        print("\n📊 ALL FIPS CODES IN DATABASE:")
        cursor.execute("""
            SELECT 
                substring(fips_code, 1, 2) as state_fips,
                COUNT(*) as count
            FROM datnest.properties 
            GROUP BY substring(fips_code, 1, 2)
            ORDER BY count DESC;
        """)
        
        all_results = cursor.fetchall()
        for fips, count in all_results:
            state_name = fips_map.get(fips, f'State {fips}')
            print(f"      {state_name} ({fips}): {count:,} records")
        
        # Check against expected counts
        print("\n🎯 COMPARISON WITH EXPECTED COUNTS:")
        expected_counts = {
            '01': 3164162,  # Alabama
            '02': 380172,   # Alaska  
            '04': 3507109   # Arizona
        }
        
        loaded_counts = {fips: count for fips, count in results}
        
        for fips, expected in expected_counts.items():
            loaded = loaded_counts.get(fips, 0)
            state_name = fips_map[fips]
            status = "✅ LOADED" if loaded > 0 else "❌ MISSING"
            print(f"   {state_name}: Expected {expected:,}, Loaded {loaded:,} {status}")
            
            if loaded > 0:
                diff = expected - loaded
                pct_diff = (diff / expected) * 100
                print(f"      Gap: {diff:,} records ({pct_diff:.1f}%)")
        
        cursor.close()
        conn.close()
        
        return True
        
    except Exception as e:
        print(f"❌ Error: {e}")
        return False

def check_second_tsv_file():
    """Check if second TSV file exists and analyze its structure"""
    
    print("\n" + "=" * 60)
    print("📂 CHECKING SECOND TSV FILE")
    print("🎯 Goal: Understand multi-file structure")
    print("=" * 60)
    
    # Standard location for second file
    tsv_path2 = r"C:\DataNest-TSV-Files\extracted-tsv\Quantarium_OpenLien_20250414_00002.TSV"
    
    if os.path.exists(tsv_path2):
        file_size_gb = os.path.getsize(tsv_path2) / (1024 * 1024 * 1024)
        print(f"✅ Second TSV file found!")
        print(f"   📂 File: {os.path.basename(tsv_path2)}")
        print(f"   💾 Size: {file_size_gb:.2f} GB")
        
        # Quick analysis of second file
        try:
            import pandas as pd
            import csv
            csv.field_size_limit(2147483647)
            
            # Sample beginning of second file
            df_sample = pd.read_csv(
                tsv_path2,
                sep='\t',
                nrows=10000,
                dtype=str,
                encoding='utf-8',
                engine='python',
                quoting=csv.QUOTE_NONE,
                on_bad_lines='skip'
            )
            
            if 'FIPS_Code' in df_sample.columns:
                fips_codes = df_sample['FIPS_Code'].fillna('UNKNOWN').str[:2]
                fips_counts = fips_codes.value_counts().head(5)
                
                print(f"\n   🔍 Second file content (first 10K records):")
                fips_map = {'01': 'Alabama', '02': 'Alaska', '04': 'Arizona', '05': 'Arkansas', '06': 'California'}
                for fips, count in fips_counts.items():
                    state_name = fips_map.get(fips, f'State {fips}')
                    pct = (count / len(df_sample)) * 100
                    print(f"      {state_name} ({fips}): {count:,} ({pct:.1f}%)")
            
        except Exception as e:
            print(f"   ❌ Error analyzing second file: {e}")
            
    else:
        print(f"❌ Second TSV file not found at: {tsv_path2}")
        print("   📂 Please provide correct path or check file naming")
        
        # Check for any other TSV files
        tsv_dir = os.path.dirname(tsv_path2)
        if os.path.exists(tsv_dir):
            tsv_files = [f for f in os.listdir(tsv_dir) if f.endswith('.TSV')]
            if tsv_files:
                print(f"\n   📂 Other TSV files found in directory:")
                for tsv_file in sorted(tsv_files):
                    print(f"      {tsv_file}")
    
    return True

def generate_recommendations():
    """Generate next steps based on findings"""
    
    print("\n" + "=" * 60)
    print("🎯 RECOMMENDATIONS")
    print("=" * 60)
    
    print("📋 IMMEDIATE ACTIONS NEEDED:")
    print("   1. 🔍 Investigate why Alaska records were not loaded")
    print("   2. 📂 Analyze second TSV file structure")
    print("   3. 🔧 Check loader field mapping for Alaska FIPS codes")
    print("   4. 📊 Validate total record counts against expectations")
    
    print("\n🚨 CRITICAL QUESTIONS:")
    print("   ❓ Why is Alaska (FIPS 02) missing from database?")
    print("   ❓ Are we filtering out certain FIPS codes?")
    print("   ❓ Is there an issue with our loader logic?")
    print("   ❓ Does the second file start with remaining Arizona records?")
    
    print("\n⚠️  DO NOT PROCEED TO NATIONAL DEPLOYMENT until:")
    print("   ✅ Alaska mystery resolved")
    print("   ✅ All expected states accounted for")
    print("   ✅ Multi-file pattern understood")
    print("   ✅ Loading completeness validated")

if __name__ == "__main__":
    print("🚀 STARTING ALASKA MYSTERY INVESTIGATION")
    
    success1 = investigate_alaska_mystery()
    success2 = check_second_tsv_file()
    generate_recommendations()
    
    overall_success = success1 and success2
    print(f"\n🎯 INVESTIGATION: {'COMPLETE' if overall_success else 'FAILED'}")
    exit(0 if overall_success else 1) 