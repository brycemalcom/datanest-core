#!/usr/bin/env python3
"""
COMPREHENSIVE DATA CATEGORY AUDIT - Master Database Engineer
STRATEGY: Verify true completion status of all categories and identify gaps
GOAL: Accurate assessment of what we've actually completed vs what's available
"""

import os
import re
import sys
from collections import defaultdict

# Add src to path for imports
sys.path.append(os.path.join(os.path.dirname(__file__), '..'))

def extract_current_field_mappings():
    """Extract all current field mappings from the production loader"""
    print("🔍 EXTRACTING CURRENT FIELD MAPPINGS FROM PRODUCTION LOADER...")
    
    loader_path = "src/loaders/bulletproof_production_loader.py"
    current_mappings = {}
    
    try:
        with open(loader_path, 'r', encoding='utf-8') as f:
            content = f.read()
        
        # Extract field_mapping dictionary
        start_marker = "field_mapping = {"
        end_marker = "}"
        
        start_idx = content.find(start_marker)
        if start_idx == -1:
            print("❌ Could not find field_mapping in loader")
            return {}
        
        # Find the matching closing brace
        brace_count = 0
        mapping_start = start_idx + len(start_marker) - 1
        
        for i, char in enumerate(content[mapping_start:], mapping_start):
            if char == '{':
                brace_count += 1
            elif char == '}':
                brace_count -= 1
                if brace_count == 0:
                    mapping_end = i + 1
                    break
        
        mapping_text = content[mapping_start:mapping_end]
        
        # Parse field mappings with regex
        pattern = r"'([^']+)':\s*'([^']+)'"
        matches = re.findall(pattern, mapping_text)
        
        for tsv_field, db_field in matches:
            current_mappings[tsv_field] = db_field
        
        print(f"✅ Extracted {len(current_mappings)} current field mappings")
        return current_mappings
        
    except Exception as e:
        print(f"❌ Error extracting mappings: {e}")
        return {}

def load_data_dictionary():
    """Load and parse the complete data dictionary"""
    print("📖 LOADING COMPLETE DATA DICTIONARY...")
    
    dict_path = "docs/specs/data_dictionary.txt"
    all_fields = {}
    
    try:
        with open(dict_path, 'r', encoding='utf-8') as f:
            lines = f.readlines()
        
        for line in lines[1:]:  # Skip header line
            if not line.strip():
                continue
                
            # Split by tabs - the format is tab-separated
            parts = line.strip().split('\t')
            
            if len(parts) >= 4:
                try:
                    field_num = int(parts[0].strip())
                    category = parts[1].strip()
                    display_name = parts[2].strip() 
                    tsv_header = parts[3].strip()  # This is the actual TSV column name!
                    
                    if tsv_header and tsv_header != 'NaN':
                        all_fields[tsv_header] = {
                            'field_number': field_num,
                            'display_name': display_name,
                            'category': category,
                            'description': f"{display_name} (Field #{field_num})"
                        }
                except (ValueError, IndexError):
                    continue  # Skip malformed lines
        
        print(f"✅ Loaded {len(all_fields)} total fields from data dictionary")
        return all_fields
        
    except Exception as e:
        print(f"❌ Error loading data dictionary: {e}")
        return {}

