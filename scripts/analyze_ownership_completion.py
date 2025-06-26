#!/usr/bin/env python3
"""
Ownership Category Completion Analysis
Identify missing fields for 100% ownership intelligence
"""

import os
import sys

# Add src directory to path
sys.path.append(os.path.join(os.path.dirname(__file__), '..', 'src'))

import psycopg2
from config import get_db_config

def analyze_ownership_completion():
    """Analyze Ownership category completion status"""
    
    print("👤 OWNERSHIP CATEGORY COMPLETION ANALYSIS")
    print("🎯 Goal: Identify missing fields for 100% completion")
    print("=" * 65)
    
    try:
        db_config = get_db_config()
        conn = psycopg2.connect(**db_config)
        cursor = conn.cursor()
        
        # Get all current ownership-related columns
        cursor.execute("""
            SELECT column_name, data_type, character_maximum_length
            FROM information_schema.columns 
            WHERE table_name = 'properties' 
            AND table_schema = 'datnest'
            AND (
                column_name LIKE '%owner%' OR 
                column_name LIKE '%co_%' OR 
                column_name LIKE '%mail%' OR
                column_name LIKE '%buyer%' OR
                column_name LIKE '%residence%' OR
                column_name = 'current_owner_name'
            )
            ORDER BY column_name;
        """)
        
        existing_ownership_fields = {row[0]: row[1] for row in cursor.fetchall()}
        
        # COMPLETE Ownership fields from data_dictionary.txt lines 6-28
        complete_ownership_fields = {
            # Core Owner Information
            'current_owner_name': 'VARCHAR(166)',                    # Line 6 - Current Owner Name
            'owner1_first_name': 'VARCHAR(166)',                     # Line 17 - Owner1FirstName  
            'owner1_middle_name': 'VARCHAR(166)',                    # Line 18 - Owner1MiddleName
            'owner1_last_name': 'VARCHAR(166)',                      # Line 19 - Owner1LastName
            'owner2_first_name': 'VARCHAR(166)',                     # Line 20 - Owner2Firstname
            'owner2_middle_name': 'VARCHAR(166)',                    # Line 21 - Owner2MiddleName
            'owner2_last_name': 'VARCHAR(166)',                      # Line 22 - Owner2LastName
            
            # Owner Mailing Address (Complete)
            'co_mail_care_of_name': 'VARCHAR(60)',                   # Line 7 - CO_Mail_Care_of_Name
            'co_mail_street_address': 'VARCHAR(80)',                 # Line 8 - CO_Mail_Street_Address
            'co_mailing_city': 'VARCHAR(30)',                        # Line 9 - CO_Mailing_City
            'co_mailing_state': 'VARCHAR(2)',                        # Line 10 - CO_Mailing_State
            'co_mailing_zip_code': 'VARCHAR(5)',                     # Line 11 - CO_Mailing_Zip_Code
            'co_mailing_zip_plus4_code': 'VARCHAR(4)',               # Line 12 - CO_Mailing_Zip_Plus4Code
            'co_unit_number': 'VARCHAR(11)',                         # Line 13 - CO_Unit_Number
            'co_unit_type': 'VARCHAR(4)',                            # Line 14 - CO_Unit_Type
            
            # Owner Classification & Intelligence
            'mail_care_of_name_indicator': 'VARCHAR(1)',             # Line 15 - Mail_Care_Of_Name_Indicator
            'owner_occupied': 'VARCHAR(1)',                          # Line 16 - Owner_Occupied
            'parsed_owner_source_code': 'VARCHAR(1)',                # Line 23 - ParsedOwnerSourceCode
            'buyer_id_code_1': 'VARCHAR(2)',                         # Line 24 - Buyer_ID_Code_1
            'buyer_vesting_code': 'VARCHAR(2)',                      # Line 25 - Buyer_Vesting_Code
            
            # Ownership Duration Intelligence  
            'length_of_residence_months': 'INTEGER',                 # Line 26 - Length_of_Residence_Months
            'length_of_residence_code': 'VARCHAR(2)',                # Line 27 - Length_of_Residence_Code
            'ownership_start_date': 'DATE',                          # Line 28 - Ownership_Start_Date
        }
        
        # Analyze what exists vs what's needed
        existing_fields = set(existing_ownership_fields.keys())
        required_fields = set(complete_ownership_fields.keys())
        
        present_fields = existing_fields & required_fields
        missing_fields = required_fields - existing_fields
        
        completion_rate = len(present_fields) / len(required_fields) * 100
        
        print(f"📊 OWNERSHIP COMPLETION STATUS:")
        print(f"   🎯 Target Fields: {len(required_fields)} (100% complete category)")
        print(f"   ✅ Present: {len(present_fields)}/{len(required_fields)}")
        print(f"   ❌ Missing: {len(missing_fields)}")
        print(f"   📈 Completion Rate: {completion_rate:.1f}%")
        print()
        
        print(f"✅ EXISTING OWNERSHIP FIELDS ({len(present_fields)}):")
        for field in sorted(present_fields):
            print(f"   • {field}")
        
        if missing_fields:
            print(f"\n❌ MISSING OWNERSHIP FIELDS ({len(missing_fields)}):")
            for field in sorted(missing_fields):
                expected_type = complete_ownership_fields[field]
                print(f"   • {field} ({expected_type})")
        
        # Categorize by functionality
        print(f"\n🔍 FUNCTIONAL ANALYSIS:")
        
        # Core Identity Fields
        identity_fields = ['current_owner_name', 'owner1_first_name', 'owner1_middle_name', 'owner1_last_name', 
                          'owner2_first_name', 'owner2_middle_name', 'owner2_last_name']
        identity_present = [f for f in identity_fields if f in existing_fields]
        identity_missing = [f for f in identity_fields if f not in existing_fields]
        
        print(f"   👥 Owner Identity: {len(identity_present)}/7 = {len(identity_present)/7*100:.0f}%")
        if identity_missing:
            print(f"      Missing: {', '.join(identity_missing)}")
        
        # Mailing Address Fields
        mailing_fields = ['co_mail_care_of_name', 'co_mail_street_address', 'co_mailing_city', 
                         'co_mailing_state', 'co_mailing_zip_code', 'co_mailing_zip_plus4_code',
                         'co_unit_number', 'co_unit_type']
        mailing_present = [f for f in mailing_fields if f in existing_fields]
        mailing_missing = [f for f in mailing_fields if f not in existing_fields]
        
        print(f"   📬 Mailing Address: {len(mailing_present)}/8 = {len(mailing_present)/8*100:.0f}%")
        if mailing_missing:
            print(f"      Missing: {', '.join(mailing_missing)}")
        
        # Classification Fields
        classification_fields = ['mail_care_of_name_indicator', 'owner_occupied', 'parsed_owner_source_code',
                               'buyer_id_code_1', 'buyer_vesting_code']
        classification_present = [f for f in classification_fields if f in existing_fields]
        classification_missing = [f for f in classification_fields if f not in existing_fields]
        
        print(f"   🏷️  Owner Classification: {len(classification_present)}/5 = {len(classification_present)/5*100:.0f}%")
        if classification_missing:
            print(f"      Missing: {', '.join(classification_missing)}")
        
        # Duration Intelligence Fields
        duration_fields = ['length_of_residence_months', 'length_of_residence_code', 'ownership_start_date']
        duration_present = [f for f in duration_fields if f in existing_fields]
        duration_missing = [f for f in duration_fields if f not in existing_fields]
        
        print(f"   ⏱️  Ownership Duration: {len(duration_present)}/3 = {len(duration_present)/3*100:.0f}%")
        if duration_missing:
            print(f"      Missing: {', '.join(duration_missing)}")
        
        # Recommendations
        print(f"\n🎯 COMPLETION RECOMMENDATIONS:")
        
        if completion_rate >= 90:
            print(f"   🚀 STATUS: Nearly complete - add final {len(missing_fields)} fields")
        elif completion_rate >= 75:
            print(f"   ⚡ STATUS: Good progress - {len(missing_fields)} fields to complete")
        else:
            print(f"   🔧 STATUS: Significant work needed - {len(missing_fields)} missing fields")
        
        print(f"\n📋 BATCH 3B RECOMMENDATION:")
        print(f"   🎯 Goal: Complete Ownership category (remaining {len(missing_fields)} fields)")
        print(f"   📊 Impact: {completion_rate:.1f}% → 100% completion")
        print(f"   🚀 Value: Complete owner intelligence & contact information")
        
        conn.close()
        return completion_rate, missing_fields
        
    except Exception as e:
        print(f"❌ Analysis failed: {e}")
        return 0, []

if __name__ == "__main__":
    completion_rate, missing_fields = analyze_ownership_completion()
    
    if completion_rate >= 90:
        print(f"\n🎯 OWNERSHIP CATEGORY: NEARLY COMPLETE")
        print(f"🚀 Ready for BATCH 3B completion")
    elif completion_rate >= 75:
        print(f"\n✅ OWNERSHIP CATEGORY: GOOD PROGRESS")  
        print(f"🔧 BATCH 3B will complete the category")
    else:
        print(f"\n⚠️  OWNERSHIP CATEGORY: NEEDS WORK")
        print(f"📋 Plan multi-phase completion strategy")
    
    print(f"📊 Missing: {len(missing_fields)} fields for 100% completion") 