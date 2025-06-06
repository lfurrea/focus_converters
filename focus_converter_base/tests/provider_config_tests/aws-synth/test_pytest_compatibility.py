# test_pytest_compatibility.py
"""
Updated pytest compatibility tests for AWS-Synth provider
Validates that all configuration files exist and load correctly with the latest implementation
"""

import pytest
import sys
from pathlib import Path

# Add focus_converter_base to path
focus_converter_base = Path(__file__).parent.parent.parent.parent
sys.path.insert(0, str(focus_converter_base))

# Import required modules
from focus_converter.converter import FocusConverter
from focus_converter.configs.base_config import ConversionPlan
from focus_converter.data_loaders.data_loader import DataFormats
import polars as pl
import pyarrow.dataset as ds


def test_imports():
    """Test that all required imports work"""
    try:
        # Test imports are already done above, but verify they work
        assert FocusConverter is not None
        assert ConversionPlan is not None
        assert DataFormats is not None
        assert pl is not None
        assert ds is not None
        
        # Test that we can create instances
        converter = FocusConverter()
        assert converter is not None
        
    except ImportError as e:
        pytest.fail(f"Import failed: {e}")
    except Exception as e:
        pytest.fail(f"Import validation failed: {e}")


def test_focus_converter_loads():
    """Test that FocusConverter can load configurations"""
    try:
        converter = FocusConverter()
        converter.load_provider_conversion_configs()
        assert "aws-synth" in converter.plans, "aws-synth provider not found in loaded plans"
        assert len(converter.plans["aws-synth"]) > 0, "No configurations loaded for aws-synth"
    except Exception as e:
        pytest.fail(f"FocusConverter failed to load: {e}")


def test_aws_synth_config_files_exist():
    """Test that AWS-Synth configuration files exist and can be loaded"""
    config_files = [
        # Core configuration files based on actual implementation
        "focus_converter/conversion_configs/aws-synth/0_dimension_dtypes_S001.yaml",
        "focus_converter/conversion_configs/aws-synth/provider_S001.yaml",
        "focus_converter/conversion_configs/aws-synth/focus_version_S001.yaml",
        "focus_converter/conversion_configs/aws-synth/line_item_id_S001.yaml",
        "focus_converter/conversion_configs/aws-synth/billing_period_start_S001.yaml",
        "focus_converter/conversion_configs/aws-synth/billing_period_end_S001.yaml",
        "focus_converter/conversion_configs/aws-synth/charge_period_start_S001.yaml",
        "focus_converter/conversion_configs/aws-synth/charge_period_end_S001.yaml",
        "focus_converter/conversion_configs/aws-synth/service_name_S001.yaml",
        "focus_converter/conversion_configs/aws-synth/sub_account_id_S001.yaml",
        "focus_converter/conversion_configs/aws-synth/billing_account_id_S001.yaml",
        "focus_converter/conversion_configs/aws-synth/billing_account_name_S001.yaml",
        "focus_converter/conversion_configs/aws-synth/resource_id_S001.yaml",
        "focus_converter/conversion_configs/aws-synth/effective_cost_S001.yaml",
        "focus_converter/conversion_configs/aws-synth/billed_cost_S001.yaml",
        "focus_converter/conversion_configs/aws-synth/consumed_quantity_S001.yaml",
        "focus_converter/conversion_configs/aws-synth/consumed_unit_S001.yaml",
        "focus_converter/conversion_configs/aws-synth/billing_currency_S001.yaml",
        "focus_converter/conversion_configs/aws-synth/region_id_S001.yaml",
        "focus_converter/conversion_configs/aws-synth/availability_zone_S001.yaml",
        "focus_converter/conversion_configs/aws-synth/service_category_S001.yaml",
        "focus_converter/conversion_configs/aws-synth/tags_S001.yaml",
        "focus_converter/conversion_configs/aws-synth/updatedAt_S001.yaml"
    ]
    
    for config_file in config_files:
        try:
            plan = ConversionPlan.load_yaml(config_file)
            assert plan is not None, f"Failed to load {config_file}"
            assert hasattr(plan, 'conversion_type'), f"Invalid plan structure in {config_file}"
        except Exception as e:
            pytest.fail(f"Failed to load config {config_file}: {e}")


