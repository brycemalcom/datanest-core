import pandas as pd

# Read Excel file
df = pd.read_excel('Quantarium_Open_Lien_Data_File_License_RLO_20240419_Public_V2.6.xlsx', sheet_name='OpenLien')

print(f"Total rows: {len(df)}")
print(f"Total columns: {len(df.columns)}")
print("\nColumn names:")
for i, col in enumerate(df.columns):
    print(f"{i+1}. {col}")

print("\nFirst few rows:")
print(df.head(3)) 