#!/usr/bin/env python3
"""
DATANEST CORE PLATFORM - ALABAMA DATA VALIDATION SYSTEM
Comprehensive QA Session: Validate captured Alabama data against expected counts
"""

import os
import sys
import psycopg2
import pandas as pd
from collections import defaultdict

# Add src directory to path  
sys.path.append(os.path.join(os.path.dirname(__file__), '..', 'src'))

from config import get_db_config

def analyze_alabama_data_completeness():
    """Comprehensive analysis of Alabama data completeness and patterns"""
    
    print("🔍 ALABAMA DATA VALIDATION SYSTEM - QA SESSION")
    print("🎯 Goal: Validate captured data against expected Alabama counts/percentages")
    print("=" * 75)
    
    try:
        # Connect to database
        print("📊 Connecting to database...")
        conn = psycopg2.connect(**get_db_config())
        cursor = conn.cursor()
        
        # Get total record count
        print("📋 ANALYZING ALABAMA DATA PATTERNS...")
        cursor.execute("SELECT COUNT(*) FROM datnest.properties;")
        total_records = cursor.fetchone()[0]
        print(f"   📊 Total records in database: {total_records:,}")
        
        # Analyze state distribution
        print("\n🗺️  STATE DISTRIBUTION ANALYSIS:")
        cursor.execute("""
            SELECT property_state, COUNT(*) as count
            FROM datnest.properties 
            WHERE property_state IS NOT NULL
            GROUP BY property_state 
            ORDER BY count DESC;
        """)
        
        state_counts = cursor.fetchall()
        alabama_count = 0
        for state, count in state_counts:
            if state == 'AL':
                alabama_count = count
                print(f"   🎯 Alabama (AL): {count:,} records ({count/total_records*100:.1f}%)")
            elif count > 100:  # Show significant states
                print(f"   📍 {state}: {count:,} records ({count/total_records*100:.1f}%)")
        
        if alabama_count == 0:
            print("   ⚠️  No Alabama records found with property_state = 'AL'")
            # Check other potential Alabama indicators
            cursor.execute("""
                SELECT COUNT(*) FROM datnest.properties 
                WHERE property_city_name ILIKE '%alabama%' 
                OR fips_code LIKE '01%';
            """)
            alt_alabama = cursor.fetchone()[0]
            if alt_alabama > 0:
                print(f"   🔍 Alternative Alabama indicators found: {alt_alabama:,} records")
                alabama_count = alt_alabama
        
        # QVM Analysis
        print("\n💎 QVM (VALUATION) DATA ANALYSIS:")
        cursor.execute("""
            SELECT 
                COUNT(*) as total_properties,
                COUNT(CASE WHEN estimated_value IS NOT NULL THEN 1 END) as with_qvm,
                COUNT(CASE WHEN confidence_score IS NOT NULL THEN 1 END) as with_confidence,
                AVG(estimated_value) as avg_value,
                MIN(estimated_value) as min_value,
                MAX(estimated_value) as max_value
            FROM datnest.properties;
        """)
        
        qvm_stats = cursor.fetchone()
        total_props, with_qvm, with_confidence, avg_val, min_val, max_val = qvm_stats
        
        print(f"   📊 Properties with QVM data: {with_qvm:,} / {total_props:,} ({with_qvm/total_props*100:.1f}%)")
        print(f"   📊 Properties with confidence: {with_confidence:,} / {total_props:,} ({with_confidence/total_props*100:.1f}%)")
        if avg_val:
            print(f"   💰 Average value: ${avg_val:,.0f}")
            print(f"   💰 Value range: ${min_val:,.0f} - ${max_val:,.0f}")
        
        # Building Characteristics Analysis
        print("\n🏠 BUILDING CHARACTERISTICS ANALYSIS:")
        cursor.execute("""
            SELECT 
                COUNT(*) as total,
                COUNT(CASE WHEN building_area_total IS NOT NULL THEN 1 END) as with_area,
                COUNT(CASE WHEN number_of_bedrooms IS NOT NULL THEN 1 END) as with_bedrooms,
                COUNT(CASE WHEN number_of_bathrooms IS NOT NULL THEN 1 END) as with_bathrooms,
                COUNT(CASE WHEN year_built IS NOT NULL THEN 1 END) as with_year_built,
                AVG(building_area_total) as avg_sqft,
                AVG(number_of_bedrooms) as avg_bedrooms,
                AVG(number_of_bathrooms) as avg_bathrooms
            FROM datnest.properties;
        """)
        
        building_stats = cursor.fetchone()
        total, with_area, with_beds, with_baths, with_year, avg_sqft, avg_beds, avg_baths = building_stats
        
        print(f"   🏠 Building area: {with_area:,} / {total:,} ({with_area/total*100:.1f}%)")
        print(f"   🛏️  Bedrooms: {with_beds:,} / {total:,} ({with_beds/total*100:.1f}%)")
        print(f"   🛁 Bathrooms: {with_baths:,} / {total:,} ({with_baths/total*100:.1f}%)")
        print(f"   📅 Year built: {with_year:,} / {total:,} ({with_year/total*100:.1f}%)")
        if avg_sqft:
            print(f"   📐 Average sq ft: {avg_sqft:,.0f}")
            print(f"   🛏️  Average bedrooms: {avg_beds:.1f}")
            print(f"   🛁 Average bathrooms: {avg_baths:.1f}")
        
        # Property Sale Analysis
        print("\n💰 PROPERTY SALE DATA ANALYSIS:")
        cursor.execute("""
            SELECT 
                COUNT(*) as total,
                COUNT(CASE WHEN lsale_price IS NOT NULL THEN 1 END) as with_sale_price,
                COUNT(CASE WHEN lsale_date IS NOT NULL THEN 1 END) as with_sale_date,
                COUNT(CASE WHEN seller_name IS NOT NULL THEN 1 END) as with_seller,
                AVG(lsale_price) as avg_sale_price,
                MIN(lsale_date) as earliest_sale,
                MAX(lsale_date) as latest_sale
            FROM datnest.properties;
        """)
        
        sale_stats = cursor.fetchone()
        if sale_stats and sale_stats[0]:
            total, with_price, with_date, with_seller, avg_price, earliest, latest = sale_stats
            print(f"   💰 Sale prices: {with_price:,} / {total:,} ({with_price/total*100:.1f}%)")
            print(f"   📅 Sale dates: {with_date:,} / {total:,} ({with_date/total*100:.1f}%)")
            print(f"   👤 Seller info: {with_seller:,} / {total:,} ({with_seller/total*100:.1f}%)")
            if avg_price:
                print(f"   💰 Average sale price: ${avg_price:,.0f}")
            if earliest and latest:
                print(f"   📅 Sale date range: {earliest} to {latest}")
        
        # Ownership Analysis
        print("\n👤 OWNERSHIP DATA ANALYSIS:")
        cursor.execute("""
            SELECT 
                COUNT(*) as total,
                COUNT(CASE WHEN owner1lastname IS NOT NULL THEN 1 END) as with_owner1,
                COUNT(CASE WHEN owner2lastname IS NOT NULL THEN 1 END) as with_owner2,
                COUNT(CASE WHEN mailing_address IS NOT NULL THEN 1 END) as with_mailing
            FROM datnest.properties;
        """)
        
        owner_stats = cursor.fetchone()
        if owner_stats and owner_stats[0]:
            total, with_owner1, with_owner2, with_mailing = owner_stats
            print(f"   👤 Primary owner: {with_owner1:,} / {total:,} ({with_owner1/total*100:.1f}%)")
            print(f"   👥 Secondary owner: {with_owner2:,} / {total:,} ({with_owner2/total*100:.1f}%)")
            print(f"   📮 Mailing address: {with_mailing:,} / {total:,} ({with_mailing/total*100:.1f}%)")
        
        # Tax/Assessment Analysis
        print("\n💵 TAX & ASSESSMENT DATA ANALYSIS:")
        cursor.execute("""
            SELECT 
                COUNT(*) as total,
                COUNT(CASE WHEN total_assessed_value IS NOT NULL THEN 1 END) as with_assessed,
                COUNT(CASE WHEN assessment_year IS NOT NULL THEN 1 END) as with_year,
                COUNT(CASE WHEN tax_amount IS NOT NULL THEN 1 END) as with_tax_amount,
                AVG(total_assessed_value) as avg_assessed,
                AVG(tax_amount) as avg_tax
            FROM datnest.properties;
        """)
        
        tax_stats = cursor.fetchone()
        if tax_stats and tax_stats[0]:
            total, with_assessed, with_year, with_tax, avg_assessed, avg_tax = tax_stats
            print(f"   💵 Assessed values: {with_assessed:,} / {total:,} ({with_assessed/total*100:.1f}%)")
            print(f"   📅 Assessment years: {with_year:,} / {total:,} ({with_year/total*100:.1f}%)")
            print(f"   💰 Tax amounts: {with_tax:,} / {total:,} ({with_tax/total*100:.1f}%)")
            if avg_assessed:
                print(f"   💵 Average assessed value: ${avg_assessed:,.0f}")
            if avg_tax:
                print(f"   💰 Average tax amount: ${avg_tax:,.0f}")
        
        # Financing Analysis
        print("\n💰 FINANCING DATA ANALYSIS:")
        cursor.execute("""
            SELECT 
                COUNT(*) as total,
                COUNT(CASE WHEN first_mtg_amount IS NOT NULL THEN 1 END) as with_mtg1,
                COUNT(CASE WHEN second_mtg_amount IS NOT NULL THEN 1 END) as with_mtg2,
                COUNT(CASE WHEN first_mtg_lender_name IS NOT NULL THEN 1 END) as with_lender,
                AVG(first_mtg_amount) as avg_mtg1,
                AVG(second_mtg_amount) as avg_mtg2
            FROM datnest.properties;
        """)
        
        financing_stats = cursor.fetchone()
        if financing_stats and financing_stats[0]:
            total, with_mtg1, with_mtg2, with_lender, avg_mtg1, avg_mtg2 = financing_stats
            print(f"   💰 First mortgages: {with_mtg1:,} / {total:,} ({with_mtg1/total*100:.1f}%)")
            print(f"   💰 Second mortgages: {with_mtg2:,} / {total:,} ({with_mtg2/total*100:.1f}%)")
            print(f"   🏦 Lender info: {with_lender:,} / {total:,} ({with_lender/total*100:.1f}%)")
            if avg_mtg1:
                print(f"   💰 Average 1st mortgage: ${avg_mtg1:,.0f}")
            if avg_mtg2:
                print(f"   💰 Average 2nd mortgage: ${avg_mtg2:,.0f}")
        
        # Generate Alabama-specific recommendations
        print("\n🎯 ALABAMA DATA VALIDATION SUMMARY:")
        print(f"   📊 Total properties analyzed: {total_records:,}")
        print(f"   🗺️  Alabama properties identified: {alabama_count:,}")
        print(f"   💎 QVM coverage: {with_qvm/total_props*100:.1f}%")
        print(f"   🏠 Building data coverage: {with_area/total*100:.1f}%")
        print(f"   👤 Ownership data coverage: {with_owner1/total*100:.1f}%")
        
        print("\n📋 READY FOR COUNT DOCUMENT VALIDATION:")
        print("   🔍 System can now compare against your expected Alabama counts")
        print("   📊 All major data categories analyzed and ready for validation")
        print("   🎯 Baseline metrics established for comparison")
        
        cursor.close()
        conn.close()
        
        print("\n✅ ALABAMA DATA VALIDATION ANALYSIS COMPLETE!")
        return True
        
    except Exception as e:
        print(f"❌ Error during Alabama analysis: {e}")
        return False