def test_aws_synth_conversion_types():
    """Test that AWS-Synth configurations use correct conversion types"""
    expected_conversion_types = {
        "focus_converter/conversion_configs/aws-synth/0_dimension_dtypes_S001.yaml": "SET_COLUMN_DTYPES",
        "focus_converter/conversion_configs/aws-synth/provider_S001.yaml": "ASSIGN_STATIC_VALUE",
        "focus_converter/conversion_configs/aws-synth/focus_version_S001.yaml": "ASSIGN_STATIC_VALUE",
        "focus_converter/conversion_configs/aws-synth/line_item_id_S001.yaml": "RENAME_COLUMN",
        "focus_converter/conversion_configs/aws-synth/billing_period_start_S001.yaml": "PARSE_DATETIME",
        "focus_converter/conversion_configs/aws-synth/billing_period_end_S001.yaml": "PARSE_DATETIME",
        "focus_converter/conversion_configs/aws-synth/charge_period_start_S001.yaml": "PARSE_DATETIME",
        "focus_converter/conversion_configs/aws-synth/charge_period_end_S001.yaml": "PARSE_DATETIME",
        "focus_converter/conversion_configs/aws-synth/service_name_S001.yaml": "RENAME_COLUMN",
        "focus_converter/conversion_configs/aws-synth/sub_account_id_S001.yaml": "RENAME_COLUMN",
        "focus_converter/conversion_configs/aws-synth/billing_account_id_S001.yaml": "RENAME_COLUMN",
        "focus_converter/conversion_configs/aws-synth/billing_account_name_S001.yaml": "SQL_CONDITION",
        "focus_converter/conversion_configs/aws-synth/resource_id_S001.yaml": "RENAME_COLUMN",
        "focus_converter/conversion_configs/aws-synth/effective_cost_S001.yaml": "RENAME_COLUMN",
        "focus_converter/conversion_configs/aws-synth/billed_cost_S001.yaml": "RENAME_COLUMN",
        "focus_converter/conversion_configs/aws-synth/consumed_quantity_S001.yaml": "RENAME_COLUMN",
        "focus_converter/conversion_configs/aws-synth/consumed_unit_S001.yaml": "RENAME_COLUMN",
        "focus_converter/conversion_configs/aws-synth/billing_currency_S001.yaml": "SQL_CONDITION",
        "focus_converter/conversion_configs/aws-synth/region_id_S001.yaml": "RENAME_COLUMN",
        "focus_converter/conversion_configs/aws-synth/availability_zone_S001.yaml": "RENAME_COLUMN",
        "focus_converter/conversion_configs/aws-synth/service_category_S001.yaml": "SQL_CONDITION",
        "focus_converter/conversion_configs/aws-synth/tags_S001.yaml": "RENAME_COLUMN",
        "focus_converter/conversion_configs/aws-synth/updatedAt_S001.yaml": "PARSE_DATETIME"
    }
    
    for config_file, expected_type in expected_conversion_types.items():
        try:
            plan = ConversionPlan.load_yaml(config_file)
            actual_type = plan.conversion_type.name
            assert actual_type == expected_type, f"Config {config_file} has type {actual_type}, expected {expected_type}"
        except Exception as e:
            pytest.fail(f"Failed to validate conversion type for {config_file}: {e}")


