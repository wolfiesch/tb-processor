import os

# Allow override by environment variables
INPUT_DIR = os.environ.get('TB_INPUT_DIR', './')  # Current directory as default
OUTPUT_FILE = os.environ.get('TB_OUTPUT_FILE', "tb_full.xlsx")
BS_PATTERN = os.environ.get('TB_BS_PATTERN', "Balance Sheet by Month-*.xlsx")
IS_PATTERN = os.environ.get('TB_IS_PATTERN', "Profit and Loss by Month-*.xlsx")
