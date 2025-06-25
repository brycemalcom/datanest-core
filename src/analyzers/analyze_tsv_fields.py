#!/usr/bin/env python3
"""
Analyze actual TSV field structure and identify QVM priority fields
"""

def analyze_tsv_fields():
    # Read the header line
    with open('Quantarium_OpenLien_20250414_00001.TSV', 'r', encoding='utf-8') as f:
        header_line = f.readline().strip()
    
    # Split by tabs to get individual field names
    fields = header_line.split('\t')
    
    print(f"Total fields in TSV: {len(fields)}")
    
    # Categorize fields by priority
    qvm_fields = []
    property_id_fields = []
    mortgage_fields = []
    property_details = []
    
    for i, field in enumerate(fields, 1):
        field_lower = field.lower()
        
        # QVM/Valuation fields (highest priority)
        if any(keyword in field_lower for keyword in ['qvm', 'estimated_value', 'price_range', 'confidence', 'fsd_score']):
            qvm_fields.append((i, field))
        
        # Property identifier fields
        elif any(keyword in field_lower for keyword in ['quantarium_internal_pid', 'fips_code', 'assessors_parcel', 'property_full_street']):
            property_id_fields.append((i, field))
        
        # Mortgage/financing fields
        elif field.startswith('Mtg') or 'mortgage' in field_lower or 'loan' in field_lower:
            mortgage_fields.append((i, field))
        
        # Other property details
        else:
            property_details.append((i, field))
    
    print("\n=== QVM/VALUATION FIELDS (Tier 1 Priority) ===")
    for pos, field in qvm_fields:
        print(f"Field {pos}: {field}")
    
    print("\n=== PROPERTY IDENTIFIER FIELDS (Tier 2 Priority) ===")
    for pos, field in property_id_fields[:10]:  # First 10
        print(f"Field {pos}: {field}")
    
    print("\n=== MORTGAGE/FINANCING FIELDS (Sample) ===")
    for pos, field in mortgage_fields[:15]:  # First 15
        print(f"Field {pos}: {field}")
    
    print(f"\nFIELD SUMMARY:")
    print(f"- QVM/Valuation fields: {len(qvm_fields)}")
    print(f"- Property ID fields: {len(property_id_fields)}")
    print(f"- Mortgage fields: {len(mortgage_fields)}")
    print(f"- Other property details: {len(property_details)}")
    print(f"- Total: {len(fields)}")

if __name__ == "__main__":
    analyze_tsv_fields() 