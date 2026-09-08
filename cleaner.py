"""
Data Cleaner
------------
Raw data ko analysis-ready banata hai:
- Duplicate rows hatana
- Missing values fill karna
- Date columns ko proper datetime mein convert karna
"""

import pandas as pd


def clean_data(df: pd.DataFrame, cleaning_config: dict) -> pd.DataFrame:
    df = df.copy()
    original_rows = len(df)

    # 1. Duplicates hatao
    if cleaning_config.get("drop_duplicates", True):
        df = df.drop_duplicates()

    # 2. Date columns ko convert karo
    for col in cleaning_config.get("date_columns", []):
        if col in df.columns:
            df[col] = pd.to_datetime(df[col], errors="coerce")

    # 3. Missing values fill karo (numeric vs text alag se)
    numeric_fill = cleaning_config.get("fill_missing_numeric_with", 0)
    text_fill = cleaning_config.get("fill_missing_text_with", "Unknown")

    for col in df.columns:
        if pd.api.types.is_numeric_dtype(df[col]):
            df[col] = df[col].fillna(numeric_fill)
        elif pd.api.types.is_datetime64_any_dtype(df[col]):
            continue  # dates ko force-fill nahi karte
        else:
            df[col] = df[col].fillna(text_fill)

    cleaned_rows = len(df)
    print(f"[Cleaner] Rows: {original_rows} -> {cleaned_rows} (after cleaning)")

    return df
