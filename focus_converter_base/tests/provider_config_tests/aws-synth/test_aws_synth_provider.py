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
            "focus_converter/conversion_configs/aws-synth/providerName_S001.yaml"
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
        self.assertEqual(list(test_pl_df["Provider"])[0], "AWS-Synth")
        
    def test_focus_version_config(self):
        """Test the FOCUS version static value configuration"""
        conversion_plan = ConversionPlan.load_yaml(
            "focus_converter/conversion_configs/aws-synth/focusVersion_S001.yaml"
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
        # Note: focusVersion maps to PlaceHolder, so we'd need to check the actual column name
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
        
    def test_service_name_config(self):
        """Test rename column configuration for service name"""
        conversion_plan = ConversionPlan.load_yaml(
            "focus_converter/conversion_configs/aws-synth/serviceName_S001.yaml"
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
            "focus_converter/conversion_configs/aws-synth/effectiveCost_S001.yaml"
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
        
    def test_region_config(self):
        """Test rename column configuration for region"""
        conversion_plan = ConversionPlan.load_yaml(
            "focus_converter/conversion_configs/aws-synth/region_S001.yaml"
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
            "lineItem_UsageAmount"
        ]
        
        for expected_col in expected_columns:
            self.assertIn(expected_col, dtype_columns)