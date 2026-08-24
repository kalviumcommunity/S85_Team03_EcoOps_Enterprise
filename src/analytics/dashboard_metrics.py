"""Pure analytics helpers used by the Streamlit dashboard."""

from collections.abc import Iterable

import pandas as pd


def find_column(dataframe: pd.DataFrame, candidates: Iterable[str]) -> str | None:
    """Return the first case-insensitive column match from candidates."""
    columns_by_name = {str(column).lower(): column for column in dataframe.columns}
    return next(
        (columns_by_name[candidate.lower()] for candidate in candidates if candidate.lower() in columns_by_name),
        None,
    )


def calculate_kpis(
    dataframe: pd.DataFrame, value_column: str | None = None
) -> dict[str, float | int | None]:
    """Calculate dashboard KPIs from the supplied, already-filtered data."""
    if dataframe.empty:
        return {
            "total_value": None,
            "average_value": None,
            "records": 0,
            "customers": 0,
            "quality": 100.0,
        }

    numeric_columns = dataframe.select_dtypes(include="number").columns.tolist()
    value_column = value_column or (numeric_columns[0] if numeric_columns else None)
    total_cells = dataframe.shape[0] * dataframe.shape[1]
    null_percentage = dataframe.isna().sum().sum() / total_cells * 100

    customer_column = find_column(dataframe, ("customer_id", "user_id", "customer"))
    return {
        "total_value": dataframe[value_column].sum() if value_column else None,
        "average_value": dataframe[value_column].mean() if value_column else None,
        "records": len(dataframe),
        "customers": dataframe[customer_column].nunique() if customer_column else len(dataframe),
        "quality": 100 - null_percentage,
    }


def aggregate_values(
    dataframe: pd.DataFrame,
    group_column: str,
    value_column: str,
    aggregation: str,
) -> pd.Series:
    """Aggregate a numeric column for a chart using a named operation."""
    grouped_values = dataframe.groupby(group_column)[value_column]
    if aggregation == "Average":
        return grouped_values.mean()
    if aggregation == "Count":
        return grouped_values.count()
    return grouped_values.sum()


def build_quality_summary(dataframe: pd.DataFrame) -> pd.DataFrame:
    """Build a consistent per-column data-quality report."""
    return pd.DataFrame(
        {
            "Column": dataframe.columns,
            "Data Type": dataframe.dtypes.astype(str).values,
            "Unique Values": [
                dataframe[column].nunique(dropna=True) for column in dataframe.columns
            ],
            "Missing Values": dataframe.isna().sum().values,
            "Completeness %": dataframe.notna().mean().mul(100).round(1).values,
        }
    )
