import logging
import re
import os
from collections import defaultdict

import pandas as pd


def preprocess_file(src: str):
    """
    Reads a file (CSV or Excel), transforms all column names to lowercase
    and replaces spaces with underscores, rounds float columns, drops all
    null columns.
    """

    # 1. Read the file into a DataFrame
    file_path = None
    try:
        # Determine how to read the source: Excel, CSV, or an existing DataFrame
        if isinstance(src, str):
            file_path = src
            src_lower = src.lower()
            if src_lower.endswith(('.xls', '.xlsx')):
                df = pd.read_excel(src)
            elif src_lower.endswith('.csv'):
                df = pd.read_csv(src, encoding='utf-8')
            else:
                raise ValueError(f"Unsupported file type for source: {src}")
        elif isinstance(src, pd.DataFrame):
            df = src.copy()
        else:
            raise TypeError("Source must be a file path (str) or a pandas DataFrame.")

    except Exception as e:
        logging.error(f"Error reading source file/data: {e}")
        return None

    logging.info(f"Original dimension: {df.shape}")

    # 2. Transform the column names
    original_cols = df.columns
    # First: lowercase and replace spaces with underscore
    # Second: remove any characters that are NOT a-z, 0-9, or _
    new_cols = [re.sub(r'[^a-z0-9_]+', '', col.strip().lower().replace(' ', '_')) for col in original_cols]
    df.columns = new_cols

    logging.info("Column names transformed successfully.")
    logging.info(f"Original Columns: {list(original_cols)}")
    logging.info(f"New Columns:      {list(df.columns)}")

    # 3. Drop all null columns
    cols_before_drop = df.shape[1]
    df.dropna(axis=1, how='all', inplace=True)
    cols_dropped = cols_before_drop - df.shape[1]

    if cols_dropped > 0:
        logging.info(f"Dropped {cols_dropped} column(s) that were entirely null.")
    else:
        logging.info("No entirely null columns found to drop.")

    # 4. Round float columns to fewer decimal places
    float_cols = df.select_dtypes(include=['float']).columns.tolist()
    if float_cols:
        df[float_cols] = df[float_cols].round(3)
        logging.info(f"Rounded float columns to 3 decimal places: {float_cols}")
    else:
        logging.info("No float columns found to round.")

    # 5. Log columns name per dtypes
    dtype_groups = defaultdict(list)
    for col, dtype in df.dtypes.items():
        dtype_groups[str(dtype)].append(col)

    logging.info("--- Columns Grouped by DType ---")
    for dtype, columns in dtype_groups.items():
        logging.info(f"DType '{dtype}': {', '.join(columns)}")

    logging.info(f"post processing dimension: {df.shape}")
    logging.info("--------------------------------")

    # 6. Rewrite/Overwrite or Convert file
    if file_path:
        ext = os.path.splitext(file_path)[1].lower()

        try:
            if ext in ('.xls', '.xlsx'):
                # Overwrite existing Excel file
                os.remove(file_path)
                df.to_excel(file_path, index=False)
                logging.info(f"Successfully overwrote Excel file: {file_path}")

            elif ext == '.csv':
                os.remove(file_path)
                df.to_csv(file_path, index=False, encoding='utf-8')
                logging.info(f"Successfully overwrote CSV file: {file_path}")

        except Exception as e:
            # Re-raise error if it's not permission related, but log cleanly
            logging.error(f"Error writing/deleting file {file_path}. Details: {e}")

            # Check for the common missing engine error and provide specific advice
            if "No engine for filetype: 'xlsx'" in str(e) or "No engine for filetype" in str(e):
                logging.error(
                    "The error suggests a missing Excel engine. Ensure 'openpyxl' is installed: pip install openpyxl")

        finally:
            return file_path
