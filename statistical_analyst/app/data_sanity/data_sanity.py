import json
import logging

import pandas as pd
from pandas.api.types import infer_dtype


def analyze_columns(src):
    try:
        df = (
            pd.read_excel(src)
            if isinstance(src, str) and src.lower().endswith(('.xls', '.xlsx'))
            else (pd.read_csv(src) if isinstance(src, str) else src.copy())
        )
        cols = list(df.columns)
        # Header checks (log only when true)
        dup = [c for c in cols if cols.count(c) > 1]
        if dup:
            logging.info(json.dumps({"duplicate_headers": dup}))

        empty = [c for c in cols if str(c).strip() == '' or pd.isna(c)]
        if empty:
            logging.info(json.dumps({"empty_headers": empty}))

        # Column-level scan (log only if ANY check is true)
        for c in cols:
            s = df[c].dropna()

            info = {
                "all_null": s.empty,
                "mixed_types": 'mixed' in infer_dtype(s.tolist(), skipna=True),
                "json_like": any(isinstance(x, str) and x.strip().startswith(('{', '[')) for x in s.head(30)),
                "binary": any(isinstance(x, (bytes, bytearray)) for x in s.head(50)),
                "long_strings": any(isinstance(x, str) and len(x) > 1000 for x in s.head(50)),
            }

            # Log ONLY if at least one true
            if any(info.values()):
                logging.info(json.dumps({"column": c, **info}))
    except Exception as e:
        logging.error(f"Please review the files for quality issue , even the sanity check failed : {e}")
