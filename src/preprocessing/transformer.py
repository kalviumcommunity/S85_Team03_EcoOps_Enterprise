"""
Dataset transformation utilities.

This module transforms cleaned datasets into
analysis-ready datasets.
"""

import pandas as pd


def transform_dataset(
    dataset_name: str,
    dataframe: pd.DataFrame,
) -> pd.DataFrame:
    """
    Transform a cleaned dataset.

    Args:
        dataset_name: Dataset name.
        dataframe: Cleaned dataset.

    Returns:
        Transformed dataset.
    """

    transformed_dataframe = dataframe.copy()

    if dataset_name == "interactions":

        transformed_dataframe["timestamp"] = pd.to_datetime(
            transformed_dataframe["timestamp"],
            errors="coerce",
        )

        transformed_dataframe["price"] = pd.to_numeric(
            transformed_dataframe["price"],
            errors="coerce",
        )

        transformed_dataframe["rating"] = pd.to_numeric(
            transformed_dataframe["rating"],
            errors="coerce",
        )

    elif dataset_name == "products":

        transformed_dataframe["price"] = pd.to_numeric(
            transformed_dataframe["price"],
            errors="coerce",
        )

        transformed_dataframe["final_quality"] = pd.to_numeric(
            transformed_dataframe["final_quality"],
            errors="coerce",
        )

        transformed_dataframe["rating_count"] = pd.to_numeric(
            transformed_dataframe["rating_count"],
            errors="coerce",
        ).astype("Int64")

    elif dataset_name == "users":

        transformed_dataframe["loyalty"] = pd.to_numeric(
            transformed_dataframe["loyalty"],
            errors="coerce",
        )

        transformed_dataframe["price_sensitivity"] = pd.to_numeric(
            transformed_dataframe["price_sensitivity"],
            errors="coerce",
        )

    elif dataset_name == "sellers":

        transformed_dataframe["quality"] = pd.to_numeric(
            transformed_dataframe["quality"],
            errors="coerce",
        )

    return transformed_dataframe