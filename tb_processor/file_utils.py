import pathlib
import datetime
import glob
import re
import os

# Handle both direct execution and module import
try:
    from . import config
except ImportError:
    # When run directly, use absolute import
    import sys
    sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
    import tb_processor.config as config

def find_monthly_files(pattern: str) -> list[pathlib.Path]:
    """Uses glob on INPUT_DIR and sorts by date parsed from filename."""
    # Replace pattern placeholders with actual glob pattern
    glob_pattern = pattern.replace("yyyy-mm", "*")
    
    # Get all matching files
    files = [pathlib.Path(p) for p in glob.glob(str(pathlib.Path(config.INPUT_DIR) / glob_pattern))]
    
    # Sort files by the date extracted from filename
    return sorted(files, key=extract_date)

def extract_date(fn: pathlib.Path) -> datetime.date:
    """Extracts date from filename."""
    # Extract year from filename (looking for 4-digit year like 2022, 2023, etc.)
    year_match = re.search(r'(\d{4})', fn.stem)
    if not year_match:
        # If no year found, use current year as fallback
        return datetime.date.today()
    
    year = int(year_match.group(1))
    
    # Look for month in filename
    # First try to find a date pattern like yyyy-mm or mm-yyyy
    date_pattern = re.search(r'(\d{4})-(\d{1,2})|(\d{1,2})-(\d{4})', fn.stem)
    
    if date_pattern:
        # Extract month based on which pattern matched
        if date_pattern.group(1) and date_pattern.group(2):  # yyyy-mm
            month = int(date_pattern.group(2))
        elif date_pattern.group(3) and date_pattern.group(4):  # mm-yyyy
            month = int(date_pattern.group(3))
        else:
            # Default to January if parsing fails
            month = 1
    else:
        # Try to extract month from month name or abbreviation
        month_names = {
            'jan': 1, 'feb': 2, 'mar': 3, 'apr': 4, 'may': 5, 'jun': 6,
            'jul': 7, 'aug': 8, 'sep': 9, 'oct': 10, 'nov': 11, 'dec': 12
        }
        
        for month_name, month_num in month_names.items():
            if month_name in fn.stem.lower():
                month = month_num
                break
        else:
            # Default to January if no month found
            month = 1
    
    # Create date with day=1 (first day of the month)
    return datetime.date(year, month, 1)