def test_aws_synth_focus_columns():
    """Test that AWS-Synth configurations map to correct FOCUS columns"""
    expected_focus_columns = {
        "focus_converter/conversion_configs/aws-synth/provider_S001.yaml": "Provider",
        "focus_converter/conversion_configs/aws-synth/billing_period_start_S001.yaml": "BillingPeriodStart",
        "focus_converter/conversion_configs/aws-synth/billing_period_end_S001.yaml": "BillingPeriodEnd",
        "focus_converter/conversion_configs/aws-synth/charge_period_start_S001.yaml": "ChargePeriodStart",
        "focus_converter/conversion_configs/aws-synth/charge_period_end_S001.yaml": "ChargePeriodEnd",
        "focus_converter/conversion_configs/aws-synth/service_name_S001.yaml": "ServiceName",
        "focus_converter/conversion_configs/aws-synth/sub_account_id_S001.yaml": "SubAccountId",
        "focus_converter/conversion_configs/aws-synth/billing_account_id_S001.yaml": "BillingAccountId",
        "focus_converter/conversion_configs/aws-synth/billing_account_name_S001.yaml": "BillingAccountName",
        "focus_converter/conversion_configs/aws-synth/resource_id_S001.yaml": "ResourceId",
        "focus_converter/conversion_configs/aws-synth/effective_cost_S001.yaml": "EffectiveCost",
        "focus_converter/conversion_configs/aws-synth/billed_cost_S001.yaml": "BilledCost",
        "focus_converter/conversion_configs/aws-synth/consumed_quantity_S001.yaml": "ConsumedQuantity",
        "focus_converter/conversion_configs/aws-synth/consumed_unit_S001.yaml": "ConsumedUnit",
        "focus_converter/conversion_configs/aws-synth/billing_currency_S001.yaml": "BillingCurrency",
        "focus_converter/conversion_configs/aws-synth/region_id_S001.yaml": "RegionId",
        "focus_converter/conversion_configs/aws-synth/availability_zone_S001.yaml": "AvailabilityZone",
        "focus_converter/conversion_configs/aws-synth/service_category_S001.yaml": "ServiceCategory"
    }
    
    for config_file, expected_focus_column in expected_focus_columns.items():
        try:
            plan = ConversionPlan.load_yaml(config_file)
            actual_focus_column = plan.focus_column.value
            assert actual_focus_column == expected_focus_column, f"Config {config_file} maps to {actual_focus_column}, expected {expected_focus_column}"
        except Exception as e:
            pytest.fail(f"Failed to validate FOCUS column for {config_file}: {e}")


def test_aws_synth_required_columns_covered():
    """Test that all Postgres table required columns are covered by AWS-Synth configurations"""
    try:
        converter = FocusConverter()
        converter.load_provider_conversion_configs()
        converter.prepare_horizontal_conversion_plan("aws-synth")
        
        # Required columns for Postgres table focus_line_items
        postgres_required_columns = {
            "Provider",           # providerName
            "BillingPeriodStart", # billing_period_start  
            "ChargePeriodStart",  # chargeDate
            "ServiceName",        # serviceName
            "SubAccountId",       # usageAccountId
            "EffectiveCost",      # effectiveCost
            "BillingCurrency"     # currencyCode
        }
        
        # Optional but important columns
        postgres_optional_columns = {
            "BillingAccountId",   # payerAccountId
            "ResourceId",         # resourceId
            "ConsumedQuantity",   # usageQuantity
            "RegionId",           # region
            "AvailabilityZone",   # availabilityZone
            "ServiceCategory",    # productFamily (mapped from conversion)
            "ConsumedUnit"        # pricingUnit
        }
        
        collected_columns = set(converter.h_collected_columns)
        
        # Check required columns
        missing_required = postgres_required_columns - collected_columns
        assert len(missing_required) == 0, f"Missing required columns: {missing_required}"
        
        # Check optional columns (should have most of them)
        missing_optional = postgres_optional_columns - collected_columns
        coverage_ratio = (len(postgres_optional_columns) - len(missing_optional)) / len(postgres_optional_columns)
        assert coverage_ratio >= 0.8, f"Low coverage of optional columns: {coverage_ratio:.2%}, missing: {missing_optional}"
        
    except Exception as e:
        pytest.fail(f"Failed to test column coverage: {e}")


if __name__ == "__main__":
    # Run with pytest when called directly
    pytest.main([__file__, "-v"])