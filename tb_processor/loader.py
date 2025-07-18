import datetime
import re
import pathlib
import numpy as np
import pandas as pd
from . import file_utils

def find_header_row(df, keywords=["account", "description", "total", "item", "distribution account", "january", "february", "gl", "gl code", "account number"]):
    """Find the header row by looking for common accounting terms."""
    for i in range(min(15, len(df))):  # Check the first 15 rows or all rows if fewer
        row_values = [str(val).lower() for val in df.iloc[i].values if val is not None and str(val).strip()]
        row_text = " ".join(row_values)
        
        # Look for month names which typically appear in the header row
        if "january" in row_text and "february" in row_text and "march" in row_text:
            return i
            
        # Or look for other accounting terms
        if any(keyword in row_text for keyword in keywords):
            return i
            
    return 0  # Default to first row if no match found

def convert_columns_to_dates(df):
    """Convert column names that look like dates to datetime objects."""
    new_columns = []
    
    for col in df.columns:
        # Skip the first column (typically account names)
        if col == df.columns[0]:
            new_columns.append(col)
            continue
            
        # Try to convert to date if it's a string
        if isinstance(col, str):
            # Handle specific format from these Excel files (e.g., "January 2022")
            month_pattern = re.compile(r'(January|February|March|April|May|June|July|August|September|October|November|December)\s+(\d{4})', re.IGNORECASE)
            match = month_pattern.match(col)
            
            if match:
                month_name = match.group(1).capitalize()
                year = int(match.group(2))
                
                # Convert month name to month number
                month_mapping = {
                    'January': 1, 'February': 2, 'March': 3, 'April': 4, 'May': 5, 'June': 6,
                    'July': 7, 'August': 8, 'September': 9, 'October': 10, 'November': 11, 'December': 12
                }
                month_num = month_mapping.get(month_name, 1)
                
                # Create date object (day 1 of the month)
                date_obj = datetime.date(year, month_num, 1)
                new_columns.append(date_obj)
                continue
                
            # Try standard date formats
            for date_format in ['%b %Y', '%B %Y', '%m/%d/%Y', '%Y-%m-%d', '%m-%d-%Y']:
                try:
                    date_obj = datetime.datetime.strptime(col, date_format).date()
                    new_columns.append(date_obj)
                    break
                except ValueError:
                    continue
            else:
                # If no date format matches, keep original
                new_columns.append(col)
        else:
            new_columns.append(col)
            
    return new_columns

def load_sheet(path: pathlib.Path, sheet_name: str) -> pd.DataFrame:
    """
    Reads Excel file and processes it to have clean headers with date columns.
    Specifically handles the trial balance format in the provided Excel files.
    """
    try:
        # Read the Excel file without headers first
        df = pd.read_excel(path, sheet_name=sheet_name, header=None)
        
        # Find the header row (typically row with month names)
        header_row = find_header_row(df)
        
        # Re-read with the detected header row
        df = pd.read_excel(path, sheet_name=sheet_name, header=header_row)
        
        # Clean up column names
        df.columns = [str(col).strip() if col is not None else f"Column_{i}" 
                     for i, col in enumerate(df.columns)]
        
        # Convert date-like columns to proper dates
        df.columns = convert_columns_to_dates(df)
        
        # Filter out rows that are just section headers or blank
        # In trial balance reports, actual data rows typically have numeric values
        numeric_mask = df.iloc[:, 1:].apply(lambda x: pd.to_numeric(x, errors='coerce')).notna().any(axis=1)
        df = df[numeric_mask]
        
        # Drop any columns that are entirely NaN
        df = df.dropna(axis=1, how='all')
        
        # Sort columns: first column (typically account name/number) followed by dates in order
        date_cols = [col for col in df.columns[1:] if isinstance(col, datetime.date)]
        non_date_cols = [col for col in df.columns[1:] if not isinstance(col, datetime.date)]
        
        # Reorder columns: first column, then date columns (sorted), then other columns
        if date_cols:  # Only reorder if we have identified date columns
            new_order = [df.columns[0]] + sorted(date_cols) + non_date_cols
            df = df[new_order]
        
        # Clean up data - replace NaN with 0 for numeric columns
        for col in df.columns[1:]:
            try:
                if df[col].dtype in [np.float64, np.int64] or pd.api.types.is_numeric_dtype(df[col]):
                    df[col] = df[col].fillna(0)
            except:
                pass
        
        return df
    
    except Exception as e:
        print(f"Error loading {path}, sheet '{sheet_name}': {e}")
        # Return empty DataFrame with the file date in filename
        empty_df = pd.DataFrame(columns=["Line Item", file_utils.extract_date(path)])
        return empty_df

def load_bs(path: pathlib.Path) -> pd.DataFrame:
    """Loads Balance Sheet data."""
    # Try different sheet names that might contain balance sheet data
    for sheet_name in ["Sheet1", "Balance Sheet", "BS", "Balance_Sheet"]:
        try:
            return load_sheet(path, sheet_name=sheet_name)
        except Exception:
            continue
            
    # If no sheet found, try the first sheet
    try:
        return load_sheet(path, sheet_name=0)
    except Exception as e:
        print(f"Failed to load balance sheet from {path}: {e}")
        return pd.DataFrame()

def load_is(path: pathlib.Path) -> pd.DataFrame:
    """Loads Income Statement data."""
    # Try different sheet names that might contain income statement data
    for sheet_name in ["Sheet1", "Income Statement", "Profit and Loss", "P&L", "IS"]:
        try:
            return load_sheet(path, sheet_name=sheet_name)
        except Exception:
            continue
            
    # If no sheet found, try the first sheet
    try:
        return load_sheet(path, sheet_name=0)
    except Exception as e:
        print(f"Failed to load income statement from {path}: {e}")
        return pd.DataFrame()
