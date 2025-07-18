import pytest
import pandas as pd
from pathlib import Path
from tb_processor import loader

def test_find_header_row():
    """Test finding header row in DataFrame."""
    # Create a test DataFrame with header in row 2
    data = [["", "", ""],
            ["Some", "random", "data"],
            ["Account", "January 2023", "February 2023"],
            ["Cash", 1000, 1500],
            ["AR", 2000, 2500]]
    
    df = pd.DataFrame(data)
    header_row = loader.find_header_row(df)
    assert header_row == 2

def test_convert_columns_to_dates():
    """Test converting column names to date objects."""
    # Create a DataFrame with month-year column names
    df = pd.DataFrame({
        'Account': ['Cash', 'AR'],
        'January 2023': [1000, 2000],
        'February 2023': [1500, 2500]
    })
    
    new_columns = loader.convert_columns_to_dates(df)
    
    # First column should remain unchanged
    assert new_columns[0] == 'Account'
    
    # Other columns should be converted to dates
    import datetime
    assert isinstance(new_columns[1], datetime.date)
    assert isinstance(new_columns[2], datetime.date)
    assert new_columns[1].year == 2023
    assert new_columns[1].month == 1
    assert new_columns[2].month == 2

# TODO: Add more comprehensive tests with actual Excel files
# This would require creating sample Excel files in tests/fixtures/
