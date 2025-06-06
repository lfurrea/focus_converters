# test_aws_synth_sample_csv.py
import pathlib
import tempfile

import polars as pl
import pyarrow.dataset as ds

from focus_converter.converter import FocusConverter
from focus_converter.data_loaders.data_loader import DataFormats


class TestAWSSynthSampleCSV:
    """Test AWS-Synth provider with sample CSV data following AWS test patterns"""
    
    def test_sample_csv_dataset(self):
        """Test complete conversion pipeline with synthetic AWS CSV data"""
        with tempfile.TemporaryDirectory() as temp_dir:
            export_path = pathlib.Path(temp_dir).joinpath("aws_synth_sample_csv_dataset")

            # Create sample synthetic data matching the actual CSV structure
            sample_data = self._create_sample_synthetic_data()
            sample_csv_path = pathlib.Path(temp_dir) / "sample_aws_synth.csv"
            
            df = pl.DataFrame(sample_data)
            df.write_csv(sample_csv_path)

            converter = FocusConverter(
                column_prefix=None  # Optional column prefix if needed else can be set to None
            )
            converter.load_provider_conversion_configs()
            converter.load_data(
                data_path=str(sample_csv_path),
                data_format=DataFormats.CSV,
                parquet_data_format=None,
            )
            converter.configure_data_export(
                export_path=export_path,
                export_include_source_columns=False,
            )
            converter.prepare_horizontal_conversion_plan(provider="aws-synth")

            # Run the conversion
            converter.convert()

            # Validate output
            dataset = ds.dataset(temp_dir, format="parquet")
            df = pl.scan_pyarrow_dataset(dataset).collect()
            assert len(df.columns) > 0
            assert len(df) > 0  # Should have rows
            
            # Validate required FOCUS columns exist
            required_columns = [
                "Provider", "BillingPeriodStart", "ChargePeriodStart", 
                "ServiceName", "SubAccountId", "BillingAccountId", 
                "ResourceId", "EffectiveCost", "ConsumedQuantity", 
                "BillingCurrency", "RegionId", "AvailabilityZone", "PricingUnit"
            ]
            
            for column in required_columns:
                assert column in df.columns, f"Required column {column} missing"
                
            # Validate static values
            provider_values = df.select("Provider").unique().to_series().to_list()
            assert provider_values == ["AWS-Synth"], f"Expected Provider='AWS-Synth', got {provider_values}"
            
    def test_postgres_compatibility(self):
        """Test that output is compatible with Postgres table requirements"""
        with tempfile.TemporaryDirectory() as temp_dir:
            export_path = pathlib.Path(temp_dir).joinpath("postgres_compat_test")

            # Create sample data
            sample_data = self._create_sample_synthetic_data()
            sample_csv_path = pathlib.Path(temp_dir) / "sample_data.csv"
            
            df = pl.DataFrame(sample_data)
            df.write_csv(sample_csv_path)

            # Convert
            converter = FocusConverter()
            converter.load_provider_conversion_configs()
            converter.load_data(str(sample_csv_path), DataFormats.CSV)
            converter.configure_data_export(export_path, False)
            converter.prepare_horizontal_conversion_plan("aws-synth")
            converter.convert()

            # Load result
            dataset = ds.dataset(temp_dir, format="parquet")
            result_df = pl.scan_pyarrow_dataset(dataset).collect()
            
            # Test Postgres table compatibility
            postgres_columns = [
                "Provider", "BillingPeriodStart", "ChargePeriodStart", "ServiceName",
                "SubAccountId", "BillingAccountId", "ResourceId", "EffectiveCost",
                "ConsumedQuantity", "BillingCurrency", "RegionId", "AvailabilityZone", 
                "PricingUnit"
            ]
            
            # All required columns should exist
            for column in postgres_columns:
                assert column in result_df.columns, f"Postgres required column {column} missing"
                
            # Test data types for key fields
            assert result_df.schema["BillingPeriodStart"] in [pl.Datetime, pl.Date], "BillingPeriodStart wrong type"
            assert result_df.schema["ChargePeriodStart"] in [pl.Datetime, pl.Date], "ChargePeriodStart wrong type"
            assert result_df.schema["EffectiveCost"] in [pl.Float64, pl.Float32], "EffectiveCost wrong type"
            assert result_df.schema["ConsumedQuantity"] in [pl.Float64, pl.Float32], "ConsumedQuantity wrong type"
            
            # Test required fields are not null
            required_non_null = ["Provider", "ServiceName", "SubAccountId", "EffectiveCost"]
            for column in required_non_null:
                null_count = result_df.select(pl.col(column).is_null().sum()).item()
                assert null_count == 0, f"Required column {column} has {null_count} null values"
                
    def test_data_accuracy(self):
        """Test that data transformations are accurate"""
        with tempfile.TemporaryDirectory() as temp_dir:
            export_path = pathlib.Path(temp_dir).joinpath("accuracy_test")

            # Create sample data with known values
            sample_data = {
                "line_item_id": [1, 2, 3],
                "bill_BillingPeriodStartDate": ["2025-01-01T00:00:00Z", "2025-01-01T00:00:00Z", "2025-01-01T00:00:00Z"],
                "lineItem_UsageStartDate": ["2025-01-05T10:15:00Z", "2025-01-12T09:00:00Z", "2025-01-20T14:00:00Z"],
                "product_ProductName": ["EC2", "EBS", "Lambda"],
                "lineItem_UsageAccountId": ["210987654321", "123456789012", "210987654321"],
                "bill_PayerAccountId": ["123456789012", "210987654321", "123456789012"],
                "resourceId": ["i-01abc", "i-02abc", "i-03abc"],
                "amortisedCost": [1.05, 5.20, 1.10],
                "lineItem_UsageAmount": [10.0, 100.0, 50.0],
                "lineItem_CurrencyCode": ["USD", "USD", "USD"],
                "tags": ['{"env":"prod"}', '{"env":"dev"}', '{"env":"test"}'],
                "updatedAt": ["2023-10-15T16:30:00Z", "2023-10-15T16:30:00Z", "2023-10-15T16:30:00Z"],
                "region": ["us-east-1", "us-west-2", "us-east-1"],
                "availabilityZone": ["us-east-1a", "us-west-2a", "us-east-1b"],
                "product_ProductFamily": ["Compute", "Storage", "Serverless"],
                "lineItem_UsageType": ["USW2-BoxUsage:m4.xlarge", "USW2-DataProcessed-GB", "USW2-DataProcessed-GB"],
                "lineItem_Operation": ["RunInstances", "CreateVolume", "Invoke"],
                "pricing_Unit": ["Hrs", "GB", "Requests"]
            }
            
            sample_csv_path = pathlib.Path(temp_dir) / "accuracy_test.csv"
            df = pl.DataFrame(sample_data)
            df.write_csv(sample_csv_path)

            # Convert
            converter = FocusConverter()
            converter.load_provider_conversion_configs()
            converter.load_data(str(sample_csv_path), DataFormats.CSV)
            converter.configure_data_export(export_path, True)  # Include source for comparison
            converter.prepare_horizontal_conversion_plan("aws-synth")
            converter.convert()

            # Load and test
            dataset = ds.dataset(temp_dir, format="parquet")
            result_df = pl.scan_pyarrow_dataset(dataset).collect()
            
            # Test EffectiveCost = amortisedCost
            if "amortisedCost" in result_df.columns:
                for i in range(len(result_df)):
                    expected = float(result_df["amortisedCost"][i])
                    actual = float(result_df["EffectiveCost"][i])
                    assert abs(expected - actual) < 0.01, f"EffectiveCost mismatch at row {i}: {expected} vs {actual}"
                    
            # Test ConsumedQuantity = lineItem_UsageAmount  
            if "lineItem_UsageAmount" in result_df.columns:
                for i in range(len(result_df)):
                    expected = float(result_df["lineItem_UsageAmount"][i])
                    actual = float(result_df["ConsumedQuantity"][i])
                    assert abs(expected - actual) < 0.01, f"ConsumedQuantity mismatch at row {i}: {expected} vs {actual}"
                    
            # Test ServiceName = product_ProductName
            if "product_ProductName" in result_df.columns:
                for i in range(len(result_df)):
                    expected = str(result_df["product_ProductName"][i])
                    actual = str(result_df["ServiceName"][i])
                    assert expected == actual, f"ServiceName mismatch at row {i}: {expected} vs {actual}"
                    
    def _create_sample_synthetic_data(self):
        """Create sample synthetic data matching the CSV structure"""
        return {
            "line_item_id": [1, 2, 3, 4, 5],
            "bill_BillingPeriodStartDate": ["2025-01-01T00:00:00Z"] * 5,
            "lineItem_UsageStartDate": [
                "2025-01-05T10:15:00Z", "2025-01-12T09:00:00Z", "2025-01-20T14:00:00Z", 
                "2025-02-10T08:00:00Z", "2025-02-15T13:00:00Z"
            ],
            "product_ProductName": ["EC2", "EBS", "Lambda", "EC2", "EBS"],
            "lineItem_UsageAccountId": ["210987654321", "123456789012", "210987654321", "123456789012", "210987654321"],
            "bill_PayerAccountId": ["123456789012", "210987654321", "123456789012", "210987654321", "123456789012"],
            "resourceId": ["i-01abcdef123456789", "i-02abcdef123456789", "i-03abcdef123456789", "i-04abcdef123456789", "i-05abcdef123456789"],
            "amortisedCost": [1.05, 5.20, 1.10, 0.00, 15.30],
            "lineItem_UsageAmount": [10.0, 100.0, 50.0, 20.0, 150.0],
            "lineItem_CurrencyCode": ["USD"] * 5,
            "tags": [
                '{"env":"prod","team":"devops"}',
                '{"env":"dev","team":"analytics"}', 
                '{"env":"test","team":"qa"}',
                '{"env":"prod","team":"finance"}',
                '{"env":"dev","team":"ops"}'
            ],
            "updatedAt": ["2023-10-15T16:30:00Z"] * 5,
            "region": ["us-east-1", "us-west-2", "us-east-1", "us-west-2", "us-east-1"],
            "availabilityZone": ["us-east-1a", "us-west-2a", "us-east-1b", "us-west-2a", "us-east-1a"],
            "product_ProductFamily": ["Compute", "Storage", "Serverless", "Compute", "Storage"],
            "lineItem_UsageType": ["USW2-BoxUsage:m4.xlarge", "USW2-DataProcessed-GB", "USW2-DataProcessed-GB", "USW2-BoxUsage:m4.xlarge", "USW2-DataProcessed-GB"],
            "lineItem_Operation": ["RunInstances", "CreateVolume", "Invoke", "RunInstances", "CreateVolume"],
            "pricing_Unit": ["Hrs", "GB", "Requests", "Hrs", "GB"]
        }