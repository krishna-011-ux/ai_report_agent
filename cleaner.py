"""
Data Cleaner
------------
Prepares raw data for analysis by:
- Removing duplicate rows
- Filling missing values
- Converting date columns to proper datetime format
"""

import pandas as pd


def clean_data(
    df: pd.DataFrame,
    cleaning_config: dict
) -> pd.DataFrame:

    df = df.copy()

    original_rows = len(df)

    # 1. Remove duplicate rows
    if cleaning_config.get(
        "drop_duplicates",
        True
    ):
        df = df.drop_duplicates()


    # 2. Convert date columns to datetime format
    for col in cleaning_config.get(
        "date_columns",
        []
    ):

        if col in df.columns:

            df[col] = pd.to_datetime(
                df[col],
                errors="coerce"
            )


    # 3. Fill missing values based on column data type
    numeric_fill = cleaning_config.get(
        "fill_missing_numeric_with",
        0
    )

    text_fill = cleaning_config.get(
        "fill_missing_text_with",
        "Unknown"
    )


    for col in df.columns:

        if pd.api.types.is_numeric_dtype(
            df[col]
        ):

            df[col] = df[col].fillna(
                numeric_fill
            )

        elif pd.api.types.is_datetime64_any_dtype(
            df[col]
        ):

            # Date columns are not force-filled.
            continue

        else:

            df[col] = df[col].fillna(
                text_fill
            )


    cleaned_rows = len(df)

    print(
        f"[Cleaner] Rows: {original_rows} -> "
        f"{cleaned_rows} (after cleaning)"
    )

    return df
