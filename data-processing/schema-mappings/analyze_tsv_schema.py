#!/usr/bin/env python3
"""
DatNest Core Platform - TSV Schema Analysis
Analyzes TSV files to validate field mappings and QVM coverage
"""

import argparse
import pandas as pd
import boto3
from io import StringIO
import sys
import json
from typing import Dict, List, Any
from tsv_field_mapping import get_field_mapper

def download_tsv_from_s3(bucket: str, key: str) -> str:
    """Download TSV content from S3"""
    s3 = boto3.client('s3')
    try:
        response = s3.get_object(Bucket=bucket, Key=key)
        return response['Body'].read().decode('utf-8')
    except Exception as e:
        print(f"Error downloading from S3: {e}")
        return None

def analyze_tsv_headers(tsv_content: str, sample_rows: int = 5) -> Dict[str, Any]:
    """Analyze TSV file headers and sample data"""
    
    # Read TSV into DataFrame
    df = pd.read_csv(StringIO(tsv_content), sep='\t', nrows=sample_rows)
    
    # Get headers
    headers = list(df.columns)
    
    # Get field mapper
    mapper = get_field_mapper()
    
    # Validate headers against our mappings
    validation_results = mapper.validate_tsv_headers(headers)
    
    # Analyze sample data
    sample_analysis = {}
    for col in headers[:20]:  # Analyze first 20 columns
        sample_values = df[col].dropna().head(3).tolist()
        sample_analysis[col] = {
            "sample_values": [str(v) for v in sample_values],
            "null_count": df[col].isnull().sum(),
            "data_type": str(df[col].dtype)
        }
    
    return {
        "file_info": {
            "total_columns": len(headers),
            "sample_rows": len(df),
            "file_size_chars": len(tsv_content)
        },
        "headers": headers,
        "validation": validation_results,
        "sample_analysis": sample_analysis,
        "tier1_analysis": analyze_tier1_fields(headers, df, mapper)
    }

def analyze_tier1_fields(headers: List[str], df: pd.DataFrame, mapper) -> Dict[str, Any]:
    """Analyze Tier 1 (QVM and critical) fields specifically"""
    
    tier1_mappings = mapper.get_tier1_mappings()
    tier1_analysis = {
        "qvm_fields_found": [],
        "qvm_fields_missing": [],
        "location_fields_found": [],
        "property_fields_found": [],
        "field_variations": {}
    }
    
    # Check for QVM fields
    qvm_field_names = [
        "Quantarium Value", "ESTIMATED_VALUE", "QVM Value",
        "Quantarium Value High", "PRICE_RANGE_MAX", "QVM High",
        "Quantarium Value Low", "PRICE_RANGE_MIN", "QVM Low",
        "Quantarium Value Confidence", "CONFIDENCE_SCORE", "QVM Confidence",
        "QVM_asof_Date", "QVM_Date"
    ]
    
    location_field_names = [
        "Property_Full_Street_Address", "Site Address", "Property Address",
        "Property_City_Name", "Site City", "Property City",
        "Property_State", "Site State", "Property State",
        "Property_Zip_Code", "Site Zip5", "Site Zip"
    ]
    
    property_field_names = [
        "Building_Area_1", "Building Area 1", "Building Area",
        "LotSize_Square_Feet", "Lot Size SqFt", "Lot Size",
        "Number of Bedroom", "Bedrooms", "Bedroom Count",
        "Number of Baths", "Bathrooms", "Bath Count"
    ]
    
    # Find matching fields
    for header in headers:
        if header in qvm_field_names:
            tier1_analysis["qvm_fields_found"].append(header)
        elif header in location_field_names:
            tier1_analysis["location_fields_found"].append(header)
        elif header in property_field_names:
            tier1_analysis["property_fields_found"].append(header)
    
    # Look for similar field names (fuzzy matching)
    for target_field in ["Quantarium Value", "Site Address", "Building Area"]:
        similar_fields = [h for h in headers if target_field.lower().replace(" ", "") in h.lower().replace("_", "").replace(" ", "")]
        if similar_fields:
            tier1_analysis["field_variations"][target_field] = similar_fields
    
    return tier1_analysis

def generate_mapping_recommendations(analysis: Dict[str, Any]) -> List[str]:
    """Generate recommendations for field mapping updates"""
    recommendations = []
    
    validation = analysis["validation"]
    tier1 = analysis["tier1_analysis"]
    
    # Check Tier 1 coverage
    if validation["tier1_coverage"] < 80:
        recommendations.append(
            f"⚠️  LOW TIER 1 COVERAGE: Only {validation['tier1_coverage']:.1f}% of critical QVM fields found"
        )
    
    # Check for missing QVM fields
    if len(tier1["qvm_fields_found"]) < 3:
        recommendations.append(
            "🚨 CRITICAL: Less than 3 QVM fields found. Please verify field names in TSV file."
        )
    
    # Check for field variations
    if tier1["field_variations"]:
        recommendations.append(
            "💡 FIELD VARIATIONS DETECTED: Update field mappings to match actual TSV field names"
        )
        for target, variations in tier1["field_variations"].items():
            recommendations.append(f"   - {target} → Found: {', '.join(variations)}")
    
    # Check overall coverage
    if validation["coverage_percentage"] < 50:
        recommendations.append(
            f"📊 LOW OVERALL COVERAGE: Only {validation['coverage_percentage']:.1f}% of expected fields mapped"
        )
    
    return recommendations

