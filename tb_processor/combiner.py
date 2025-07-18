import pandas as pd
from typing import List
import pathlib
import datetime

from . import loader

def combine_monthly(dfs: List[pd.DataFrame]) -> pd.DataFrame:
    """
    Combines multiple trial balance dataframes:
    - Aligns on the first column (typically account names)
    - Preserves all unique accounts across all dataframes
    - Fills missing values with 0
    - Ensures consistent monthly columns
    """
    if not dfs:
        return pd.DataFrame()
    
    # Filter out empty dataframes
    dfs = [df for df in dfs if not df.empty]
    
    if not dfs:
        return pd.DataFrame()
    
    # Use the first column as the key for joining (typically account names)
    key_column = dfs[0].columns[0]
    
    # Collect all unique accounts across all dataframes
    all_accounts = set()
    for df in dfs:
        if not df.empty and len(df.columns) > 0:
            accounts = df[df.columns[0]].dropna().astype(str).unique()
            all_accounts.update(accounts)
    
    # Create a result dataframe with all unique accounts
    result = pd.DataFrame({key_column: sorted(list(all_accounts))})
    
    # Add data from each dataframe
    for df in dfs:
        if df.empty:
            continue
            
        # Get date columns only
        date_cols = [col for col in df.columns if isinstance(col, datetime.date)]
        
        if not date_cols:
            # If no date columns, skip this dataframe
            continue
        
        # Convert key column to string for consistent joining
        df = df.copy()
        df[df.columns[0]] = df[df.columns[0]].astype(str)
        
        # For each date column, merge into the result
        for date_col in date_cols:
            # Create a temporary dataframe with just the key column and this date column
            temp_df = df[[df.columns[0], date_col]].copy()
            temp_df.columns = [key_column, date_col]  # Ensure consistent column names
            
            # Merge with the result
            result = pd.merge(result, temp_df, on=key_column, how='left')
    
    # Clean up any NaN values - replace with 0 for numeric columns
    for col in result.columns:
        if col != key_column:
            result[col] = pd.to_numeric(result[col], errors='coerce').fillna(0)
    
    # Sort columns: account column first, followed by date columns in chronological order
    date_cols = [col for col in result.columns if isinstance(col, datetime.date)]
    other_cols = [col for col in result.columns if col != key_column and col not in date_cols]
    
    sorted_cols = [key_column] + sorted(date_cols) + other_cols
    
    # Only include columns that exist in the result
    sorted_cols = [col for col in sorted_cols if col in result.columns]
    
    return result[sorted_cols]

def combine_all_bs(files: List[pathlib.Path]) -> pd.DataFrame:
    """Combine all Balance Sheet files."""
    print(f"Processing {len(files)} Balance Sheet files...")
    dfs = []
    
    for f in files:
        print(f"  Loading {f.name}")
        dfs.append(loader.load_bs(f))
    
    return combine_monthly(dfs)

def combine_all_is(files: List[pathlib.Path]) -> pd.DataFrame:
    """Combine all Income Statement files."""
    print(f"Processing {len(files)} Income Statement files...")
    dfs = []
    
    for f in files:
        print(f"  Loading {f.name}")
        dfs.append(loader.load_is(f))
    
    return combine_monthly(dfs)
