#!/usr/bin/env python3
"""
Analyze Database Schema vs Working Fields
Explains the difference between total database columns and mapped working fields
"""

import psycopg2
import sys
import os

# Add src to path for imports
sys.path.append(os.path.join(os.path.dirname(__file__), '..'))

from src.config import get_db_config

def analyze_schema_vs_working():
    """Analyze difference between database columns and working fields"""
    
    print("🔍 DATABASE SCHEMA vs WORKING FIELDS ANALYSIS")
    print("=" * 60)
    
    try:
        conn = psycopg2.connect(**get_db_config())
        cursor = conn.cursor()
        cursor.execute("SET search_path TO datnest, public")
        
        # Get all database columns
        cursor.execute("""
            SELECT column_name, data_type, is_nullable
            FROM information_schema.columns 
            WHERE table_name = 'properties' AND table_schema = 'datnest'
            ORDER BY ordinal_position
        """)
        
        all_columns = cursor.fetchall()
        db_column_names = [col[0] for col in all_columns]
        
        print(f"📊 TOTAL DATABASE COLUMNS: {len(all_columns)}")
        
        # Our 29 working fields (the ones we actively map from TSV)
        working_fields = [
            'quantarium_internal_pid', 'apn', 'fips_code', 'estimated_value', 'price_range_max', 
            'price_range_min', 'confidence_score', 'qvm_asof_date', 'qvm_value_range_code',
            'property_full_street_address', 'property_city_name', 'property_state', 
            'property_zip_code', 'latitude', 'longitude', 'building_area_total',
            'lot_size_square_feet', 'number_of_bedrooms', 'number_of_bathrooms', 'year_built',
            'total_assessed_value', 'assessment_year', 'standardized_land_use_code', 'style',
            'zoning', 'owner_occupied', 'current_owner_name', 'building_quality', 'building_condition'
        ]
        
        print(f"🎯 OUR WORKING FIELDS: {len(working_fields)}")
        print()
        
        # Check which working fields exist in database
        working_in_db = []
        working_missing = []
        
        for field in working_fields:
            if field in db_column_names:
                working_in_db.append(field)
            else:
                working_missing.append(field)
        
        print(f"✅ WORKING FIELDS STATUS:")
        print(f"  • In database: {len(working_in_db)}/{len(working_fields)}")
        if working_missing:
            print(f"  • Missing: {working_missing}")
        
        # Find extra columns (in database but not in our working set)
        extra_columns = [col for col in db_column_names if col not in working_fields]
        
        print(f"\n🔍 EXTRA DATABASE COLUMNS: {len(extra_columns)}")
        print("   (Columns that exist in database but we don't actively use)")
        
        # Categorize extra columns
        system_columns = [col for col in extra_columns if col in ['id', 'created_at', 'updated_at']]
        previous_attempt_columns = []
        potential_future_columns = []
        
        for col in extra_columns:
            if any(keyword in col.lower() for keyword in ['mtg', 'mortgage', 'lien', 'sale', 'prior', 'last']):
                previous_attempt_columns.append(col)
            else:
                potential_future_columns.append(col)
        
        if system_columns:
            print(f"\n  📋 System/Metadata Columns ({len(system_columns)}):")
            for col in system_columns:
                print(f"    • {col}")
        
        if previous_attempt_columns:
            print(f"\n  ⚠️  Previous Engineer Attempts ({len(previous_attempt_columns)}):")
            print("     (Likely from failed schema additions)")
            for col in previous_attempt_columns[:10]:  # Show first 10
                print(f"    • {col}")
            if len(previous_attempt_columns) > 10:
                print(f"    ... and {len(previous_attempt_columns) - 10} more")
        
        if potential_future_columns:
            print(f"\n  🔮 Available for Future Mapping ({len(potential_future_columns)}):")
            for col in potential_future_columns[:10]:  # Show first 10
                print(f"    • {col}")
            if len(potential_future_columns) > 10:
                print(f"    ... and {len(potential_future_columns) - 10} more")
        
        print(f"\n📊 SUMMARY:")
        print(f"  • Total Database Columns: {len(all_columns)}")
        print(f"  • Our Working Fields: {len(working_fields)}")
        print(f"  • Actively Mapped Fields: {len(working_in_db)}")
        print(f"  • Unused Database Columns: {len(extra_columns)}")
        
        print(f"\n💡 EXPLANATION:")
        print(f"  The difference between {len(all_columns)} database columns and {len(working_fields)} working fields")
        print(f"  comes from previous schema additions that aren't actively mapped to TSV data.")
        print(f"  Our evidence-based approach focuses on fields we can actually populate with real data.")
        
        cursor.close()
        conn.close()
        
        return True
        
    except Exception as e:
        print(f"❌ Error: {e}")
        return False

if __name__ == "__main__":
    analyze_schema_vs_working() 