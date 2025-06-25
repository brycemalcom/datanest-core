#!/usr/bin/env python3
"""
Lambda function to deploy DatNest database schema
"""
import json
import psycopg2
import boto3

def lambda_handler(event, context):
    # Get database credentials from Secrets Manager
    secrets_client = boto3.client('secretsmanager')
    
    try:
        response = secrets_client.get_secret_value(
            SecretId='datnest-core/db/credentials'
        )
        db_creds = json.loads(response['SecretString'])
        
        # Connect to PostgreSQL
        conn = psycopg2.connect(
            host=db_creds['host'],
            port=db_creds['port'],
            database=db_creds['dbname'],
            user=db_creds['username'],
            password=db_creds['password']
        )
        cursor = conn.cursor()
        
        # Database schema SQL (optimized for 150M+ records)
        schema_sql = """
        -- DatNest Core Platform Database Schema
        -- Optimized for 150M+ property records with QVM prioritization
        
        -- Properties table (core property data)
        CREATE TABLE IF NOT EXISTS properties (
            quantarium_internal_pid VARCHAR(50) PRIMARY KEY,
            fips_code VARCHAR(10),
            assessors_parcel_number VARCHAR(100),
            property_full_street_address TEXT,
            property_city_name VARCHAR(100),
            property_state VARCHAR(5),
            property_zip_code VARCHAR(10),
            
            -- QVM Fields (Tier 1 Priority)
            estimated_value DECIMAL(15,2),
            confidence_score DECIMAL(5,2),
            fsd_score DECIMAL(5,2),
            price_range_min DECIMAL(15,2),
            price_range_max DECIMAL(15,2),
            qvm_value_range_code VARCHAR(10),
            qvm_asof_date DATE,
            
            -- Property details
            year_built INTEGER,
            total_assessed_value DECIMAL(15,2),
            total_market_value DECIMAL(15,2),
            building_area INTEGER,
            lot_size_square_feet INTEGER,
            number_of_bedrooms INTEGER,
            number_of_baths DECIMAL(3,1),
            
            -- Metadata
            record_creation_date DATE,
            trans_asof_date DATE,
            quantarium_version VARCHAR(20),
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        );
        
        -- Mortgages table (financing data)
        CREATE TABLE IF NOT EXISTS mortgages (
            id SERIAL PRIMARY KEY,
            quantarium_internal_pid VARCHAR(50) REFERENCES properties(quantarium_internal_pid),
            mortgage_number INTEGER,
            lender_name TEXT,
            loan_amount DECIMAL(15,2),
            interest_rate DECIMAL(5,4),
            loan_type VARCHAR(50),
            recording_date DATE,
            original_date_of_contract DATE,
            curr_est_balance DECIMAL(15,2),
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        );
        
        -- Performance Indexes (optimized for QVM queries)
        CREATE INDEX IF NOT EXISTS idx_properties_qvm_value ON properties(estimated_value) WHERE estimated_value IS NOT NULL;
        CREATE INDEX IF NOT EXISTS idx_properties_confidence ON properties(confidence_score) WHERE confidence_score IS NOT NULL;
        CREATE INDEX IF NOT EXISTS idx_properties_fips ON properties(fips_code);
        CREATE INDEX IF NOT EXISTS idx_properties_zip ON properties(property_zip_code);
        CREATE INDEX IF NOT EXISTS idx_properties_address_gin ON properties USING gin(to_tsvector('english', property_full_street_address));
        CREATE INDEX IF NOT EXISTS idx_mortgages_pid ON mortgages(quantarium_internal_pid);
        CREATE INDEX IF NOT EXISTS idx_mortgages_amount ON mortgages(loan_amount);
        
        -- QVM Analytics View
        CREATE OR REPLACE VIEW qvm_analytics AS
        SELECT 
            p.fips_code,
            p.property_state,
            p.property_zip_code,
            COUNT(*) as total_properties,
            COUNT(p.estimated_value) as properties_with_qvm,
            ROUND(AVG(p.estimated_value), 2) as avg_estimated_value,
            ROUND(AVG(p.confidence_score), 2) as avg_confidence_score,
            MIN(p.estimated_value) as min_value,
            MAX(p.estimated_value) as max_value
        FROM properties p
        WHERE p.estimated_value IS NOT NULL
        GROUP BY p.fips_code, p.property_state, p.property_zip_code;
        """
        
        # Execute schema
        cursor.execute(schema_sql)
        conn.commit()
        
        # Verify tables
        cursor.execute("""
            SELECT table_name 
            FROM information_schema.tables 
            WHERE table_schema = 'public' 
            ORDER BY table_name;
        """)
        tables = [row[0] for row in cursor.fetchall()]
        
        cursor.close()
        conn.close()
        
        return {
            'statusCode': 200,
            'body': json.dumps({
                'message': 'Database schema deployed successfully!',
                'tables_created': tables
            })
        }
        
    except Exception as e:
        return {
            'statusCode': 500,
            'body': json.dumps({
                'error': str(e)
            })
        } 