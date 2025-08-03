#!/usr/bin/env python3
"""
MVP Clean Loader - DataNest Core Platform
Loads 19 core fields for immediate client valuation business.
Removes problematic fields to eliminate chunk failures.

Performance Target: 5M records in 20 minutes
Strategy: No total_assessed_value, no owner_occupied, clean UTF8
"""

import pandas as pd
import psycopg2
import multiprocessing as mp
import logging
import time
from concurrent.futures import ProcessPoolExecutor
import json
import os
import tempfile
import csv

# Setup logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

def load_config():
    """Load database configuration"""
    with open('local_config.json', 'r') as f:
        return json.load(f)

def get_db_connection():
    """Create database connection"""
    config = load_config()
    return psycopg2.connect(
        host=config['database']['host'],
        port=config['database']['port'],
        database=config['database']['database'],
        user=config['database']['user'],
        password=config['database']['password']
    )

def clean_utf8_data(value):
    """Clean UTF8 null bytes and other problematic characters"""
    if pd.isna(value) or value is None:
        return None
    
    # Convert to string and clean
    str_value = str(value).strip()
    
    # Remove null bytes and other problematic characters
    cleaned = str_value.replace('\x00', '').replace('\r', '').replace('\n', ' ')
    
    # Return None for empty strings
    return cleaned if cleaned else None

def process_chunk(args):
    """Process a single chunk of data"""
    chunk_data, chunk_id, total_chunks = args
    
    # MVP FIELD MAPPING - 19 Core Fields Only
    field_mapping = {
        # Core identifiers  
        'Quantarium_Internal_PID': 'quantarium_internal_pid',
        'Assessors_Parcel_Number': 'apn', 
        'FIPS_Code': 'fips_code',
        
        # Address matching
        'Property_Full_Street_Address': 'property_full_street_address',
        'Property_City_Name': 'property_city_name',
        'Property_State': 'property_state', 
        'Property_Zip_Code': 'property_zip_code',
        
        # Location
        'PA_Latitude': 'latitude',
        'PA_Longitude': 'longitude',
        
        # Valuation (core business)
        'ESTIMATED_VALUE': 'estimated_value',
        'PRICE_RANGE_MIN': 'price_range_min', 
        'PRICE_RANGE_MAX': 'price_range_max',
        'CONFIDENCE_SCORE': 'confidence_score',
        
        # Bonus property data
        'Current_Owner_Name': 'current_owner_name',
        'LotSize_Square_Feet': 'lot_size_square_feet',
        'Building_Area_1': 'building_area_total',
        'Number_of_Bedrooms': 'number_of_bedrooms', 
        'Year_Built': 'year_built',
        'LSale_Price': 'lsale_price'
    }
    
    try:
        logger.info(f"🔄 Processing chunk {chunk_id}/{total_chunks} - {len(chunk_data)} rows")
        
        # Create processed dataframe with only MVP fields
        processed_data = []
        
        for _, row in chunk_data.iterrows():
            processed_row = {}
            
            # Process each MVP field
            for tsv_col, db_col in field_mapping.items():
                if tsv_col in row.index:
                    raw_value = row[tsv_col]
                    cleaned_value = clean_utf8_data(raw_value)
                    processed_row[db_col] = cleaned_value
                else:
                    # Field not present in TSV - set to None
                    processed_row[db_col] = None
            
            processed_data.append(processed_row)
        
        # Convert to DataFrame
        df_processed = pd.DataFrame(processed_data)
        
        # Create temporary CSV file for COPY
        with tempfile.NamedTemporaryFile(mode='w', suffix='.csv', delete=False, encoding='utf-8') as temp_file:
            # Write CSV with explicit null handling
            df_processed.to_csv(
                temp_file.name, 
                index=False, 
                header=False,
                na_rep='\\N',  # PostgreSQL null representation
                sep='\t'
            )
            temp_csv_path = temp_file.name
        
        # Load into database
        conn = get_db_connection()
        cursor = conn.cursor()
        
        # Set schema
        cursor.execute("SET search_path TO datnest, public")
        
        # Get column names in order
        columns = list(field_mapping.values())
        columns_str = ', '.join(columns)
        
        # COPY command
        with open(temp_csv_path, 'r', encoding='utf-8') as f:
            cursor.copy_from(
                f, 
                'properties', 
                columns=(columns_str,),
                sep='\t',
                null='\\N'
            )
        
        conn.commit()
        cursor.close()
        conn.close()
        
        # Clean up temp file
        os.unlink(temp_csv_path)
        
        logger.info(f"✅ Chunk {chunk_id}/{total_chunks} completed - {len(df_processed)} records loaded")
        return len(df_processed)
        
    except Exception as e:
        logger.error(f"❌ Chunk {chunk_id}/{total_chunks} failed: {str(e)}")
        # Clean up temp file if it exists
        if 'temp_csv_path' in locals():
            try:
                os.unlink(temp_csv_path)
            except:
                pass
        return 0

