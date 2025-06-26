#!/usr/bin/env python3
"""
MEGA BATCH 2B: COMPLETE BUILDING + LAND CATEGORIES
STRATEGY: Complete entire data categories for business intelligence organization
GOAL: Cross off Building Characteristics + Land Characteristics categories (54 → 90+ fields)
"""

import psycopg2
import sys
import os

# Add src to path for imports
sys.path.append(os.path.join(os.path.dirname(__file__), '..'))

from src.config import get_db_config

def mega_batch_complete_categories():
    """Complete Building Characteristics and Land Characteristics categories"""
    
    print("🔥 MEGA BATCH 2B: COMPLETE BUILDING + LAND CATEGORIES")
    print("=" * 70)
    
    # Define columns to COMPLETE categories
    columns_to_add = [
        # 🏗️ BUILDING CHARACTERISTICS - COMPLETE THE CATEGORY
        ("pool", "VARCHAR(1)", "Pool indicator (Y/N)"),
        ("air_conditioning", "VARCHAR(1)", "Air conditioning indicator"),
        ("air_conditioning_type", "VARCHAR(1)", "Type of AC system"),
        ("fireplace", "VARCHAR(1)", "Fireplace indicator"),
        ("basement", "VARCHAR(1)", "Basement indicator"),
        ("elevator", "VARCHAR(1)", "Elevator indicator"),
        ("number_of_partial_baths", "INTEGER", "Number of partial bathrooms"),
        ("number_of_units", "INTEGER", "Number of units in building"),
        ("number_of_stories", "VARCHAR(10)", "Number of stories"),
        ("number_of_buildings", "INTEGER", "Number of buildings on property"),
        ("total_number_of_rooms", "VARCHAR(2)", "Total number of rooms"),
        ("exterior_walls", "VARCHAR(1)", "Exterior wall material code"),
        ("roof_cover", "VARCHAR(1)", "Roof cover material code"),
        ("roof_type", "VARCHAR(1)", "Roof type code"),
        ("foundation", "VARCHAR(1)", "Foundation type code"),
        ("heating", "VARCHAR(1)", "Heating system code"),
        ("heating_fuel_type", "VARCHAR(1)", "Heating fuel type code"),
        ("interior_walls", "VARCHAR(1)", "Interior wall material code"),
        ("floor_cover", "VARCHAR(2)", "Floor covering type code"),
        ("water", "VARCHAR(1)", "Water source code"),
        ("sewer", "VARCHAR(1)", "Sewer system code"),
        ("type_construction", "VARCHAR(1)", "Construction type code"),
        ("garage_type", "VARCHAR(1)", "Garage type code"),
        ("amenities", "VARCHAR(5)", "Property amenities codes"),
        ("amenities_2", "VARCHAR(5)", "Additional amenities codes"),
        
        # 🌍 LAND CHARACTERISTICS - COMPLETE THE CATEGORY  
        ("lot_size_acres", "DECIMAL(10,4)", "Lot size in acres"),
        ("lot_size_depth_feet", "DECIMAL(10,2)", "Lot depth in feet"),
        ("lot_size_frontage_feet", "DECIMAL(10,2)", "Lot frontage in feet"),
        ("lot_size_or_area", "DECIMAL(14,4)", "Lot size or area (various units)"),
        ("lot_size_area_unit", "VARCHAR(2)", "Unit of measurement for lot size"),
        ("original_lot_size_or_area", "VARCHAR(14)", "Original lot size before subdivision"),
        ("topography", "VARCHAR(1)", "Topography code"),
        ("site_influence", "VARCHAR(2)", "Site influence factors code"),
        
        # 🎯 HIGH-VALUE BONUS FIELDS (Business critical)
        ("owner1_first_name", "VARCHAR(166)", "Primary owner first name"),
        ("owner1_last_name", "VARCHAR(166)", "Primary owner last name"),
        ("owner2_first_name", "VARCHAR(166)", "Secondary owner first name"),
        ("owner2_last_name", "VARCHAR(166)", "Secondary owner last name"),
        ("co_mailing_city", "VARCHAR(30)", "Owner mailing city"),
        ("co_mailing_state", "VARCHAR(2)", "Owner mailing state"),
        ("co_mailing_zip_code", "VARCHAR(5)", "Owner mailing zip code"),
        ("length_of_residence_months", "INTEGER", "Months current owner has owned property"),
    ]
    
    try:
        conn = psycopg2.connect(**get_db_config())
        cursor = conn.cursor()
        cursor.execute("SET search_path TO datnest, public")
        
        print("🏗️ CATEGORY COMPLETION ANALYSIS:")
        print(f"   • Building Characteristics: 25 fields (COMPLETE CATEGORY)")
        print(f"   • Land Characteristics: 8 fields (COMPLETE CATEGORY)")
        print(f"   • Ownership Intelligence: 7 fields (enhance category)")
        print(f"   • TOTAL TARGET: {len(columns_to_add)} new fields for category completion")
        print()
        
        success_count = 0
        for column_name, data_type, description in columns_to_add:
            try:
                sql = f"ALTER TABLE properties ADD COLUMN IF NOT EXISTS {column_name} {data_type};"
                cursor.execute(sql)
                conn.commit()
                print(f"✅ Added: {column_name} ({data_type}) - {description}")
                success_count += 1
            except Exception as e:
                print(f"❌ Failed: {column_name} - {str(e)}")
        
        print()
        print("🎯 MEGA BATCH CATEGORY COMPLETION RESULTS:")
        print(f"   ✅ Successfully added: {success_count}/{len(columns_to_add)} columns")
        print(f"   🏗️ Building Characteristics: TARGET COMPLETE")
        print(f"   🌍 Land Characteristics: TARGET COMPLETE") 
        print(f"   👤 Ownership Intelligence: ENHANCED")
        print(f"   🚀 Ready for mega batch field mapping")
        
        # Verify final column count
        cursor.execute("""
            SELECT COUNT(*) 
            FROM information_schema.columns 
            WHERE table_name = 'properties' AND table_schema = 'datnest'
        """)
        total_columns = cursor.fetchone()[0]
        print(f"   📊 Total database columns: {total_columns}")
        
        cursor.close()
        conn.close()
        
        if success_count == len(columns_to_add):
            print()
            print("🔥 MEGA BATCH 2B: CATEGORY COMPLETION READY!")
            print("   ✅ Building Characteristics: READY TO COMPLETE")
            print("   ✅ Land Characteristics: READY TO COMPLETE")
            print("   🎯 Business Value: Complete property intelligence domains")
            return True
        else:
            print()
            print("⚠️  PARTIAL SUCCESS: Some columns may need manual review")
            return False
            
    except Exception as e:
        print(f"❌ Database connection error: {str(e)}")
        return False

if __name__ == "__main__":
    success = mega_batch_complete_categories()
    if success:
        print("\n🚀 Next step: Add mega batch field mappings and validate")
        print("🎯 Goal: Cross off Building + Land categories as COMPLETE")
    else:
        print("\n⚠️  Review any failed columns before proceeding") 