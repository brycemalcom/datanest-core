"""
DatNest Core Platform - TSV Field Mapping System
Maps 400+ TSV fields to optimized PostgreSQL schema with QVM focus
"""

from typing import Dict, Any, Optional, Union, List
from dataclasses import dataclass
from datetime import datetime
import logging

logger = logging.getLogger(__name__)

@dataclass
class FieldMapping:
    """Represents a mapping from TSV field to database field"""
    tsv_field: str
    db_table: str
    db_field: str
    data_type: str
    is_required: bool = False
    is_tier1: bool = False  # QVM and core business fields
    transformation: Optional[str] = None
    validation_rule: Optional[str] = None
    default_value: Optional[Any] = None
    max_length: Optional[int] = None

class TSVFieldMapper:
    """
    Handles mapping between TSV fields and database schema
    Based on prototype lessons and optimized for 150M+ records
    """
    
    def __init__(self):
        self.field_mappings = self._initialize_field_mappings()
        self.tier1_fields = [f for f in self.field_mappings if f.is_tier1]
        self.tier2_fields = [f for f in self.field_mappings if not f.is_tier1 and f.is_required]
        self.tier3_fields = [f for f in self.field_mappings if not f.is_tier1 and not f.is_required]
    
    def _initialize_field_mappings(self) -> List[FieldMapping]:
        """Initialize all field mappings based on TSV schema and prototype lessons"""
        mappings = []
        
        # =====================================================
        # TIER 1: QVM VALUATION FIELDS (HIGHEST PRIORITY)
        # =====================================================
        
        qvm_mappings = [
            FieldMapping(
                tsv_field="Quantarium Value",
                db_table="properties",
                db_field="estimated_value",
                data_type="DECIMAL(12,2)",
                is_required=True,
                is_tier1=True,
                validation_rule="value > 0",
                transformation="clean_currency"
            ),
            FieldMapping(
                tsv_field="Quantarium Value High",
                db_table="properties",
                db_field="price_range_max",
                data_type="DECIMAL(12,2)",
                is_tier1=True,
                transformation="clean_currency"
            ),
            FieldMapping(
                tsv_field="Quantarium Value Low",
                db_table="properties",
                db_field="price_range_min",
                data_type="DECIMAL(12,2)",
                is_tier1=True,
                transformation="clean_currency"
            ),
            FieldMapping(
                tsv_field="Quantarium Value Confidence",
                db_table="properties",
                db_field="confidence_score",
                data_type="INTEGER",
                is_tier1=True,
                validation_rule="value >= 0 AND value <= 100"
            ),
            FieldMapping(
                tsv_field="QVM_asof_Date",
                db_table="properties",
                db_field="qvm_asof_date",
                data_type="DATE",
                is_tier1=True,
                transformation="parse_date"
            ),
        ]
        mappings.extend(qvm_mappings)
        
        # =====================================================
        # TIER 1: CORE PROPERTY IDENTIFIERS
        # =====================================================
        
        identifier_mappings = [
            FieldMapping(
                tsv_field="Quantarium_Internal_PID",
                db_table="properties",
                db_field="quantarium_internal_pid",
                data_type="VARCHAR(100)",
                is_required=True,
                is_tier1=True,
                max_length=100
            ),
            FieldMapping(
                tsv_field="Assessors_Parcel_Number",
                db_table="properties",
                db_field="apn",
                data_type="VARCHAR(100)",
                is_required=True,
                is_tier1=True,
                max_length=100,
                transformation="clean_apn"
            ),
            FieldMapping(
                tsv_field="FIPS_Code",
                db_table="properties",
                db_field="fips_code",
                data_type="VARCHAR(10)",
                is_required=True,
                is_tier1=True,
                max_length=10
            ),
        ]
        mappings.extend(identifier_mappings)
        
        # =====================================================
        # TIER 1: PROPERTY LOCATION
        # =====================================================
        
        location_mappings = [
            FieldMapping(
                tsv_field="Property_Full_Street_Address",
                db_table="properties",
                db_field="property_full_street_address",
                data_type="VARCHAR(200)",
                is_tier1=True,
                max_length=200,
                transformation="clean_address"
            ),
            FieldMapping(
                tsv_field="Property_City_Name",
                db_table="properties",
                db_field="property_city_name",
                data_type="VARCHAR(100)",
                is_tier1=True,
                max_length=100,
                transformation="clean_city"
            ),
            FieldMapping(
                tsv_field="Property_State",
                db_table="properties",
                db_field="property_state",
                data_type="CHAR(2)",
                is_tier1=True,
                max_length=2,
                transformation="clean_state",
                validation_rule="LENGTH(value) = 2"
            ),
            FieldMapping(
                tsv_field="Property_Zip_Code",
                db_table="properties",
                db_field="property_zip_code",
                data_type="CHAR(5)",
                is_tier1=True,
                max_length=5,
                transformation="clean_zipcode",
                validation_rule="LENGTH(value) = 5"
            ),
        ]
        mappings.extend(location_mappings)
        
        # =====================================================
        # TIER 1: PROPERTY CHARACTERISTICS
        # =====================================================
        
        characteristic_mappings = [
            FieldMapping(
                tsv_field="Building_Area_1",
                db_table="properties",
                db_field="building_area_total",
                data_type="DECIMAL(10,0)",
                is_tier1=True,
                transformation="clean_numeric",
                validation_rule="value > 0"
            ),
            FieldMapping(
                tsv_field="LotSize_Square_Feet",
                db_table="properties",
                db_field="lot_size_square_feet",
                data_type="DECIMAL(12,2)",
                is_tier1=True,
                transformation="clean_numeric"
            ),
            FieldMapping(
                tsv_field="Number of Bedroom",
                db_table="properties",
                db_field="number_of_bedrooms",
                data_type="INTEGER",
                is_tier1=True,
                transformation="clean_integer",
                validation_rule="value >= 0 AND value <= 20"
            ),
            FieldMapping(
                tsv_field="Number of Baths",
                db_table="properties",
                db_field="number_of_bathrooms",
                data_type="DECIMAL(4,2)",
                is_tier1=True,
                transformation="clean_decimal"
            ),
        ]
        mappings.extend(characteristic_mappings)
        
        return mappings
    
    def get_field_mapping(self, tsv_field: str) -> Optional[FieldMapping]:
        """Get mapping for a specific TSV field"""
        for mapping in self.field_mappings:
            if mapping.tsv_field == tsv_field:
                return mapping
        return None
    
    def get_tier1_mappings(self) -> List[FieldMapping]:
        """Get only Tier 1 (highest priority) field mappings"""
        return self.tier1_fields
    
    def validate_tsv_headers(self, headers: List[str]) -> Dict[str, Any]:
        """
        Validate TSV headers against expected schema
        Returns coverage statistics and missing fields
        """
        mapped_headers = set()
        tier1_found = set()
        tier1_missing = set()
        
        for header in headers:
            mapping = self.get_field_mapping(header)
            if mapping:
                mapped_headers.add(header)
                if mapping.is_tier1:
                    tier1_found.add(header)
        
        # Check for missing Tier 1 fields
        for mapping in self.tier1_fields:
            if mapping.tsv_field not in headers:
                tier1_missing.add(mapping.tsv_field)
        
        total_expected = len(self.field_mappings)
        total_tier1 = len(self.tier1_fields)
        
        return {
            "total_headers": len(headers),
            "mapped_headers": len(mapped_headers),
            "unmapped_headers": len(headers) - len(mapped_headers),
            "coverage_percentage": (len(mapped_headers) / total_expected) * 100,
            "tier1_found": len(tier1_found),
            "tier1_missing": len(tier1_missing),
            "tier1_coverage": (len(tier1_found) / total_tier1) * 100,
            "missing_tier1_fields": list(tier1_missing),
            "unmapped_headers_list": [h for h in headers if h not in [m.tsv_field for m in self.field_mappings]]
        }

# Singleton instance for global use
tsv_field_mapper = TSVFieldMapper()

def get_field_mapper() -> TSVFieldMapper:
    """Get the global field mapper instance"""
    return tsv_field_mapper 