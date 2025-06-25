#!/usr/bin/env python3
"""
Analyze Quantarium OpenLien field mappings
"""
import pandas as pd

def analyze_fields():
    # Read the Excel file
    df = pd.read_excel('Quantarium_Open_Lien_Data_File_License_RLO_20240419_Public_V2.6.xlsx', 
                       sheet_name='OpenLien')
    
    print(f"Total fields: {len(df)}")
    print("\nField Categories:")
    print(df['Data Category'].value_counts())
    
    print("\n=== QVM/Valuation Fields ===")
    qvm_fields = df[df['Data Category'].str.contains('Valuation|QVM', na=False, case=False)]
    if len(qvm_fields) > 0:
        for _, row in qvm_fields.head(10).iterrows():
            print(f"Field {row['Field']}: {row['Field Display Name']} -> {row['Header Name in Delivered File']}")
    else:
        print("No QVM/Valuation fields found")
    
    print("\n=== Property Identifier Fields ===")
    prop_fields = df[df['Data Category'].str.contains('Property|Location', na=False, case=False)]
    for _, row in prop_fields.head(5).iterrows():
        print(f"Field {row['Field']}: {row['Field Display Name']} -> {row['Header Name in Delivered File']}")
    
    print("\n=== All Data Categories ===")
    for category in df['Data Category'].unique():
        if pd.notna(category):
            print(f"- {category}")

if __name__ == "__main__":
    analyze_fields() 