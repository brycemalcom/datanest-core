#!/usr/bin/env python3
"""
Property Location Field Analysis - BATCH 3A Validation
Properly categorize location vs classification fields
"""

import os
import sys

# Add src directory to path
sys.path.append(os.path.join(os.path.dirname(__file__), '..', 'src'))

import psycopg2
from config import get_db_config

def analyze_location_fields():
    """Analyze actual Property Location fields vs other property fields"""
    
    print("🔍 PROPERTY LOCATION FIELD ANALYSIS")
    print("=" * 60)
    
    try:
        db_config = get_db_config()
        conn = psycopg2.connect(**db_config)
        cursor = conn.cursor()
        
        # Get all columns
        cursor.execute("""
            SELECT column_name, data_type, character_maximum_length
            FROM information_schema.columns 
            WHERE table_name = 'properties' 
            AND table_schema = 'datnest'
            ORDER BY column_name;
        """)
        
        all_columns = {row[0]: row[1] for row in cursor.fetchall()}
        
        # TRUE Property Location fields (from data_dictionary.txt lines 76-93)
        true_location_fields = [
            'property_full_street_address',    # Line 76 - Complete address
            'property_city_name',              # Line 77 - City
            'property_state',                  # Line 78 - State
            'property_zip_code',               # Line 79 - ZIP code
            'property_zip_plus4_code',         # Line 80 - ZIP+4 (NEW)
            'property_house_number',           # Line 81 - House number (NEW)
            'property_street_direction_left',  # Line 82 - Direction prefix (NEW)
            'property_street_name',            # Line 83 - Street name (NEW)
            'property_street_suffix',          # Line 84 - Street suffix (NEW)
            'property_street_direction_right', # Line 85 - Direction suffix (NEW)
            'property_unit_number',            # Line 86 - Unit number (NEW)
            'property_unit_type',              # Line 87 - Unit type (NEW)
            'pa_carrier_route',                # Line 88 - Carrier route (NEW)
            'pa_census_tract',                 # Line 89 - Census tract (NEW)
            'latitude',                        # Line 90 - Latitude
            'longitude',                       # Line 91 - Longitude
            'match_code',                      # Line 92 - GeoStan match (NEW)
            'location_code',                   # Line 93 - GeoStan location (NEW)
        ]
        
        # Property Classification fields (NOT location)
        classification_fields = [
            'property_land_use_description',
            'property_land_use_standardized_code',
            'property_type',
            'property_subtype', 
            'property_use_general',
        ]
        
        # Check what exists
        existing_location = [field for field in true_location_fields if field in all_columns]
        existing_classification = [field for field in classification_fields if field in all_columns]
        missing_location = [field for field in true_location_fields if field not in all_columns]
        
        print(f"📊 FIELD ANALYSIS RESULTS:")
        print(f"   🎯 TRUE Property Location Fields: {len(true_location_fields)} expected")
        print(f"   ✅ Actually Present: {len(existing_location)}/{len(true_location_fields)}")
        print(f"   📋 Property Classification: {len(existing_classification)} (separate category)")
        print()
        
        print(f"🏠 ACTUAL PROPERTY LOCATION FIELDS ({len(existing_location)}/18):")
        for field in existing_location:
            print(f"   ✅ {field}")
        
        if missing_location:
            print(f"\n⚠️  MISSING LOCATION FIELDS ({len(missing_location)}):")
            for field in missing_location:
                print(f"   ❌ {field}")
        
        print(f"\n📋 PROPERTY CLASSIFICATION FIELDS (Different Category):")
        for field in existing_classification:
            print(f"   📊 {field}")
        
        # Calculate true completion
        location_completion = len(existing_location) / len(true_location_fields) * 100
        
        print(f"\n🎯 TRUE PROPERTY LOCATION COMPLETION: {location_completion:.1f}%")
        
        # Address standardization analysis
        print(f"\n🔍 ADDRESS STANDARDIZATION ANALYSIS:")
        
        core_address_fields = [
            'property_full_street_address',
            'property_city_name', 
            'property_state',
            'property_zip_code'
        ]
        
        enhanced_address_fields = [
            'property_house_number',
            'property_street_direction_left',
            'property_street_name',
            'property_street_suffix',
            'property_street_direction_right',
            'property_unit_number',
            'property_unit_type',
            'property_zip_plus4_code'
        ]
        
        geographic_fields = [
            'latitude',
            'longitude',
            'pa_census_tract',
            'pa_carrier_route',
            'match_code',
            'location_code'
        ]
        
        core_present = [f for f in core_address_fields if f in existing_location]
        enhanced_present = [f for f in enhanced_address_fields if f in existing_location]  
        geo_present = [f for f in geographic_fields if f in existing_location]
        
        print(f"   🔑 Core Address (Search/API): {len(core_present)}/4 = {len(core_present)/4*100:.0f}%")
        for field in core_present:
            print(f"      ✅ {field}")
        
        print(f"   🚀 Enhanced Address (Parsing): {len(enhanced_present)}/8 = {len(enhanced_present)/8*100:.0f}%")
        for field in enhanced_present:
            print(f"      ✅ {field}")
            
        print(f"   🌍 Geographic Intelligence: {len(geo_present)}/6 = {len(geo_present)/6*100:.0f}%")
        for field in geo_present:
            print(f"      ✅ {field}")
        
        conn.close()
        
        # Recommendations
        print(f"\n🎯 API & SEARCH OPTIMIZATION RECOMMENDATIONS:")
        
        if len(core_present) == 4:
            print(f"   ✅ Core address fields: COMPLETE - Ready for API/search")
        else:
            print(f"   ⚠️  Core address fields: INCOMPLETE - Missing critical search fields")
        
        if len(enhanced_present) >= 6:
            print(f"   ✅ Enhanced parsing: EXCELLENT - Address standardization ready")
        else:
            print(f"   ⚠️  Enhanced parsing: NEEDS WORK - Address parsing limited")
            
        if len(geo_present) >= 4:
            print(f"   ✅ Geographic intelligence: STRONG - Location analytics ready")
        else:
            print(f"   ⚠️  Geographic intelligence: BASIC - Limited location features")
        
        return location_completion >= 90
        
    except Exception as e:
        print(f"❌ Analysis failed: {e}")
        return False

if __name__ == "__main__":
    success = analyze_location_fields()
    print(f"\n{'🎯 PROPERTY LOCATION: ANALYSIS COMPLETE' if success else '❌ PROPERTY LOCATION: NEEDS ATTENTION'}") 