"""Run ingestion, cleaning, aggregation, and file output from the CLI."""

import argparse
import logging
from pathlib import Path

import pandas as pd

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s",
)
logger = logging.getLogger(__name__)


COLUMN_ALIASES = {
    "customer_id": ("customer_id", "user_id", "customer"),
    "amount": ("amount", "revenue", "price", "order_amount"),
    "segment": ("segment", "category", "customer_segment"),
    "order_id": ("order_id", "transaction_id", "id"),
}


def _find_column(dataframe: pd.DataFrame, names: tuple[str, ...]) -> str | None:
    columns = {str(column).lower(): column for column in dataframe.columns}
    return next((columns[name] for name in names if name in columns), None)


def ingest(path: str | Path) -> pd.DataFrame:
    """Read a CSV file and log the ingested record count."""
    input_path = Path(path)
    logger.info("Ingesting: %s", input_path)
    dataframe = pd.read_csv(input_path)
    logger.info("Rows ingested: %d", len(dataframe))
    return dataframe


def clean(dataframe: pd.DataFrame) -> pd.DataFrame:
    """Normalize common source names and retain valid positive transactions."""
    logger.info("Cleaning...")
    initial_count = len(dataframe)
    cleaned = dataframe.copy()

    for canonical_name, aliases in COLUMN_ALIASES.items():
        source_column = _find_column(cleaned, aliases)
        if source_column is None:
            if canonical_name in {"customer_id", "amount"}:
                raise ValueError(
                    f"Input must include a column for {canonical_name}: {aliases}"
                )
            continue
        if source_column != canonical_name:
            cleaned[canonical_name] = cleaned[source_column]

    cleaned["amount"] = pd.to_numeric(cleaned["amount"], errors="coerce")
    cleaned = cleaned.dropna(subset=["customer_id", "amount"])
    cleaned = cleaned[cleaned["amount"] > 0].copy()
    cleaned["customer_id"] = cleaned["customer_id"].astype(str).str.strip()
    cleaned = cleaned[cleaned["customer_id"] != ""]

    if "segment" not in cleaned:
        cleaned["segment"] = "Unknown"
    else:
        cleaned["segment"] = cleaned["segment"].fillna("Unknown").astype(str).str.strip()
        cleaned.loc[cleaned["segment"] == "", "segment"] = "Unknown"

    if "order_id" not in cleaned:
        cleaned["order_id"] = [f"generated_{index}" for index in cleaned.index]

    logger.info("Cleaned: %d -> %d rows", initial_count, len(cleaned))
    return cleaned.reset_index(drop=True)


def aggregate(dataframe: pd.DataFrame) -> pd.DataFrame:
    """Aggregate valid transactions by business segment."""
    logger.info("Aggregating...")
    aggregated = (
        dataframe.groupby("segment", dropna=False)
        .agg(
            revenue=("amount", "sum"),
            orders=("order_id", "count"),
            customers=("customer_id", "nunique"),
        )
        .reset_index()
        .sort_values("revenue", ascending=False)
        .reset_index(drop=True)
    )
    logger.info("Segments: %d", len(aggregated))
    return aggregated


def output(cleaned: pd.DataFrame, aggregated: pd.DataFrame, output_dir: str | Path) -> None:
    """Write cleaned transaction data and segment aggregates to output_dir."""
    destination = Path(output_dir)
    destination.mkdir(parents=True, exist_ok=True)
    cleaned.to_csv(destination / "cleaned.csv", index=False)
    aggregated.to_csv(destination / "aggregated.csv", index=False)
    logger.info("Output written to: %s", destination.resolve())


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Clean a transaction CSV and create segment aggregates."
    )
    parser.add_argument("--input", required=True, help="Path to the source CSV.")
    parser.add_argument(
        "--output",
        default="output",
        help="Directory for cleaned.csv and aggregated.csv.",
    )
    return parser.parse_args()


def main() -> None:
    """Execute all pipeline stages in order."""
    args = parse_args()
    raw_data = ingest(args.input)
    cleaned_data = clean(raw_data)
    aggregated_data = aggregate(cleaned_data)
    output(cleaned_data, aggregated_data, args.output)
    logger.info("Pipeline complete")


if __name__ == "__main__":
    main()
