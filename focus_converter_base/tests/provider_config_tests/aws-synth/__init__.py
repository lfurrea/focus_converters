# __init__.py
"""
AWS-Synth provider test package

Test suite for validating AWS-Synth provider configurations and conversions.
Follows the same patterns as other provider tests in the focus_converter project.

The aws-synth provider is designed to handle synthetic AWS CUR (Cost and Usage Report) data
and transform it into FOCUS-compatible format for insertion into a Postgres database.

Test modules:
- test_aws_synth_provider.py: Unit tests for individual configuration files
- test_aws_synth_sample_csv.py: Integration tests with complete CSV processing
- test_pytest_compatibility.py: Pytest framework compatibility and configuration validation
"""