def categorize_fields(all_fields):
    """Categorize all fields based on data dictionary categories"""
    print("🏷️ CATEGORIZING ALL AVAILABLE FIELDS...")
    
    categories = {
        'Property ID': [],
        'Property Location': [],
        'Valuation': [],
        'Building Characteristics': [],
        'Land Characteristics': [],
        'Ownership': [],
        'Property Sale': [],
        'County Values/Taxes': [],
        'Financing': [],
        'Foreclosure': [],
        'Property Legal': [],
        'Parcel/Ref': [],
        'System/Meta': []
    }
    
    # Map data dictionary categories to our categories
    category_mapping = {
        'Property ID': 'Property ID',
        'Property Location': 'Property Location', 
        'Ownership': 'Ownership',
        'Property Sale': 'Property Sale',
        'Property Legal': 'Property Legal',
        'Building Characteristics': 'Building Characteristics',
        'Land Characteristics': 'Land Characteristics'
    }
    
    for field_name, field_info in all_fields.items():
        dict_category = field_info['category']
        field_lower = field_name.lower()
        
        # Use data dictionary category first, then fall back to pattern matching
        if dict_category in category_mapping:
            categories[category_mapping[dict_category]].append(field_name)
            
        # Special cases that need pattern matching due to data dictionary limitations
        elif any(x in field_lower for x in ['estimated_value', 'price_range', 'confidence_score', 'qvm']):
            categories['Valuation'].append(field_name)
            
        elif any(x in field_lower for x in ['assessed', 'assessment', 'market_value', 'tax_']):
            categories['County Values/Taxes'].append(field_name)
            
        elif any(x in field_lower for x in ['mtg', 'mortgage', 'lien', 'ltv', 'equity', 'loan', 'financing', 'lender']):
            categories['Financing'].append(field_name)
            
        elif any(x in field_lower for x in ['foreclosure', 'preforeclosure', 'pre_fcl', 'auction']):
            categories['Foreclosure'].append(field_name)
            
        elif any(x in field_lower for x in ['building_area', 'number_of_bed', 'number_of_bath', 'year_built', 'pool', 'garage', 'fireplace', 'basement', 'air_conditioning', 'heating', 'roof', 'foundation', 'exterior_walls', 'interior_walls', 'elevator', 'amenities', 'floor_cover', 'water', 'sewer', 'style', 'building_quality', 'building_condition', 'type_construction', 'number_of_stories', 'number_of_units', 'total_number_of_rooms']):
            categories['Building Characteristics'].append(field_name)
            
        elif any(x in field_lower for x in ['lot_size', 'lotsize', 'topography', 'site_influence', 'zoning']):
            categories['Land Characteristics'].append(field_name)
            
        elif any(x in field_lower for x in ['record_creation', 'trans_asof', 'quantarium_version']):
            categories['Parcel/Ref'].append(field_name)
            
        else:
            categories['System/Meta'].append(field_name)
    
    # Clean up empty categories and sort
    for category in categories:
        categories[category].sort()
    
    return categories

def audit_category_completion(categories, current_mappings):
    """Audit completion status for each category"""
    print("📊 AUDITING CATEGORY COMPLETION STATUS...")
    
    audit_results = {}
    total_available = 0
    total_mapped = 0
    
    for category, available_fields in categories.items():
        if not available_fields:  # Skip empty categories
            continue
            
        mapped_fields = []
        unmapped_fields = []
        
        for field in available_fields:
            if field in current_mappings:
                mapped_fields.append(field)
            else:
                unmapped_fields.append(field)
        
        completion_rate = (len(mapped_fields) / len(available_fields)) * 100 if available_fields else 0
        
        audit_results[category] = {
            'total_available': len(available_fields),
            'mapped_count': len(mapped_fields),
            'unmapped_count': len(unmapped_fields),
            'completion_rate': completion_rate,
            'mapped_fields': mapped_fields,
            'unmapped_fields': unmapped_fields
        }
        
        total_available += len(available_fields)
        total_mapped += len(mapped_fields)
    
    overall_completion = (total_mapped / total_available) * 100 if total_available > 0 else 0
    
    audit_results['OVERALL'] = {
        'total_available': total_available,
        'mapped_count': total_mapped,
        'completion_rate': overall_completion
    }
    
    return audit_results

def generate_audit_report(audit_results):
    """Generate comprehensive audit report"""
    print("\n" + "="*80)
    print("📋 COMPREHENSIVE DATA CATEGORY AUDIT REPORT")
    print("="*80)
    
    # Overall summary
    overall = audit_results['OVERALL']
    print(f"\n🎯 OVERALL COMPLETION STATUS:")
    print(f"   📊 Total Available Fields: {overall['total_available']:,}")
    print(f"   ✅ Currently Mapped Fields: {overall['mapped_count']:,}")
    print(f"   📈 Overall Completion Rate: {overall['completion_rate']:.1f}%")
    
    # Category breakdown
    print(f"\n📋 CATEGORY-BY-CATEGORY BREAKDOWN:")
    print("-"*80)
    
    # Sort categories by completion rate (descending)
    categories_sorted = [(cat, data) for cat, data in audit_results.items() if cat != 'OVERALL']
    categories_sorted.sort(key=lambda x: x[1]['completion_rate'], reverse=True)
    
    for category, data in categories_sorted:
        rate = data['completion_rate']
        mapped = data['mapped_count']
        total = data['total_available']
        
        # Status indicators
        if rate >= 90:
            status = "✅ COMPLETE"
        elif rate >= 70:
            status = "🔥 NEARLY COMPLETE"
        elif rate >= 30:
            status = "🚧 IN PROGRESS"
        elif rate > 0:
            status = "🌱 STARTED"
        else:
            status = "⚠️ UNMAPPED"
        
        print(f"{status:<20} {category:<25} {mapped:>3}/{total:<3} ({rate:>5.1f}%)")
        
        # Show some unmapped fields if category is incomplete
        if rate < 100 and data['unmapped_fields']:
            unmapped_sample = data['unmapped_fields'][:5]  # Show first 5 unmapped
            print(f"                     📝 Unmapped examples: {', '.join(unmapped_sample)}")
            if len(data['unmapped_fields']) > 5:
                print(f"                     📝 ... and {len(data['unmapped_fields']) - 5} more")
        print()
    
    return audit_results

