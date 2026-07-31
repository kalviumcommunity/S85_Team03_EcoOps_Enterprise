"""
Dataset cleaning utilities.

This module contains reusable functions for cleaning
raw datasets before transformation.
"""

import pandas as pd


def clean_dataset(dataframe: pd.DataFrame) -> pd.DataFrame:
    """
    Clean a dataset.

    Operations:
    - Remove duplicate rows.
    - Trim whitespace from text columns.

    Args:
        dataframe: Raw dataset.

    Returns:
        Cleaned dataset.
    """

    cleaned_dataframe = dataframe.copy()

    # Remove duplicate rows
    cleaned_dataframe = cleaned_dataframe.drop_duplicates()

    # Trim whitespace from string columns
    string_columns = cleaned_dataframe.select_dtypes(
        include=["object", "string"],
    ).columns

    for column in string_columns:
        cleaned_dataframe[column] = (
            cleaned_dataframe[column]
            .astype(str)
            .str.strip()
        )

    return cleaned_dataframe
