"""
Preprocessing pipeline.

Loads validated datasets, applies cleaning and
transformation, and saves processed datasets.
"""

import pandas as pd

from src.config.paths import PROCESSED_DATA_DIR, RAW_DATA_DIR
from src.preprocessing.cleaner import clean_dataset
from src.preprocessing.transformer import transform_dataset

def run_pipeline() -> None:
    """
    Execute the preprocessing pipeline.
    """

    processed_count = 0

    PROCESSED_DATA_DIR.mkdir(
        parents=True,
        exist_ok=True,
    )

    csv_files = sorted(RAW_DATA_DIR.glob("*.csv"))

    print("=" * 60)
    print("Seller Trust Analytics Platform")
    print("Data Preprocessing Pipeline")
    print("=" * 60)

    for csv_file in csv_files:

        dataset_name = csv_file.stem

        dataframe = pd.read_csv(csv_file)

        dataframe = clean_dataset(dataframe)

        dataframe = transform_dataset(
            dataset_name,
            dataframe,
        )

        output_file = (
            PROCESSED_DATA_DIR /
            csv_file.name
        )

        dataframe.to_csv(
            output_file,
            index=False,
        )

        if output_file.exists():
            print(f"✅ Saved to: {output_file}")
            processed_count+=1
        else:
            print(f"❌ Failed to save: {output_file}")

        print(
            f"Processed: {csv_file.name} "
            f"({len(dataframe)} rows, {len(dataframe.columns)} columns)"
        )

    print("=" * 60)
    print("Preprocessing completed successfully.")
    print("=" * 60)
    print(f"Datasets Processed : {processed_count}")
    print(f"Output Directory   : {PROCESSED_DATA_DIR}")
    print("Status             : SUCCESS")
    print("=" * 60)


if __name__ == "__main__":
    run_pipeline()