def save_audit_documentation(audit_results, categories, current_mappings):
    """Save detailed audit documentation for context management"""
    print("💾 SAVING COMPREHENSIVE AUDIT DOCUMENTATION...")
    
    doc_content = f"""# DataNest Core Platform - Comprehensive Field Audit Report
Generated: {os.popen('date').read().strip()}

## Executive Summary
- **Total Available Fields**: {audit_results['OVERALL']['total_available']:,}
- **Currently Mapped Fields**: {audit_results['OVERALL']['mapped_count']:,}
- **Overall Completion Rate**: {audit_results['OVERALL']['completion_rate']:.1f}%

## Category Completion Status

"""
    
    # Sort categories by completion rate for the documentation
    categories_sorted = [(cat, data) for cat, data in audit_results.items() if cat != 'OVERALL']
    categories_sorted.sort(key=lambda x: x[1]['completion_rate'], reverse=True)
    
    for category, data in categories_sorted:
        rate = data['completion_rate']
        mapped = data['mapped_count']
        total = data['total_available']
        
        status_emoji = "✅" if rate >= 90 else "🔥" if rate >= 70 else "🚧" if rate >= 30 else "🌱" if rate > 0 else "⚠️"
        
        doc_content += f"### {status_emoji} {category}\n"
        doc_content += f"- **Status**: {mapped}/{total} fields mapped ({rate:.1f}%)\n"
        doc_content += f"- **Mapped Fields**: {len(data['mapped_fields'])}\n"
        doc_content += f"- **Unmapped Fields**: {len(data['unmapped_fields'])}\n\n"
        
        if data['mapped_fields']:
            doc_content += f"**Currently Mapped**:\n"
            for field in sorted(data['mapped_fields'])[:10]:  # Show first 10
                doc_content += f"- {field}\n"
            if len(data['mapped_fields']) > 10:
                doc_content += f"- ... and {len(data['mapped_fields']) - 10} more\n"
            doc_content += "\n"
        
        if data['unmapped_fields']:
            doc_content += f"**Available to Map**:\n"
            for field in sorted(data['unmapped_fields'])[:10]:  # Show first 10
                doc_content += f"- {field}\n"
            if len(data['unmapped_fields']) > 10:
                doc_content += f"- ... and {len(data['unmapped_fields']) - 10} more\n"
            doc_content += "\n"
        
        doc_content += "---\n\n"
    
    # Save the documentation
    with open("FIELD_AUDIT_REPORT.md", "w", encoding='utf-8') as f:
        f.write(doc_content)
    
    print("✅ Audit documentation saved to FIELD_AUDIT_REPORT.md")

def main():
    """Run comprehensive category audit"""
    print("🔍 STARTING COMPREHENSIVE DATA CATEGORY AUDIT")
    print("🎯 GOAL: Verify true completion status and identify all gaps")
    print("=" * 70)
    
    # Step 1: Extract current mappings
    current_mappings = extract_current_field_mappings()
    if not current_mappings:
        print("❌ Could not extract current mappings - audit cannot proceed")
        return
    
    # Step 2: Load data dictionary
    all_fields = load_data_dictionary()
    if not all_fields:
        print("❌ Could not load data dictionary - audit cannot proceed")
        return
    
    # Step 3: Categorize all fields
    categories = categorize_fields(all_fields)
    
    # Step 4: Audit completion status
    audit_results = audit_category_completion(categories, current_mappings)
    
    # Step 5: Generate report
    audit_report = generate_audit_report(audit_results)
    
    # Step 6: Save documentation
    save_audit_documentation(audit_results, categories, current_mappings)
    
    # Step 7: Recommendations
    print("\n🎯 AUDIT RECOMMENDATIONS:")
    incomplete_categories = [(cat, data) for cat, data in audit_results.items() 
                           if cat != 'OVERALL' and data['completion_rate'] < 100]
    
    if incomplete_categories:
        # Sort by potential impact (completion rate + field count)
        incomplete_categories.sort(key=lambda x: x[1]['completion_rate'] + (x[1]['total_available']/10), reverse=True)
        
        print("📈 Suggested next targets (high impact opportunities):")
        for i, (category, data) in enumerate(incomplete_categories[:5], 1):
            remaining = data['unmapped_count']
            current = data['completion_rate']
            print(f"   {i}. {category}: {remaining} fields remaining ({current:.1f}% → 100%)")
    
    print(f"\n✅ COMPREHENSIVE AUDIT COMPLETE!")
    print(f"📄 Full documentation saved to FIELD_AUDIT_REPORT.md")

if __name__ == "__main__":
    main() 