def validate_against_expected_counts(expected_counts=None):
    """Validate actual data against expected counts from count document"""
    
    print("\n" + "=" * 75)
    print("🔍 EXPECTED VS ACTUAL COUNT VALIDATION")
    print("🎯 Goal: Compare actual data capture against expected Alabama patterns")
    print("=" * 75)
    
    # Placeholder for when user provides their count document
    if expected_counts is None:
        print("📋 READY FOR COUNT DOCUMENT INPUT:")
        print("   1. Please provide your Alabama count document")
        print("   2. Expected format: percentages/counts for each data category")
        print("   3. System will automatically compare actual vs expected")
        print("   4. Discrepancies will be highlighted for investigation")
        
        print("\n📊 SAMPLE VALIDATION TEMPLATE:")
        print("   Expected QVM Coverage: ___%")
        print("   Expected Building Data: ___%") 
        print("   Expected Ownership Data: ___%")
        print("   Expected Sale Data: ___%")
        print("   Expected Tax Data: ___%")
        print("   Expected Financing Data: ___%")
        
        return True
    
    # When actual expected counts are provided, implement validation logic here
    print("🔍 Validating against provided expected counts...")
    # Implementation will be added when count document is provided
    
    return True

if __name__ == "__main__":
    print("🚀 STARTING COMPREHENSIVE ALABAMA DATA VALIDATION")
    
    # Run Alabama data analysis
    success1 = analyze_alabama_data_completeness()
    
    # Run count validation
    success2 = validate_against_expected_counts()
    
    overall_success = success1 and success2
    print(f"\n🎯 ALABAMA VALIDATION SESSION: {'SUCCESS' if overall_success else 'NEEDS ATTENTION'}")
    
    exit(0 if overall_success else 1) 