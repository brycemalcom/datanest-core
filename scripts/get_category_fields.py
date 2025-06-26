#!/usr/bin/env python3
"""
TSV HEADER EXTRACTOR FOR A SPECIFIC CATEGORY
Extracts all TSV header names for a given data category from the data dictionary.
"""
import pandas as pd
import os
import sys

def extract_headers_for_category(target_category):
    """Parses the data dictionary and prints TSV headers for a specific category."""
    dict_path = os.path.join(os.path.dirname(__file__), '..', 'docs', 'specs', 'data_dictionary.txt')
    
    # Using the proven fixed-width parsing strategy
    col_specs = [
        (8, 50),     # Data Category
        (100, 150),  # Header Name in Delivered File
    ]
    
    print(f"🔎 Extracting TSV headers for category: '{target_category}'")
    
    try:
        df = pd.read_fwf(dict_path, colspecs=col_specs, header=None, skiprows=1)
        df.columns = ['category', 'tsv_header']
        
        headers_found = []
        for index, row in df.iterrows():
            category = str(row['category']).strip()
            header = str(row['tsv_header']).strip()
            
            # Check if the row's category matches our target
            if target_category.lower() in category.lower():
                if header and 'NaN' not in header:
                    headers_found.append(header)
        
        if headers_found:
            print(f"\\n--- Found {len(headers_found)} TSV Headers for '{target_category}' ---")
            for header in sorted(headers_found):
                print(header)
            print("----------------------------------------------------")
            print(f"✅ Extraction complete.")
        else:
            print(f"⚠️ No headers found for category '{target_category}'. Check category name.")

    except FileNotFoundError:
        print(f"❌ ERROR: Data dictionary not found at {dict_path}")
    except Exception as e:
        print(f"❌ An unexpected error occurred: {e}")

if __name__ == "__main__":
    # For this run, we will hardcode the category to ensure we get the fields.
    extract_headers_for_category("Building")

    if len(sys.argv) > 1:
        target_category_name = sys.argv[1]
        extract_headers_for_category(target_category_name)
    else:
        print("Usage: python scripts/get_category_fields.py \\"<Category Name>\\"")
        print("Example: python scripts/get_category_fields.py \\"Building Characteristics\\"") 