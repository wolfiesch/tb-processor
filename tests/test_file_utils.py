import pytest
from tb_processor import file_utils
import datetime
from pathlib import Path

def test_extract_date():
    """Test date extraction from filename."""
    # Test year extraction
    path = Path("Balance Sheet by Month-2023.xlsx")
    date = file_utils.extract_date(path)
    assert date.year == 2023
    
    # Test with different year
    path2 = Path("Profit and Loss by Month-2024.xlsx")
    date2 = file_utils.extract_date(path2)
    assert date2.year == 2024

def test_find_monthly_files():
    """Test finding monthly files."""
    # TODO: Create dummy files in tests/fixtures and test finding them
    # This would require setting up a test directory structure
    pass
