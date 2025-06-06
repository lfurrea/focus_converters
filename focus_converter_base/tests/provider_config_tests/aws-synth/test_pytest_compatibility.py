# test_pytest_compatibility.py
"""
Quick validation that our AWS-Synth tests work with pytest framework
"""

import pytest
import sys
from pathlib import Path

# Add focus_converter_base to path
focus_converter_base = Path(__file__).parent.parent.parent.parent
sys.path.insert(0, str(focus_converter_base))


def test_imports():
    """Test that all required imports work"""
    try:
        from focus_converter.converter import FocusConverter
        from focus_converter.configs.base_config import ConversionPlan
        from focus_converter.data_loaders.data_loader import DataFormats
        import polars as pl
        import pyarrow.dataset as ds
        assert True
    except ImportError as e:
        pytest.fail(f"Import failed: {e}")


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
        "focus_converter/conversion_configs/aws-synth/providerName_S001.yaml",
        "focus_converter/conversion_configs/aws-synth/focusVersion_S001.yaml",
        "focus_converter/conversion_configs/aws-synth/0_dimension_dtypes_S001.yaml",
        "focus_converter/conversion_configs/aws-synth/billing_period_start_S001.yaml",
        "focus_converter/conversion_configs/aws-synth/serviceName_S001.yaml"
    ]
    
    for config_file in config_files:
        try:
            plan = ConversionPlan.load_yaml(config_file)
            assert plan is not None, f"Failed to load {config_file}"
            assert hasattr(plan, 'conversion_type'), f"Invalid plan structure in {config_file}"
        except Exception as e:
            pytest.fail(f"Failed to load config {config_file}: {e}")


if __name__ == "__main__":
    # Run with pytest when called directly
    pytest.main([__file__, "-v"])