#!/usr/bin/env python3
"""
ALABAMA RECORD INVESTIGATION - Zero Assumptions Analysis
Investigate the 3.1M expected vs 1.75M found Alabama discrepancy
"""

import os
import sys
import psycopg2

# Add src directory to path  
sys.path.append(os.path.join(os.path.dirname(__file__), '..', 'src'))

from config import get_db_config

def investigate_alabama_records():
    """Comprehensive Alabama record investigation"""
    
    print("🔍 ALABAMA RECORD INVESTIGATION - ZERO ASSUMPTIONS")
    print("🎯 Goal: Find the missing ~1.35M Alabama records")
    print("=" * 70)
    
    try:
        conn = psycopg2.connect(**get_db_config())
        cursor = conn.cursor()
        
        # Total record count
        cursor.execute("SELECT COUNT(*) FROM datnest.properties;")
        total_records = cursor.fetchone()[0]
        print(f"📊 Total records in database: {total_records:,}")
        
        print("\n🗺️  FIPS CODE ANALYSIS (Alabama = 01xxxx):")
        
        # Check FIPS codes for Alabama (should start with '01')
        cursor.execute("""
            SELECT 
                substring(fips_code, 1, 2) as state_fips,
                COUNT(*) as count,
                COUNT(CASE WHEN property_state = 'AL' THEN 1 END) as with_al_state,
                COUNT(CASE WHEN property_state IS NULL THEN 1 END) as null_state
            FROM datnest.properties 
            WHERE fips_code IS NOT NULL
            GROUP BY substring(fips_code, 1, 2)
            ORDER BY count DESC
            LIMIT 10;
        """)
        
        fips_results = cursor.fetchall()
        alabama_by_fips = 0
        
        for state_fips, count, with_al, null_state in fips_results:
            if state_fips == '01':
                alabama_by_fips = count
                print(f"   🎯 Alabama (01): {count:,} records ({with_al:,} marked 'AL', {null_state:,} NULL)")
            elif count > 10000:  # Show significant states
                print(f"   📍 State {state_fips}: {count:,} records")
        
        print(f"\n🔍 ALABAMA DETAILED BREAKDOWN:")
        
        # Alabama by FIPS - detailed breakdown
        cursor.execute("""
            SELECT 
                property_state,
                COUNT(*) as count,
                ROUND(COUNT(*) * 100.0 / SUM(COUNT(*)) OVER(), 1) as percentage
            FROM datnest.properties 
            WHERE substring(fips_code, 1, 2) = '01'
            GROUP BY property_state
            ORDER BY count DESC;
        """)
        
        alabama_breakdown = cursor.fetchall()
        total_alabama_fips = sum(row[1] for row in alabama_breakdown)
        
        print(f"   📊 Total Alabama by FIPS code: {total_alabama_fips:,}")
        for state, count, pct in alabama_breakdown:
            state_label = f"'{state}'" if state else 'NULL'
            print(f"   📋 property_state = {state_label}: {count:,} ({pct}%)")
        
        # Check if this matches our expected 3.1M
        expected_alabama = 3100000  # Approximate expected count
        print(f"\n🎯 COMPARISON WITH EXPECTED:")
        print(f"   📈 Expected Alabama records: ~{expected_alabama:,}")
        print(f"   📊 Found Alabama records (FIPS): {total_alabama_fips:,}")
        print(f"   📊 Found with state='AL': {1750000:,}")
        print(f"   🔍 Difference: {expected_alabama - total_alabama_fips:,}")
        
        if abs(total_alabama_fips - expected_alabama) < 200000:  # Within 200K tolerance
            print(f"   ✅ MATCH! Alabama count via FIPS closely matches expected")
        else:
            print(f"   ⚠️  Significant difference - need further investigation")
        
        # Check for other potential Alabama indicators
        print(f"\n🔍 ALTERNATIVE ALABAMA IDENTIFICATION:")
        
        # Check city names
        cursor.execute("""
            SELECT COUNT(*) 
            FROM datnest.properties 
            WHERE property_city_name ILIKE '%birmingham%' 
               OR property_city_name ILIKE '%montgomery%'
               OR property_city_name ILIKE '%mobile%'
               OR property_city_name ILIKE '%huntsville%';
        """)
        
        alabama_cities = cursor.fetchone()[0]
        print(f"   🏙️  Major Alabama city names found: {alabama_cities:,}")
        
        # Generate recommendations
        print(f"\n🎯 INVESTIGATION RESULTS:")
        if total_alabama_fips >= 3000000:
            print(f"   ✅ SOLUTION FOUND: Use FIPS code (01xxxx) to identify ALL Alabama records")
            print(f"   📊 This gives us {total_alabama_fips:,} Alabama records vs {1750000:,} with state='AL'")
            print(f"   🔧 Recommendation: Update loaders to use FIPS for Alabama identification")
        else:
            print(f"   ⚠️  Still missing records - need to investigate TSV file directly")
            print(f"   🔍 Check raw TSV Property_State column for data quality issues")
        
        cursor.close()
        conn.close()
        
        return True
        
    except Exception as e:
        print(f"❌ Error during investigation: {e}")
        return False

if __name__ == "__main__":
    print("🚀 STARTING ALABAMA RECORD INVESTIGATION")
    success = investigate_alabama_records()
    print(f"\n🎯 INVESTIGATION: {'SUCCESS' if success else 'FAILED'}")
    exit(0 if success else 1) 