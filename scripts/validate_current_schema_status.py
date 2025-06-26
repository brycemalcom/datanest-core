#!/usr/bin/env python3
"""
Current Schema Status Validation
Check all fields after BATCH 3A, 3B, and 4A migrations
"""

import os
import sys

# Add src directory to path
sys.path.append(os.path.join(os.path.dirname(__file__), '..', 'src'))

import psycopg2
from config import get_db_config

def validate_current_schema_status():
    """Validate complete schema status after all batch migrations"""
    
    print("📊 CURRENT SCHEMA STATUS VALIDATION")
    print("🎯 Post BATCH 3A + 3B + 4A Migration Analysis")
    print("=" * 60)
    
    try:
        db_config = get_db_config()
        conn = psycopg2.connect(**db_config)
        cursor = conn.cursor()
        
        # Get all current columns
        cursor.execute("""
            SELECT column_name, data_type, character_maximum_length, is_nullable
            FROM information_schema.columns 
            WHERE table_name = 'properties' 
            AND table_schema = 'datnest'
            ORDER BY ordinal_position;
        """)
        
        all_columns = cursor.fetchall()
        total_columns = len(all_columns)
        
        print(f"📊 Total Database Columns: {total_columns}")
        print()
        
        # Categorize columns by batch
        batch_3a_fields = [
            'property_zip_plus4_code', 'property_house_number', 'property_street_direction_left',
            'property_street_name', 'property_street_suffix', 'property_street_direction_right',
            'property_unit_number', 'property_unit_type', 'pa_carrier_route', 'pa_census_tract',
            'match_code', 'location_code', 'owner1_middle_name', 'owner2_middle_name',
            'co_mail_care_of_name', 'co_mail_street_address', 'co_mailing_zip_plus4_code',
            'co_unit_number', 'co_unit_type', 'mail_care_of_name_indicator',
            'parsed_owner_source_code', 'buyer_id_code_1', 'buyer_vesting_code', 'length_of_residence_code'
        ]
        
        batch_3b_fields = ['ownership_start_date']
        
        batch_4a_fields = ['view', 'view_code', 'land_use_code', 'land_use_general', 'neighborhood_code', 'flood_zone']
        
        # Check each batch
        existing_columns = [col[0] for col in all_columns]
        
        print("🔍 BATCH FIELD VERIFICATION:")
        
        # BATCH 3A
        batch_3a_present = [f for f in batch_3a_fields if f in existing_columns]
        print(f"   📍 BATCH 3A (Location + Ownership): {len(batch_3a_present)}/24 = {len(batch_3a_present)/24*100:.0f}%")
        if len(batch_3a_present) < 24:
            missing_3a = [f for f in batch_3a_fields if f not in existing_columns]
            print(f"      Missing: {missing_3a}")
        
        # BATCH 3B  
        batch_3b_present = [f for f in batch_3b_fields if f in existing_columns]
        print(f"   👤 BATCH 3B (Ownership Perfection): {len(batch_3b_present)}/1 = {len(batch_3b_present)/1*100:.0f}%")
        
        # BATCH 4A
        batch_4a_present = [f for f in batch_4a_fields if f in existing_columns]
        print(f"   🌱 BATCH 4A (Land Characteristics): {len(batch_4a_present)}/6 = {len(batch_4a_present)/6*100:.0f}%")
        if len(batch_4a_present) < 6:
            missing_4a = [f for f in batch_4a_fields if f not in existing_columns]
            print(f"      Missing: {missing_4a}")
        
        total_new_fields = len(batch_3a_present) + len(batch_3b_present) + len(batch_4a_present)
        print(f"   🎯 Total New Fields Added: {total_new_fields}/31")
        
        # Key category analysis
        print(f"\n📋 CATEGORY COMPLETION CHECK:")
        
        # Property Location fields (18 total)
        location_fields = [
            'property_full_street_address', 'property_city_name', 'property_state', 'property_zip_code',
            'property_zip_plus4_code', 'property_house_number', 'property_street_direction_left',
            'property_street_name', 'property_street_suffix', 'property_street_direction_right',
            'property_unit_number', 'property_unit_type', 'pa_carrier_route', 'pa_census_tract',
            'latitude', 'longitude', 'match_code', 'location_code'
        ]
        location_present = [f for f in location_fields if f in existing_columns]
        print(f"   🏠 Property Location: {len(location_present)}/18 = {len(location_present)/18*100:.0f}%")
        
        # Ownership fields (23 total)
        ownership_fields = [
            'current_owner_name', 'owner1_first_name', 'owner1_middle_name', 'owner1_last_name',
            'owner2_first_name', 'owner2_middle_name', 'owner2_last_name', 'co_mail_care_of_name',
            'co_mail_street_address', 'co_mailing_city', 'co_mailing_state', 'co_mailing_zip_code',
            'co_mailing_zip_plus4_code', 'co_unit_number', 'co_unit_type', 'mail_care_of_name_indicator',
            'owner_occupied', 'parsed_owner_source_code', 'buyer_id_code_1', 'buyer_vesting_code',
            'length_of_residence_months', 'length_of_residence_code', 'ownership_start_date'
        ]
        ownership_present = [f for f in ownership_fields if f in existing_columns]
        print(f"   👤 Ownership: {len(ownership_present)}/23 = {len(ownership_present)/23*100:.0f}%")
        
        # Land Characteristics fields (16 total)
        land_fields = [
            'lot_size_square_feet', 'lot_size_acres', 'lot_size_depth_feet', 'lot_size_frontage_feet',
            'lot_size_or_area', 'lot_size_area_unit', 'original_lot_size_or_area', 'topography',
            'site_influence', 'view', 'view_code', 'zoning', 'land_use_code', 'land_use_general',
            'neighborhood_code', 'flood_zone'
        ]
        land_present = [f for f in land_fields if f in existing_columns]
        print(f"   🌱 Land Characteristics: {len(land_present)}/16 = {len(land_present)/16*100:.0f}%")
        
        # Core system fields
        print(f"\n🔍 CORE FIELD VERIFICATION:")
        core_fields = ['quantarium_internal_pid', 'apn', 'estimated_value', 'building_area_total']
        core_present = [f for f in core_fields if f in existing_columns]
        print(f"   ✅ Core Fields: {len(core_present)}/4")
        
        # Schema migration history check
        print(f"\n📈 SCHEMA EVOLUTION:")
        print(f"   📊 Original Base Schema: ~178 columns")
        print(f"   🔥 BATCH 3A: +24 columns (Location + Ownership)")
        print(f"   💎 BATCH 3B: +1 column (Ownership perfection)")
        print(f"   🌱 BATCH 4A: +6 columns (Land Characteristics)")
        print(f"   🎯 Current Total: {total_columns} columns")
        print(f"   📈 Growth: +{total_columns - 178} columns ({(total_columns - 178)/178*100:.0f}% increase)")
        
        # Missing field analysis for loader
        print(f"\n🚀 PRODUCTION LOADER REQUIREMENTS:")
        
        # All fields that should be in the loader
        all_expected_fields = set(location_fields + ownership_fields + land_fields)
        
        # Fields definitely in database
        confirmed_fields = [f for f in all_expected_fields if f in existing_columns]
        missing_fields = [f for f in all_expected_fields if f not in existing_columns]
        
        print(f"   📊 Expected New Fields: {len(all_expected_fields)}")
        print(f"   ✅ Present in Database: {len(confirmed_fields)}")
        print(f"   ❌ Missing from Database: {len(missing_fields)}")
        
        if missing_fields:
            print(f"   🔍 Missing Fields: {missing_fields}")
        
        # Data validation (if any data exists)
        cursor.execute("SELECT COUNT(*) FROM properties")
        record_count = cursor.fetchone()[0]
        
        print(f"\n📊 DATA STATUS:")
        print(f"   🏠 Total Records: {record_count:,}")
        
        if record_count > 0:
            # Sample some key fields
            cursor.execute("""
                SELECT 
                    COUNT(*) FILTER (WHERE estimated_value IS NOT NULL) as qvm_count,
                    COUNT(*) FILTER (WHERE property_city_name IS NOT NULL) as location_count,
                    COUNT(*) FILTER (WHERE current_owner_name IS NOT NULL) as owner_count,
                    COUNT(*) FILTER (WHERE lot_size_square_feet IS NOT NULL) as land_count
                FROM properties
            """)
            
            qvm, location, owner, land = cursor.fetchone()
            
            print(f"   💰 QVM Data: {qvm:,} records ({qvm/record_count*100:.1f}%)")
            print(f"   📍 Location Data: {location:,} records ({location/record_count*100:.1f}%)")
            print(f"   👤 Owner Data: {owner:,} records ({owner/record_count*100:.1f}%)")
            print(f"   🌱 Land Data: {land:,} records ({land/record_count*100:.1f}%)")
        
        conn.close()
        return total_columns, len(confirmed_fields), len(missing_fields)
        
    except Exception as e:
        print(f"❌ Schema validation failed: {e}")
        return 0, 0, 0

if __name__ == "__main__":
    total_cols, present_fields, missing_fields = validate_current_schema_status()
    
    if total_cols > 200:
        print(f"\n🚀 SCHEMA STATUS: EXCELLENT")
        print(f"📊 {total_cols} columns - Production ready")
    elif total_cols > 180:
        print(f"\n✅ SCHEMA STATUS: GOOD")
        print(f"📊 {total_cols} columns - Most migrations complete")
    else:
        print(f"\n⚠️  SCHEMA STATUS: NEEDS ATTENTION")
        print(f"📊 {total_cols} columns - Check migration status")
        
    if missing_fields == 0:
        print(f"✅ All expected fields present - Loader ready for update")
    else:
        print(f"⚠️  {missing_fields} missing fields - Check migrations") 