#!/usr/bin/env python3
"""
DATANEST CORE PLATFORM - DATABASE ARCHITECTURE ANALYSIS
Comprehensive QA Session: Investigate 516 database columns vs 449 TSV fields
"""

import os
import sys
import psycopg2

# Add src directory to path  
sys.path.append(os.path.join(os.path.dirname(__file__), '..', 'src'))

from config import get_db_config

def analyze_database_architecture():
    """Analyze database schema to understand column architecture"""
    
    print("🔍 DATABASE ARCHITECTURE ANALYSIS - QA SESSION")
    print("🎯 Goal: Understand 516 database columns vs 449 TSV fields")
    print("=" * 70)
    
    try:
        # Connect to database
        print("📊 Connecting to database...")
        conn = psycopg2.connect(**get_db_config())
        cursor = conn.cursor()
        
        # Get all columns in properties table
        print("🗄️  ANALYZING PROPERTIES TABLE SCHEMA...")
        cursor.execute("""
            SELECT column_name, data_type, is_nullable, column_default
            FROM information_schema.columns 
            WHERE table_name = 'properties' 
            AND table_schema = 'datnest'
            ORDER BY ordinal_position;
        """)
        
        columns = cursor.fetchall()
        total_columns = len(columns)
        
        print(f"📋 Total database columns: {total_columns}")
        print()
        
        # Analyze column patterns
        print("🔍 COLUMN PATTERN ANALYSIS:")
        
        # Core system columns
        core_cols = [col for col in columns if col[0] in ['id', 'created_at', 'updated_at', 'quantarium_internal_pid']]
        print(f"   🔧 Core system columns: {len(core_cols)}")
        
        # MTG/Financing columns  
        mtg_cols = [col for col in columns if 'mtg' in col[0].lower()]
        print(f"   💰 Financing (MTG) columns: {len(mtg_cols)}")
        
        # Building characteristics
        building_cols = [col for col in columns if any(term in col[0].lower() for term in ['building', 'room', 'bath', 'bed', 'year_built', 'style', 'construction'])]
        print(f"   🏠 Building characteristics: {len(building_cols)}")
        
        # Property location
        location_cols = [col for col in columns if any(term in col[0].lower() for term in ['property_', 'address', 'city', 'state', 'zip', 'latitude', 'longitude'])]
        print(f"   📍 Property location: {len(location_cols)}")
        
        # Owner/ownership
        owner_cols = [col for col in columns if any(term in col[0].lower() for term in ['owner', 'co_', 'buyer', 'seller'])]
        print(f"   👤 Ownership: {len(owner_cols)}")
        
        # Tax/assessment
        tax_cols = [col for col in columns if any(term in col[0].lower() for term in ['tax', 'assessed', 'assessment', 'market_value', 'school'])]
        print(f"   💵 Tax/Assessment: {len(tax_cols)}")
        
        # Land characteristics
        land_cols = [col for col in columns if any(term in col[0].lower() for term in ['lot', 'land', 'site', 'zoning', 'acres'])]
        print(f"   🌱 Land characteristics: {len(land_cols)}")
        
        # Legal/parcel
        legal_cols = [col for col in columns if any(term in col[0].lower() for term in ['parcel', 'apn', 'deed', 'legal', 'subdivision', 'tract'])]
        print(f"   📋 Legal/Parcel: {len(legal_cols)}")
        
        # QVM/Valuation
        qvm_cols = [col for col in columns if any(term in col[0].lower() for term in ['qvm', 'estimated_value', 'confidence', 'price_range', 'quantarium'])]
        print(f"   💎 QVM/Valuation: {len(qvm_cols)}")
        
        # Sales/transaction
        sale_cols = [col for col in columns if any(term in col[0].lower() for term in ['sale', 'price', 'date', 'transfer', 'transaction'])]
        print(f"   💰 Sales/Transaction: {len(sale_cols)}")
        
        print()
        print("📊 SAMPLE COLUMN ANALYSIS (First 30 columns):")
        for i, (name, dtype, nullable, default) in enumerate(columns[:30]):
            print(f"   {i+1:2d}. {name:35s} ({dtype})")
        
        if total_columns > 30:
            print(f"   ... and {total_columns - 30} more columns")
        
        print()
        print("🎯 KEY FINDINGS:")
        print(f"   📊 Total Database Columns: {total_columns}")
        print(f"   📂 Expected TSV Fields: 449")
        print(f"   ❓ Extra Columns: {total_columns - 449}")
        print(f"   📈 Database vs TSV Ratio: {total_columns/449:.2f}x")
        
        # Check for specific extra columns
        print()
        print("🔍 INVESTIGATING EXTRA COLUMNS:")
        
        # Look for auto-generated or system columns
        system_cols = [col for col in columns if col[0] in ['id', 'created_at', 'updated_at']]
        if system_cols:
            print(f"   🔧 Auto-generated system columns: {len(system_cols)}")
            for col in system_cols:
                print(f"      - {col[0]}")
        
        # Look for duplicate or variant columns
        column_names = [col[0] for col in columns]
        potential_variants = []
        for name in column_names:
            if any(other != name and (name in other or other in name) for other in column_names):
                potential_variants.append(name)
        
        if potential_variants:
            print(f"   🔄 Potential variant columns: {len(potential_variants)}")
            for variant in potential_variants[:10]:  # Show first 10
                print(f"      - {variant}")
        
        cursor.close()
        conn.close()
        
        print()
        print("✅ DATABASE ARCHITECTURE ANALYSIS COMPLETE!")
        return True
        
    except Exception as e:
        print(f"❌ Error during analysis: {e}")
        return False

if __name__ == "__main__":
    success = analyze_database_architecture()
    exit(0 if success else 1) 