def main():
    """Main execution function"""
    start_time = time.time()
    
    logger.info("🚀 STARTING MVP CLEAN LOADER")
    logger.info("📋 Strategy: 19 core fields, no problematic columns, UTF8 cleaning")
    logger.info("🎯 Target: 5M records for client valuation MVP")
    
    # Configuration
    tsv_file = r'C:\DataNest-TSV-Files\extracted-tsv\Quantarium_OpenLien_20250414_00001.TSV'
    chunk_size = 100000  # 100K chunks for optimal performance
    max_workers = max(1, int(mp.cpu_count() * 0.8))  # Use 80% of CPU cores
    
    logger.info(f"📊 Configuration: {chunk_size:,} chunk size, {max_workers} workers")
    
    # Clear existing data
    logger.info("🧹 Clearing existing data...")
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("SET search_path TO datnest, public")
    cursor.execute("TRUNCATE TABLE properties")
    conn.commit()
    cursor.close()
    conn.close()
    logger.info("✅ Database cleared")
    
    # Process file in chunks
    logger.info(f"📖 Reading TSV file: {tsv_file}")
    chunk_args = []
    total_rows = 0
    
    # Read file in chunks and prepare for multiprocessing
    for chunk_id, chunk in enumerate(pd.read_csv(
        tsv_file, 
        sep='\t', 
        chunksize=chunk_size, 
        dtype=str,              # Treat all columns as strings
        encoding='utf-8',
        engine='python',
        quoting=csv.QUOTE_NONE, # Don't parse quotes (handles large fields)
        on_bad_lines='skip',    # Skip malformed rows
        na_values=['']          # Empty strings as NaN
    ), 1):
        chunk_args.append((chunk, chunk_id, 0))  # Will update total_chunks later
        total_rows += len(chunk)
    
    total_chunks = len(chunk_args)
    
    # Update chunk args with correct total_chunks
    chunk_args = [(chunk_data, chunk_id, total_chunks) for chunk_data, chunk_id, _ in chunk_args]
    
    logger.info(f"📈 Total: {total_rows:,} rows in {total_chunks} chunks")
    
    # Process chunks with multiprocessing
    logger.info(f"⚡ Starting multiprocessing with {max_workers} workers...")
    
    total_loaded = 0
    start_processing = time.time()
    
    with ProcessPoolExecutor(max_workers=max_workers) as executor:
        results = list(executor.map(process_chunk, chunk_args))
    
    total_loaded = sum(results)
    processing_time = time.time() - start_processing
    
    # Final statistics
    total_time = time.time() - start_time
    records_per_second = total_loaded / processing_time if processing_time > 0 else 0
    
    logger.info("🏆 MVP CLEAN LOADER COMPLETE!")
    logger.info(f"📊 Total records loaded: {total_loaded:,}")
    logger.info(f"📊 Total records processed: {total_rows:,}")
    logger.info(f"📊 Success rate: {(total_loaded/total_rows)*100:.1f}%")
    logger.info(f"⚡ Processing time: {processing_time:.1f} seconds")
    logger.info(f"⚡ Performance: {records_per_second:.0f} records/second")
    logger.info(f"🕒 Total runtime: {total_time:.1f} seconds")
    
    if total_loaded == total_rows:
        logger.info("🎉 PERFECT SUCCESS - NO DATA LOSS!")
    else:
        logger.warning(f"⚠️ Data loss: {total_rows - total_loaded:,} records")

if __name__ == "__main__":
    main()