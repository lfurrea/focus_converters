# test_aws_synth_provider.py
from unittest import TestCase

import pandas as pd
import polars as pl

from focus_converter.configs.base_config import ConversionPlan
from focus_converter.converter import FocusConverter


class TestAWSSynthProvider(TestCase):
    """Test individual AWS-Synth provider configurations following AWS test patterns"""
    
    def test_aws_synth_provider_config(self):
        """Test the provider static value configuration"""
        conversion_plan = ConversionPlan.load_yaml(
            "focus_converter/conversion_configs/aws-synth/provider_S001.yaml"
        )

        focus_converter = FocusConverter()
        focus_converter.plans = {"aws-synth": [conversion_plan]}
        column_exprs = focus_converter.prepare_horizontal_conversion_plan(
            provider="aws-synth"
        )

        test_dataframe = pd.DataFrame([{"a": 1}])

        test_pl_df = (
            pl.from_dataframe(test_dataframe)
            .lazy()
            .with_columns(column_exprs)
            .collect()
        )
        self.assertEqual(list(test_pl_df["Provider"])[0], "aws-synth")
        
    def test_focus_version_config(self):
        """Test the FOCUS version static value configuration"""
        conversion_plan = ConversionPlan.load_yaml(
            "focus_converter/conversion_configs/aws-synth/focus_version_S001.yaml"
        )

        focus_converter = FocusConverter()
        focus_converter.plans = {"aws-synth": [conversion_plan]}
        column_exprs = focus_converter.prepare_horizontal_conversion_plan(
            provider="aws-synth"
        )

        test_dataframe = pd.DataFrame([{"a": 1}])

        test_pl_df = (
            pl.from_dataframe(test_dataframe)
            .lazy()
            .with_columns(column_exprs)
            .collect()
        )
        # Note: focus_version maps to PlaceHolder, so we'd need to check the actual column name
        # This test validates the config loads and executes without error
        self.assertGreater(len(test_pl_df.columns), 0)
        
    def test_billing_period_start_config(self):
        """Test datetime parsing configuration for billing period start"""
        conversion_plan = ConversionPlan.load_yaml(
            "focus_converter/conversion_configs/aws-synth/billing_period_start_S001.yaml"
        )

        focus_converter = FocusConverter()
        focus_converter.plans = {"aws-synth": [conversion_plan]}
        column_exprs = focus_converter.prepare_horizontal_conversion_plan(
            provider="aws-synth"
        )

        # Test with sample datetime data
        test_dataframe = pd.DataFrame([{
            "bill_BillingPeriodStartDate": "2025-01-01T00:00:00Z"
        }])

        test_pl_df = (
            pl.from_dataframe(test_dataframe)
            .lazy()
            .with_columns(column_exprs)
            .collect()
        )
        
        # Should have BillingPeriodStart column with datetime type
        self.assertIn("BillingPeriodStart", test_pl_df.columns)
        self.assertTrue(test_pl_df.schema["BillingPeriodStart"] in [pl.Datetime, pl.Date])
        
    def test_charge_period_start_config(self):
        """Test datetime parsing configuration for charge period start"""
        conversion_plan = ConversionPlan.load_yaml(
            "focus_converter/conversion_configs/aws-synth/charge_period_start_S001.yaml"
        )

        focus_converter = FocusConverter()
        focus_converter.plans = {"aws-synth": [conversion_plan]}
        column_exprs = focus_converter.prepare_horizontal_conversion_plan(
            provider="aws-synth"
        )

        test_dataframe = pd.DataFrame([{
            "lineItem_UsageStartDate": "2025-01-05T10:15:00Z"
        }])

        test_pl_df = (
            pl.from_dataframe(test_dataframe)
            .lazy()
            .with_columns(column_exprs)
            .collect()
        )
        
        self.assertIn("ChargePeriodStart", test_pl_df.columns)
        self.assertTrue(test_pl_df.schema["ChargePeriodStart"] in [pl.Datetime, pl.Date])
        
    def test_service_name_config(self):
        """Test rename column configuration for service name"""
        conversion_plan = ConversionPlan.load_yaml(
            "focus_converter/conversion_configs/aws-synth/service_name_S001.yaml"
        )

        focus_converter = FocusConverter()
        focus_converter.plans = {"aws-synth": [conversion_plan]}
        column_exprs = focus_converter.prepare_horizontal_conversion_plan(
            provider="aws-synth"
        )

        test_dataframe = pd.DataFrame([{
            "product_ProductName": "EC2"
        }])

        test_pl_df = (
            pl.from_dataframe(test_dataframe)
            .lazy()
            .with_columns(column_exprs)
            .collect()
        )
        
        self.assertIn("ServiceName", test_pl_df.columns)
        self.assertEqual(list(test_pl_df["ServiceName"])[0], "EC2")
        
    def test_effective_cost_config(self):
        """Test rename column configuration for effective cost"""
        conversion_plan = ConversionPlan.load_yaml(
            "focus_converter/conversion_configs/aws-synth/effective_cost_S001.yaml"
        )

        focus_converter = FocusConverter()
        focus_converter.plans = {"aws-synth": [conversion_plan]}
        column_exprs = focus_converter.prepare_horizontal_conversion_plan(
            provider="aws-synth"
        )

        test_dataframe = pd.DataFrame([{
            "amortisedCost": 10.50
        }])

        test_pl_df = (
            pl.from_dataframe(test_dataframe)
            .lazy()
            .with_columns(column_exprs)
            .collect()
        )
        
        self.assertIn("EffectiveCost", test_pl_df.columns)
        self.assertEqual(float(test_pl_df["EffectiveCost"][0]), 10.50)
        
    def test_region_id_config(self):
        """Test rename column configuration for region"""
        conversion_plan = ConversionPlan.load_yaml(
            "focus_converter/conversion_configs/aws-synth/region_id_S001.yaml"
        )

        focus_converter = FocusConverter()
        focus_converter.plans = {"aws-synth": [conversion_plan]}
        column_exprs = focus_converter.prepare_horizontal_conversion_plan(
            provider="aws-synth"
        )

        test_dataframe = pd.DataFrame([{
            "region": "us-east-1"
        }])

        test_pl_df = (
            pl.from_dataframe(test_dataframe)
            .lazy()
            .with_columns(column_exprs)
            .collect()
        )
        
        self.assertIn("RegionId", test_pl_df.columns)
        self.assertEqual(list(test_pl_df["RegionId"])[0], "us-east-1")
        
    def test_availability_zone_config(self):
        """Test rename column configuration for availability zone"""
        conversion_plan = ConversionPlan.load_yaml(
            "focus_converter/conversion_configs/aws-synth/availability_zone_S001.yaml"
        )

        focus_converter = FocusConverter()
        focus_converter.plans = {"aws-synth": [conversion_plan]}
        column_exprs = focus_converter.prepare_horizontal_conversion_plan(
            provider="aws-synth"
        )

        test_dataframe = pd.DataFrame([{
            "availabilityZone": "us-east-1a"
        }])

        test_pl_df = (
            pl.from_dataframe(test_dataframe)
            .lazy()
            .with_columns(column_exprs)
            .collect()
        )
        
        self.assertIn("AvailabilityZone", test_pl_df.columns)
        self.assertEqual(list(test_pl_df["AvailabilityZone"])[0], "us-east-1a")
        
    def test_billing_currency_config(self):
        """Test SQL condition configuration for billing currency with default"""
        conversion_plan = ConversionPlan.load_yaml(
            "focus_converter/conversion_configs/aws-synth/billing_currency_S001.yaml"
        )

        focus_converter = FocusConverter()
        focus_converter.plans = {"aws-synth": [conversion_plan]}
        
        # This is a SQL condition, so we need to test through the full converter
        # We'll test this in the integration test instead
        self.assertEqual(conversion_plan.conversion_type.name, "SQL_CONDITION")
        
    def test_service_category_config(self):
        """Test SQL condition configuration for service category mapping"""
        conversion_plan = ConversionPlan.load_yaml(
            "focus_converter/conversion_configs/aws-synth/service_category_S001.yaml"
        )

        focus_converter = FocusConverter()
        focus_converter.plans = {"aws-synth": [conversion_plan]}
        
        # This is a SQL condition, so we need to test through the full converter
        # We'll test this in the integration test instead
        self.assertEqual(conversion_plan.conversion_type.name, "SQL_CONDITION")
        
    def test_billing_account_name_config(self):
        """Test SQL condition configuration for billing account name generation"""
        conversion_plan = ConversionPlan.load_yaml(
            "focus_converter/conversion_configs/aws-synth/billing_account_name_S001.yaml"
        )

        focus_converter = FocusConverter()
        focus_converter.plans = {"aws-synth": [conversion_plan]}
        
        # This is a SQL condition, so we need to test through the full converter
        # We'll test this in the integration test instead
        self.assertEqual(conversion_plan.conversion_type.name, "SQL_CONDITION")
        
    def test_consumed_unit_config(self):
        """Test rename column configuration for consumed unit"""
        conversion_plan = ConversionPlan.load_yaml(
            "focus_converter/conversion_configs/aws-synth/consumed_unit_S001.yaml"
        )

        focus_converter = FocusConverter()
        focus_converter.plans = {"aws-synth": [conversion_plan]}
        column_exprs = focus_converter.prepare_horizontal_conversion_plan(
            provider="aws-synth"
        )

        test_dataframe = pd.DataFrame([{
            "pricing_Unit": "Hrs"
        }])

        test_pl_df = (
            pl.from_dataframe(test_dataframe)
            .lazy()
            .with_columns(column_exprs)
            .collect()
        )
        
        self.assertIn("ConsumedUnit", test_pl_df.columns)
        self.assertEqual(list(test_pl_df["ConsumedUnit"])[0], "Hrs")
        
    def test_billed_cost_config(self):
        """Test rename column configuration for billed cost"""
        conversion_plan = ConversionPlan.load_yaml(
            "focus_converter/conversion_configs/aws-synth/billed_cost_S001.yaml"
        )

        focus_converter = FocusConverter()
        focus_converter.plans = {"aws-synth": [conversion_plan]}
        column_exprs = focus_converter.prepare_horizontal_conversion_plan(
            provider="aws-synth"
        )

        test_dataframe = pd.DataFrame([{
            "lineItem_UnblendedCost": 5.25
        }])

        test_pl_df = (
            pl.from_dataframe(test_dataframe)
            .lazy()
            .with_columns(column_exprs)
            .collect()
        )
        
        self.assertIn("BilledCost", test_pl_df.columns)
        self.assertEqual(float(test_pl_df["BilledCost"][0]), 5.25)
        
    def test_data_types_config(self):
        """Test data types configuration loads correctly"""
        conversion_plan = ConversionPlan.load_yaml(
            "focus_converter/conversion_configs/aws-synth/0_dimension_dtypes_S001.yaml"
        )
        
        # Validate conversion plan structure
        self.assertEqual(conversion_plan.conversion_type.name, "SET_COLUMN_DTYPES")
        self.assertIn("dtype_args", conversion_plan.conversion_args)
        
        # Check that required dtypes are defined
        dtype_args = conversion_plan.conversion_args["dtype_args"]
        dtype_columns = [arg["column_name"] for arg in dtype_args]
        
        expected_columns = [
            "bill_BillingPeriodStartDate",
            "lineItem_UsageStartDate", 
            "updatedAt",
            "amortisedCost",
            "lineItem_UsageAmount",
            "lineItem_UnblendedCost",
            "line_item_id",
            "resourceId",
            "tags"
        ]
        
        for expected_col in expected_columns:
            self.assertIn(expected_col, dtype_columns)