def print_analysis_report(analysis: Dict[str, Any]):
    """Print formatted analysis report"""
    
    print("\n" + "="*80)
    print("🏗️  DATNEST CORE PLATFORM - TSV SCHEMA ANALYSIS")
    print("="*80)
    
    # File Info
    file_info = analysis["file_info"]
    print(f"\n📁 FILE INFORMATION:")
    print(f"   Total Columns: {file_info['total_columns']}")
    print(f"   Sample Rows: {file_info['sample_rows']}")
    print(f"   File Size: {file_info['file_size_chars']:,} characters")
    
    # Validation Results
    validation = analysis["validation"]
    print(f"\n🔍 FIELD MAPPING VALIDATION:")
    print(f"   Total Headers: {validation['total_headers']}")
    print(f"   Mapped Headers: {validation['mapped_headers']}")
    print(f"   Coverage: {validation['coverage_percentage']:.1f}%")
    print(f"   Tier 1 (QVM) Coverage: {validation['tier1_coverage']:.1f}%")
    
    # Tier 1 Analysis
    tier1 = analysis["tier1_analysis"]
    print(f"\n🎯 TIER 1 (CRITICAL) FIELD ANALYSIS:")
    print(f"   QVM Fields Found: {len(tier1['qvm_fields_found'])}")
    if tier1["qvm_fields_found"]:
        print(f"   → {', '.join(tier1['qvm_fields_found'])}")
    
    print(f"   Location Fields Found: {len(tier1['location_fields_found'])}")
    if tier1["location_fields_found"]:
        print(f"   → {', '.join(tier1['location_fields_found'])}")
    
    print(f"   Property Fields Found: {len(tier1['property_fields_found'])}")
    if tier1["property_fields_found"]:
        print(f"   → {', '.join(tier1['property_fields_found'])}")
    
    # Missing Critical Fields
    if validation["missing_tier1_fields"]:
        print(f"\n⚠️  MISSING TIER 1 FIELDS:")
        for field in validation["missing_tier1_fields"][:10]:  # Show first 10
            print(f"   - {field}")
    
    # Field Variations
    if tier1["field_variations"]:
        print(f"\n💡 FIELD VARIATIONS DETECTED:")
        for target, variations in tier1["field_variations"].items():
            print(f"   {target}: {', '.join(variations)}")
    
    # Sample Data
    print(f"\n📊 SAMPLE DATA (First 10 Fields):")
    sample_analysis = analysis["sample_analysis"]
    for i, (field, data) in enumerate(list(sample_analysis.items())[:10]):
        print(f"   {i+1:2}. {field}")
        print(f"       Type: {data['data_type']}, Nulls: {data['null_count']}")
        if data["sample_values"]:
            print(f"       Samples: {', '.join(data['sample_values'][:2])}")
    
    # Recommendations
    recommendations = generate_mapping_recommendations(analysis)
    if recommendations:
        print(f"\n🚀 RECOMMENDATIONS:")
        for rec in recommendations:
            print(f"   {rec}")
    
    print(f"\n✅ NEXT STEPS:")
    print(f"   1. Update field mappings in data-processing/schema-mappings/tsv_field_mapping.py")
    print(f"   2. Test with sample data processing")
    print(f"   3. Deploy Lambda functions with updated mappings")
    print(f"   4. Process full dataset")
    
    print("\n" + "="*80)

def main():
    parser = argparse.ArgumentParser(description="Analyze TSV schema for DatNest Core Platform")
    parser.add_argument("--bucket", required=True, help="S3 bucket name containing TSV file")
    parser.add_argument("--file", required=True, help="TSV file key in S3 bucket")
    parser.add_argument("--local", help="Path to local TSV file (alternative to S3)")
    parser.add_argument("--output", help="Output JSON file path for analysis results")
    parser.add_argument("--sample-rows", type=int, default=5, help="Number of sample rows to analyze")
    
    args = parser.parse_args()
    
    # Get TSV content
    if args.local:
        try:
            with open(args.local, 'r', encoding='utf-8') as f:
                tsv_content = f.read()
        except Exception as e:
            print(f"Error reading local file: {e}")
            sys.exit(1)
    else:
        print(f"Downloading TSV from s3://{args.bucket}/{args.file}...")
        tsv_content = download_tsv_from_s3(args.bucket, args.file)
        if not tsv_content:
            sys.exit(1)
    
    # Analyze TSV
    print("Analyzing TSV schema...")
    analysis = analyze_tsv_headers(tsv_content, args.sample_rows)
    
    # Print report
    print_analysis_report(analysis)
    
    # Save to JSON if requested
    if args.output:
        with open(args.output, 'w') as f:
            json.dump(analysis, f, indent=2)
        print(f"\n💾 Analysis saved to {args.output}")

if __name__ == "__main__":
    main() 