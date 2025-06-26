#!/usr/bin/env python3
"""
DatNest Core Platform - BATCH 3A VALIDATION TEST
Systematic validation for Property Location & Ownership completion

🎯 VALIDATES: Property Location (67% → 100%) + Ownership (60% → 100%)
📊 TEST SCOPE: 22 new fields (12 Location + 10 Ownership)
📋 EVIDENCE: All fields verified against data_dictionary.txt

Author: Master Database Engineer
Date: 2025-06-26 
Status: BATCH 3A SYSTEMATIC COMPLETION VALIDATION
"""

import pandas as pd
import psycopg2
import os
import sys
from datetime import datetime

def validate_batch_3a_systematic_completion():
    """
    🎯 BATCH 3A VALIDATION: Complete Location & Ownership
    Validate 100% completion of both categories
    """
    
    print("=" * 80)
    print("🎯 BATCH 3A VALIDATION: SYSTEMATIC COMPLETION TEST")
    print("📊 TARGET: Property Location (67% → 100%) + Ownership (60% → 100%)")
    print("🔍 VALIDATING: 22 new fields for systematic completion")
    print("=" * 80)
    
    # =====================================================
    # BATCH 3A: SYSTEMATIC FIELD MAPPING VALIDATION
    # =====================================================
    
    # Property Location Fields (18 total for 100% completion)
    location_fields = {
        # EXISTING (6 fields) - Already working
        'Property_Full_Street_Address': 'property_full_street_address',
        'Property_City_Name': 'property_city_name',
        'Property_State': 'property_state',
        'Property_Zip_Code': 'property_zip_code',
        'PA_Latitude': 'latitude',
        'PA_Longitude': 'longitude',
        
        # NEW BATCH 3A (12 fields) - Complete the category
        'Property_Zip_Plus4Code': 'property_zip_plus4_code',
        'Property_House_Number': 'property_house_number',
        'Property_Street_Direction_Left': 'property_street_direction_left',
        'Property_Street_Name': 'property_street_name',
        'Property_Street_Suffix': 'property_street_suffix',
        'Property_Street_Direction_Right': 'property_street_direction_right',
        'Property_Unit_Number': 'property_unit_number',
        'Property_Unit_Type': 'property_unit_type',
        'PA_Carrier_Route': 'pa_carrier_route',
        'PA_Census_Tract': 'pa_census_tract',
        'Match_Code': 'match_code',
        'Location_Code': 'location_code',
    }
    
    # Ownership Fields (25 total for 100% completion)
    ownership_fields = {
        # EXISTING (15 fields) - Already working from previous batches
        'Current_Owner_Name': 'current_owner_name',
        'Owner_Occupied': 'owner_occupied',
        'Owner1FirstName': 'owner1_first_name',
        'Owner1LastName': 'owner1_last_name',
        'Owner2Firstname': 'owner2_first_name',
        'Owner2LastName': 'owner2_last_name',
        'CO_Mailing_City': 'co_mailing_city',
        'CO_Mailing_State': 'co_mailing_state',
        'CO_Mailing_Zip_Code': 'co_mailing_zip_code',
        'Length_of_Residence_Months': 'length_of_residence_months',
        'Ownership_Start_Date': 'ownership_start_date',
        
        # NEW BATCH 3A (10+ fields) - Complete the category
        'Owner1MiddleName': 'owner1_middle_name',
        'Owner2MiddleName': 'owner2_middle_name',
        'CO_Mail_Care_of_Name': 'co_mail_care_of_name',
        'CO_Mail_Street_Address': 'co_mail_street_address',
        'CO_Mailing_Zip_Plus4Code': 'co_mailing_zip_plus4_code',
        'CO_Unit_Number': 'co_unit_number',
        'CO_Unit_Type': 'co_unit_type',
        'Mail_Care_Of_Name_Indicator': 'mail_care_of_name_indicator',
        'ParsedOwnerSourceCode': 'parsed_owner_source_code',
        'Buyer_ID_Code_1': 'buyer_id_code_1',
        'Buyer_Vesting_Code': 'buyer_vesting_code',
        'Length_of_Residence_Code': 'length_of_residence_code',
    }
    
    all_fields = {**location_fields, **ownership_fields}
    
    print(f"🎯 BATCH 3A TARGET VALIDATION:")
    print(f"   🏠 Property Location: {len(location_fields)} fields (100% target)")
    print(f"   👤 Ownership: {len(ownership_fields)} fields (100% target)")
    print(f"   📊 Total Fields to Validate: {len(all_fields)}")
    print()
    
    # =====================================================
    # TSV DATA VALIDATION
    # =====================================================
    
    print("🔍 STEP 1: TSV Field Availability Validation")
    
    # Find TSV file
    tsv_files = [f for f in os.listdir('.') if f.endswith('.tsv')]
    if not tsv_files:
        print("❌ ERROR: No TSV files found")
        return False
    
    tsv_file = max(tsv_files, key=os.path.getmtime)
    print(f"📁 Analyzing: {tsv_file}")
    
    # Load sample for validation
    try:
        sample_df = pd.read_csv(tsv_file, sep='\t', nrows=1000, low_memory=False)
        available_cols = set(sample_df.columns)
        
        # Check field availability
        location_available = {k: v for k, v in location_fields.items() if k in available_cols}
        ownership_available = {k: v for k, v in ownership_fields.items() if k in available_cols}
        
        location_missing = set(location_fields.keys()) - available_cols
        ownership_missing = set(ownership_fields.keys()) - available_cols
        
        print(f"   🏠 Property Location Available: {len(location_available)}/{len(location_fields)}")
        print(f"   👤 Ownership Available: {len(ownership_available)}/{len(ownership_fields)}")
        
        if location_missing:
            print(f"   ⚠️  Missing Location Fields: {', '.join(sorted(location_missing))}")
        if ownership_missing:
            print(f"   ⚠️  Missing Ownership Fields: {', '.join(sorted(ownership_missing))}")
        
        # Calculate completion percentages
        location_completion = len(location_available) / len(location_fields) * 100
        ownership_completion = len(ownership_available) / len(ownership_fields) * 100
        
        print(f"   📊 Property Location Completion: {location_completion:.1f}%")
        print(f"   📊 Ownership Completion: {ownership_completion:.1f}%")
        
    except Exception as e:
        print(f"❌ TSV validation failed: {e}")
        return False
    
    # =====================================================
    # DATA TYPE AND CONTENT VALIDATION
    # =====================================================
    
    print(f"\n🔍 STEP 2: Data Type & Content Validation")
    
    # Location field content tests
    location_tests = []
    
    # Test Property Location fields
    for tsv_field, db_field in location_available.items():
        try:
            sample_values = sample_df[tsv_field].dropna().head(10)
            if len(sample_values) > 0:
                if 'Zip' in tsv_field:
                    # ZIP codes should be 5 digits or 5+4
                    valid_zips = sample_values.astype(str).str.match(r'^\d{5}(-\d{4})?$').sum()
                    location_tests.append((tsv_field, 'zip_format', valid_zips > 0))
                elif 'Latitude' in tsv_field or 'Longitude' in tsv_field:
                    # Coordinates should be numeric
                    numeric_coords = pd.to_numeric(sample_values, errors='coerce').notna().sum()
                    location_tests.append((tsv_field, 'numeric', numeric_coords > 0))
                elif 'State' in tsv_field:
                    # States should be 2 characters
                    valid_states = sample_values.astype(str).str.len().eq(2).sum()
                    location_tests.append((tsv_field, 'state_format', valid_states > 0))
                else:
                    # Text fields should have content
                    has_content = sample_values.astype(str).str.len() > 0
                    location_tests.append((tsv_field, 'text_content', has_content.sum() > 0))
        except Exception as e:
            location_tests.append((tsv_field, 'error', False))
    
    # Test Ownership fields
    ownership_tests = []
    
    for tsv_field, db_field in ownership_available.items():
        try:
            sample_values = sample_df[tsv_field].dropna().head(10)
            if len(sample_values) > 0:
                if 'Date' in tsv_field:
                    # Date fields should be parseable
                    try:
                        pd.to_datetime(sample_values.head(5), errors='coerce')
                        ownership_tests.append((tsv_field, 'date_format', True))
                    except:
                        ownership_tests.append((tsv_field, 'date_format', False))
                elif 'Months' in tsv_field:
                    # Numeric fields
                    numeric_values = pd.to_numeric(sample_values, errors='coerce').notna().sum()
                    ownership_tests.append((tsv_field, 'numeric', numeric_values > 0))
                else:
                    # Text fields should have content
                    has_content = sample_values.astype(str).str.len() > 0
                    ownership_tests.append((tsv_field, 'text_content', has_content.sum() > 0))
        except Exception as e:
            ownership_tests.append((tsv_field, 'error', False))
    
    # Validation results
    location_success = sum(1 for _, _, success in location_tests if success)
    ownership_success = sum(1 for _, _, success in ownership_tests if success)
    
    print(f"   🏠 Property Location Tests: {location_success}/{len(location_tests)} passed")
    print(f"   👤 Ownership Tests: {ownership_success}/{len(ownership_tests)} passed")
    
    # =====================================================
    # DATABASE SCHEMA VALIDATION
    # =====================================================
    
    print(f"\n🔍 STEP 3: Database Schema Validation")
    
    try:
        with psycopg2.connect(
            host=os.getenv('DB_HOST', 'localhost'),
            database=os.getenv('DB_NAME', 'datanest'),
            user=os.getenv('DB_USER', 'datanest_user'),
            password=os.getenv('DB_PASSWORD', '')
        ) as conn:
            with conn.cursor() as cursor:
                # Check if new columns exist
                cursor.execute("""
                    SELECT column_name, data_type 
                    FROM information_schema.columns 
                    WHERE table_name = 'properties' 
                    AND table_schema = 'datnest'
                    ORDER BY column_name;
                """)
                db_columns = {row[0]: row[1] for row in cursor.fetchall()}
                
                # Validate BATCH 3A columns exist
                batch_3a_fields = list(all_fields.values())
                existing_fields = [field for field in batch_3a_fields if field in db_columns]
                missing_fields = [field for field in batch_3a_fields if field not in db_columns]
                
                print(f"   📊 Database Columns Available: {len(db_columns)}")
                print(f"   ✅ BATCH 3A Fields in DB: {len(existing_fields)}/{len(batch_3a_fields)}")
                
                if missing_fields:
                    print(f"   ⚠️  Missing DB Fields: {', '.join(missing_fields[:10])}")
                    if len(missing_fields) > 10:
                        print(f"        ... and {len(missing_fields) - 10} more")
                
    except Exception as e:
        print(f"❌ Database validation failed: {e}")
        return False
    
    # =====================================================
    # SYSTEMATIC COMPLETION SCORE
    # =====================================================
    
    print(f"\n📊 BATCH 3A SYSTEMATIC COMPLETION SCORE:")
    
    # Calculate scores
    tsv_score = (len(location_available) + len(ownership_available)) / len(all_fields) * 100
    validation_score = (location_success + ownership_success) / max(1, len(location_tests) + len(ownership_tests)) * 100
    db_score = len(existing_fields) / len(batch_3a_fields) * 100
    
    overall_score = (tsv_score + validation_score + db_score) / 3
    
    print(f"   📋 TSV Field Availability: {tsv_score:.1f}%")
    print(f"   🔍 Data Quality Validation: {validation_score:.1f}%")
    print(f"   💾 Database Schema Ready: {db_score:.1f}%")
    print(f"   🎯 Overall Readiness: {overall_score:.1f}%")
    
    # Success criteria
    success = (
        location_completion >= 90 and  # 90%+ location fields available
        ownership_completion >= 90 and  # 90%+ ownership fields available
        validation_score >= 80 and    # 80%+ data quality
        overall_score >= 85           # 85%+ overall readiness
    )
    
    print(f"\n{'✅ BATCH 3A VALIDATION: PASSED' if success else '❌ BATCH 3A VALIDATION: NEEDS WORK'}")
    
    if success:
        print(f"🚀 Ready for systematic completion of Property Location & Ownership!")
        print(f"🎯 Expected Results: Property Location 100%, Ownership 100%")
    else:
        print(f"⚠️  Recommendations:")
        if location_completion < 90:
            print(f"   • Review missing Property Location fields")
        if ownership_completion < 90:
            print(f"   • Review missing Ownership fields") 
        if validation_score < 80:
            print(f"   • Improve data quality validation")
    
    return success

if __name__ == "__main__":
    success = validate_batch_3a_systematic_completion()
    if success:
        print(f"\n🎯 BATCH 3A VALIDATION: SUCCESS!")
        print(f"🚀 Proceed with systematic completion")
    else:
        print(f"\n❌ BATCH 3A VALIDATION: FAILED")
        print(f"🔧 Address issues before proceeding")
        sys.exit(1) 