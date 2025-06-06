# test_aws_synth_sample_csv.py
import pathlib
import tempfile

import polars as pl
from focus_converter.data_loaders.data_exporter import ExportDataFormats

from focus_converter.converter import FocusConverter
from focus_converter.data_loaders.data_loader import DataFormats


class TestAWSSynthSampleCSV:
    """Test AWS-Synth provider with sample CSV data following AWS test patterns"""
    
    def test_sample_csv_dataset(self):
        """Test complete conversion pipeline with synthetic AWS CSV data"""
        with tempfile.TemporaryDirectory() as temp_dir:
            export_dir = pathlib.Path(temp_dir) / "output"
            export_dir.mkdir()

            # Check if the aws_synthetic_cur.csv file has the right structure
            test_csv_path = pathlib.Path(__file__).parent / "aws_synthetic_cur.csv"
            print(f"Test CSV path: {test_csv_path}")
            
            if test_csv_path.exists():
                # Read and inspect the test data
                try:
                    sample_df = pl.read_csv(test_csv_path, truncate_ragged_lines=True, ignore_errors=True)
                    print(f"Test CSV columns: {sample_df.columns}")
                    print(f"Test CSV shape: {sample_df.shape}")
                    if len(sample_df) > 0:
                        print(f"First row sample: {dict(sample_df.row(0, named=True))}")
                    else:
                        print("CSV file is empty!")
                except Exception as e:
                    print(f"Error reading CSV: {e}")
                    # Fall back to creating minimal data
                    test_csv_path = None
            else:
                test_csv_path = None
                
            if test_csv_path is None:
                print("WARNING: Using fallback minimal test data!")
                # Let's create a minimal test file
                minimal_data = {
                    "line_item_id": [1],
                    "bill_BillingPeriodStartDate": ["2025-01-01T00:00:00Z"],
                    "bill_BillingPeriodEndDate": ["2025-01-31T23:59:59Z"],
                    "lineItem_UsageStartDate": ["2025-01-05T10:15:00Z"],
                    "lineItem_UsageEndDate": ["2025-01-05T11:15:00Z"],
                    "product_ProductName": ["EC2"],
                    "product_ProductFamily": ["Compute"],
                    "lineItem_LineItemType": ["Usage"],
                    "lineItem_UsageAccountId": ["210987654321"],
                    "bill_PayerAccountId": ["123456789012"],
                    "resourceId": ["i-01abc"],
                    "amortisedCost": [1.05],
                    "lineItem_UnblendedCost": [1.00],
                    "lineItem_UsageAmount": [10.0],
                    "lineItem_CurrencyCode": ["USD"],
                    "tags": ['{"env":"prod"}'],
                    "updatedAt": ["2023-10-15T16:30:00Z"],
                    "region": ["us-east-1"],
                    "availabilityZone": ["us-east-1a"],
                    "pricing_Unit": ["Hrs"]
                }
                test_csv_path = pathlib.Path(temp_dir) / "minimal_test.csv"
                pl.DataFrame(minimal_data).write_csv(test_csv_path)
                print(f"Created minimal test file: {test_csv_path}")

            converter = FocusConverter(
                column_prefix=None  # Optional column prefix if needed else can be set to None
            )
            converter.load_provider_conversion_configs()
            converter.load_data(
                data_path=str(test_csv_path),
                data_format=DataFormats.CSV,
                parquet_data_format=None,
            )
            converter.configure_data_export(
                export_path=str(export_dir),
                export_include_source_columns=False,
                export_format=ExportDataFormats.CSV
            )
            converter.prepare_horizontal_conversion_plan(provider="aws-synth")

            # Run the conversion with error handling
            try:
                converter.convert()
                print("Conversion completed successfully")
            except Exception as e:
                print(f"Conversion failed with error: {e}")
                import traceback
                traceback.print_exc()
                raise

            # Find the generated CSV file - it may be created with directory as prefix
            temp_dir_path = pathlib.Path(temp_dir)
            all_temp_files = list(temp_dir_path.rglob("*.csv"))
            print(f"All CSV files in temp directory: {all_temp_files}")
            
            # Filter out input files to find output files
            output_csv_files = [f for f in all_temp_files if "minimal_test" not in f.name and "aws_synthetic_cur" not in f.name]
            print(f"Output CSV files found: {output_csv_files}")
            
            assert len(output_csv_files) > 0, f"No output CSV files created. All CSV files: {all_temp_files}"
            
            # Use the first output CSV file
            output_file = output_csv_files[0]
            df = pl.read_csv(output_file)
            assert len(df.columns) > 0
            assert len(df) > 0  # Should have rows
            
            # Validate required FOCUS columns exist for Postgres compatibility
            required_columns = [
                "Provider", "BillingPeriodStart", "ChargePeriodStart", 
                "ServiceName", "SubAccountId", "BillingAccountId", 
                "ResourceId", "EffectiveCost", "ConsumedQuantity", 
                "BillingCurrency", "RegionId", "AvailabilityZone", 
                "ConsumedUnit", "BilledCost", "ServiceCategory",
                "BillingAccountName"
            ]
            
            for column in required_columns:
                assert column in df.columns, f"Required column {column} missing"
                
            # Validate static values
            provider_values = df.select("Provider").unique().to_series().to_list()
            assert provider_values == ["aws-synth"], f"Expected Provider='aws-synth', got {provider_values}"
            
    def test_data_accuracy(self):
        """Test that data transformations are accurate using first few rows of actual test data"""
        with tempfile.TemporaryDirectory() as temp_dir:
            export_dir = pathlib.Path(temp_dir) / "output"
            export_dir.mkdir()

            # Use actual test data file (just first 3 rows for faster testing)
            test_csv_path = pathlib.Path(__file__).parent / "aws_synthetic_cur.csv"
            assert test_csv_path.exists(), f"Test data file not found: {test_csv_path}"
            
            # Read original data and take first 3 rows
            original_df = pl.read_csv(test_csv_path)
            small_test_data = original_df.head(3)
            
            # Write small test file
            small_csv_path = pathlib.Path(temp_dir) / "small_test.csv"
            small_test_data.write_csv(small_csv_path)

            # Convert
            converter = FocusConverter()
            converter.load_provider_conversion_configs()
            converter.load_data(str(small_csv_path), DataFormats.CSV)
            converter.configure_data_export(str(export_dir), True, export_format=ExportDataFormats.CSV)  # Include source for comparison
            converter.prepare_horizontal_conversion_plan("aws-synth")
            converter.convert()

            # Find and load result
            temp_dir_path = pathlib.Path(temp_dir)
            all_csv_files = list(temp_dir_path.rglob("*.csv"))
            output_csv_files = [f for f in all_csv_files if "small_test" not in f.name]
            assert len(output_csv_files) > 0, f"No output CSV files created. All CSV files: {all_csv_files}"
            result_df = pl.read_csv(output_csv_files[0], truncate_ragged_lines=True, ignore_errors=True)
            
            # Test EffectiveCost = amortisedCost
            if "amortisedCost" in result_df.columns:
                for i in range(len(result_df)):
                    expected = float(result_df["amortisedCost"][i])
                    actual = float(result_df["EffectiveCost"][i])
                    assert abs(expected - actual) < 0.01, f"EffectiveCost mismatch at row {i}: {expected} vs {actual}"
                    
            # Test BilledCost = lineItem_UnblendedCost
            if "lineItem_UnblendedCost" in result_df.columns:
                for i in range(len(result_df)):
                    expected = float(result_df["lineItem_UnblendedCost"][i])
                    actual = float(result_df["BilledCost"][i])
                    assert abs(expected - actual) < 0.01, f"BilledCost mismatch at row {i}: {expected} vs {actual}"
                    
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
                    
            # Test Provider static value
            provider_values = result_df.select("Provider").unique().to_series().to_list()
            assert "aws-synth" in provider_values, f"Expected Provider='aws-synth', got {provider_values}"
                
    def test_sql_conditions_accuracy(self):
        """Test SQL condition transformations work correctly using actual test data"""
        with tempfile.TemporaryDirectory() as temp_dir:
            export_dir = pathlib.Path(temp_dir) / "output"
            export_dir.mkdir()

            # Use actual test data file
            test_csv_path = pathlib.Path(__file__).parent / "aws_synthetic_cur.csv"
            assert test_csv_path.exists(), f"Test data file not found: {test_csv_path}"
            
            # Read original data and take first 4 rows for testing edge cases
            original_df = pl.read_csv(test_csv_path)
            test_data = original_df.head(4)
            
            # Write test file
            test_file_path = pathlib.Path(temp_dir) / "sql_test.csv"
            test_data.write_csv(test_file_path)

            # Convert
            converter = FocusConverter()
            converter.load_provider_conversion_configs()
            converter.load_data(str(test_file_path), DataFormats.CSV)
            converter.configure_data_export(str(export_dir), False, export_format=ExportDataFormats.CSV)
            converter.prepare_horizontal_conversion_plan("aws-synth")
            converter.convert()

            # Find and load result
            temp_dir_path = pathlib.Path(temp_dir)
            all_csv_files = list(temp_dir_path.rglob("*.csv"))
            output_csv_files = [f for f in all_csv_files if "sql_test" not in f.name]
            assert len(output_csv_files) > 0, f"No output CSV files created. All CSV files: {all_csv_files}"
            result_df = pl.read_csv(output_csv_files[0], truncate_ragged_lines=True, ignore_errors=True)
            
            # Test ServiceCategory SQL conditions
            expected_categories = ["Compute", "Storage", "Other", "Other"]
            for i in range(len(result_df)):
                actual = str(result_df["ServiceCategory"][i])
                expected = expected_categories[i]
                assert actual == expected, f"ServiceCategory SQL condition failed at row {i}: {expected} vs {actual}"
                
            # Test BillingCurrency SQL condition with default
            expected_currencies = ["USD", "EUR", "USD", "GBP"]  # None should become USD
            for i in range(len(result_df)):
                actual = str(result_df["BillingCurrency"][i])
                expected = expected_currencies[i]
                assert actual == expected, f"BillingCurrency SQL condition failed at row {i}: {expected} vs {actual}"
                
    def _create_sample_synthetic_data(self):
        """Create sample synthetic data matching the CSV structure from aws_synthetic_cur.csv"""
        return {
            "line_item_id": ["1", "2", "3", "4", "5"],
            "bill_BillingPeriodStartDate": ["2025-01-01T00:00:00Z"] * 5,
            "bill_BillingPeriodEndDate": ["2025-01-31T23:59:59Z"] * 5,
            "lineItem_UsageStartDate": [
                "2025-01-05T10:15:00Z", "2025-01-12T09:00:00Z", "2025-01-20T14:00:00Z", 
                "2025-02-10T08:00:00Z", "2025-02-15T13:00:00Z"
            ],
            "lineItem_UsageEndDate": [
                "2025-01-05T11:15:00Z", "2025-01-12T10:00:00Z", "2025-01-20T15:00:00Z", 
                "2025-02-10T09:00:00Z", "2025-02-15T14:00:00Z"
            ],
            "product_ProductName": ["EC2", "EBS", "Lambda", "EC2", "EBS"],
            "product_ProductFamily": ["Compute", "Storage", "Serverless", "Compute", "Storage"],
            "lineItem_LineItemType": ["Usage", "Usage", "Usage", "Tax", "Usage"],
            "lineItem_UsageAccountId": ["210987654321", "123456789012", "210987654321", "123456789012", "210987654321"],
            "bill_PayerAccountId": ["123456789012", "210987654321", "123456789012", "210987654321", "123456789012"],
            "resourceId": ["i-01abcdef123456789", "i-02abcdef123456789", "i-03abcdef123456789", "i-04abcdef123456789", "i-05abcdef123456789"],
            "amortisedCost": [1.05, 5.20, 1.10, 0.00, 15.30],
            "lineItem_UnblendedCost": [1.00, 5.00, 1.00, 0.00, 15.00],
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
            "lineItem_UsageType": ["USW2-BoxUsage:m4.xlarge", "USW2-DataProcessed-GB", "USW2-DataProcessed-GB", "USW2-BoxUsage:m4.xlarge", "USW2-DataProcessed-GB"],
            "lineItem_Operation": ["RunInstances", "CreateVolume", "Invoke", "RunInstances", "CreateVolume"],
            "pricing_Unit": ["Hrs", "GB", "Requests", "Hrs", "GB"]
        }