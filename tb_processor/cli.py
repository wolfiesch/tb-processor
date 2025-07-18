import click
import pandas as pd
import os
import sys
from datetime import datetime

from . import config
from . import file_utils
from . import combiner

@click.group()
def main():
    """A command-line tool for processing trial balance files."""
    click.echo(f"TB Processor v0.1.0")
    click.echo(f"Using input directory: {config.INPUT_DIR}")
    click.echo(f"Output file will be: {config.OUTPUT_FILE}")

@main.command("bs")
@click.option('--verbose', '-v', is_flag=True, help='Enable verbose output')
def process_bs(verbose):
    """Loads all BS files, combines them, and writes to Excel."""
    try:
        click.echo("Processing Balance Sheet files...")
        
        # Find files matching the pattern
        files = file_utils.find_monthly_files(config.BS_PATTERN)
        
        if not files:
            click.echo("No Balance Sheet files found matching pattern. Please check your input directory.")
            return
            
        if verbose:
            click.echo(f"Found {len(files)} files:")
            for f in files:
                click.echo(f"  - {f.name}")
        
        # Process files
        combined_df = combiner.combine_all_bs(files)
        
        if combined_df.empty:
            click.echo("No data was extracted from the files. Please check file format.")
            return
            
        # Create output directory if it doesn't exist
        output_dir = os.path.dirname(config.OUTPUT_FILE)
        if output_dir and not os.path.exists(output_dir):
            os.makedirs(output_dir)
            
        # Write to Excel
        with pd.ExcelWriter(config.OUTPUT_FILE, engine="openpyxl") as writer:
            combined_df.to_excel(writer, sheet_name="Balance Sheet", index=False)
        click.echo(f"[SUCCESS] Balance Sheet data written to {config.OUTPUT_FILE}")
        
    except Exception as e:
        click.echo(f"[ERROR] Error processing Balance Sheet files: {str(e)}")
        if verbose:
            import traceback
            click.echo(traceback.format_exc())
        sys.exit(1)

@main.command("is")
@click.option('--verbose', '-v', is_flag=True, help='Enable verbose output')
def process_is(verbose):
    """Loads all IS files, combines them, and writes to Excel."""
    try:
        click.echo("Processing Income Statement files...")
        
        # Find files matching the pattern
        files = file_utils.find_monthly_files(config.IS_PATTERN)
        
        if not files:
            click.echo("No Income Statement files found matching pattern. Please check your input directory.")
            return
            
        if verbose:
            click.echo(f"Found {len(files)} files:")
            for f in files:
                click.echo(f"  - {f.name}")
        
        # Process files
        combined_df = combiner.combine_all_is(files)
        
        if combined_df.empty:
            click.echo("No data was extracted from the files. Please check file format.")
            return
        
        # Create output directory if it doesn't exist
        output_dir = os.path.dirname(config.OUTPUT_FILE)
        if output_dir and not os.path.exists(output_dir):
            os.makedirs(output_dir)
            
        # Check if file exists to determine mode
        mode = 'a' if os.path.exists(config.OUTPUT_FILE) else 'w'
        if_sheet_exists = 'replace' if mode == 'a' else None
        
        # Write to Excel
        with pd.ExcelWriter(config.OUTPUT_FILE, engine="openpyxl", mode=mode, if_sheet_exists=if_sheet_exists) as writer:
            combined_df.to_excel(writer, sheet_name="Income Statement", index=False)
        
        click.echo(f"[SUCCESS] Income Statement data written to {config.OUTPUT_FILE}")
        
    except Exception as e:
        click.echo(f"[ERROR] Error processing Income Statement files: {str(e)}")
        if verbose:
            import traceback
            click.echo(traceback.format_exc())
        sys.exit(1)

@main.command("all")
@click.option('--verbose', '-v', is_flag=True, help='Enable verbose output')
def process_all(verbose):
    """Processes both Balance Sheet and Income Statement files."""
    try:
        click.echo("Processing all files...")
        
        bs_files = file_utils.find_monthly_files(config.BS_PATTERN)
        is_files = file_utils.find_monthly_files(config.IS_PATTERN)

        if not bs_files and not is_files:
            click.echo("No files found to process.")
            return

        # Create output directory if it doesn't exist
        output_dir = os.path.dirname(config.OUTPUT_FILE)
        if output_dir and not os.path.exists(output_dir):
            os.makedirs(output_dir)

        with pd.ExcelWriter(config.OUTPUT_FILE, engine="openpyxl") as writer:
            if bs_files:
                bs_df = combiner.combine_all_bs(bs_files)
                if not bs_df.empty:
                    bs_df.to_excel(writer, sheet_name="Balance Sheet", index=False)
                    click.echo("Balance Sheet data written.")
                else:
                    click.echo("No Balance Sheet data extracted.")
            else:
                click.echo("No Balance Sheet files found.")

            if is_files:
                is_df = combiner.combine_all_is(is_files)
                if not is_df.empty:
                    is_df.to_excel(writer, sheet_name="Income Statement", index=False)
                    click.echo("Income Statement data written.")
                else:
                    click.echo("No Income Statement data extracted.")
            else:
                click.echo("No Income Statement files found.")
                
        click.echo(f"[SUCCESS] All data written to {config.OUTPUT_FILE}")
        
    except Exception as e:
        click.echo(f"[ERROR] Error processing files: {str(e)}")
        if verbose:
            import traceback
            click.echo(traceback.format_exc())
        sys.exit(1)

@main.command("info")
def show_info():
    """Shows configuration and file information."""
    click.echo("TB Processor Configuration:")
    click.echo(f"  Input Directory: {config.INPUT_DIR}")
    click.echo(f"  Output File: {config.OUTPUT_FILE}")
    click.echo(f"  Balance Sheet Pattern: {config.BS_PATTERN}")
    click.echo(f"  Income Statement Pattern: {config.IS_PATTERN}")
    click.echo()
    
    bs_files = file_utils.find_monthly_files(config.BS_PATTERN)
    is_files = file_utils.find_monthly_files(config.IS_PATTERN)
    
    click.echo(f"Found {len(bs_files)} Balance Sheet files:")
    for f in bs_files:
        click.echo(f"  - {f.name}")
        
    click.echo(f"Found {len(is_files)} Income Statement files:")
    for f in is_files:
        click.echo(f"  - {f.name}")

if __name__ == "__main__":
    main()
