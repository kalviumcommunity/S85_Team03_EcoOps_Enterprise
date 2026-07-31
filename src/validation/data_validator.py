"""
Data Validator

Validates the schema of every raw dataset.
"""

import pandas as pd

from src.config.paths import RAW_DATA_DIR
from src.config.schema import EXPECTED_SCHEMAS


def validate_dataset_schema(
    dataset_name: str,
    dataframe: pd.DataFrame,
) -> bool:
    """
    Validate that a dataset contains the expected columns.

    Args:
        dataset_name: Dataset name.
        dataframe: Loaded DataFrame.

    Returns:
        True if schema is valid, otherwise False.
    """

    expected_columns = EXPECTED_SCHEMAS.get(dataset_name)

    if expected_columns is None:
        print(f"❌ No schema defined for '{dataset_name}'")
        return False

    actual_columns = set(dataframe.columns)
    expected_columns = set(expected_columns)

    missing_columns = expected_columns - actual_columns
    extra_columns = actual_columns - expected_columns

    print(f"\nValidating {dataset_name}.csv")

    if missing_columns:
        print("❌ Missing columns:")
        for column in sorted(missing_columns):
            print(f"   - {column}")

    if extra_columns:
        print("⚠️ Unexpected columns:")
        for column in sorted(extra_columns):
            print(f"   - {column}")

    if not missing_columns and not extra_columns:
        print("✅ Schema validation passed.")
        return True

    return False

def validate_missing_values(
    dataset_name: str,
    dataframe: pd.DataFrame,
) -> bool:
    """
    Validate missing values in a dataset.

    Args:
        dataset_name: Name of the dataset.
        dataframe: Dataset to validate.

    Returns:
        True if validation passes, otherwise False.
    """

    print("Checking missing values...")

    # Count missing values
    missing_values = dataframe.isnull().sum()

    # Business rule:
    # 'rating' is optional in interactions.csv
    if dataset_name == "interactions":
        missing_values = missing_values.drop(
            labels=["rating"],
            errors="ignore",
        )

    missing_columns = missing_values[missing_values > 0]

    if missing_columns.empty:
        print("✅ Missing value validation passed.")
        return True

    print("❌ Missing values found:")

    for column, count in missing_columns.items():
        print(f"   - {column}: {count}")

    return False

def validate_duplicate_rows(
    dataset_name: str,
    dataframe: pd.DataFrame,
) -> bool:
    """
    Validate duplicate rows in a dataset.

    Args:
        dataset_name: Name of the dataset.
        dataframe: Dataset to validate.

    Returns:
        True if validation passes, otherwise False.
    """

    print("Checking duplicate rows...")

    duplicate_count = dataframe.duplicated().sum()

    if duplicate_count == 0:
        print("✅ Duplicate row validation passed.")
        return True

    print(f"❌ Duplicate rows found: {duplicate_count}")

    return False

def validate_business_rules(
    dataset_name: str,
    dataframe: pd.DataFrame,
) -> bool:
    """
    Validate business-specific rules for each dataset.

    Args:
        dataset_name: Name of the dataset.
        dataframe: Dataset to validate.

    Returns:
        True if all business rules pass, otherwise False.
    """

    print("Checking business rules...")

    validation_passed = True

    if dataset_name == "interactions":

        # Price must be positive
        if (dataframe["price"] <= 0).any():
            print("❌ Invalid price values detected.")
            validation_passed = False

        # Ratings (when present) must be between 1 and 5
        ratings = dataframe["rating"].dropna()

        if not ratings.between(1, 5).all():
            print("❌ Invalid rating values detected.")
            validation_passed = False

        # Allowed actions
        allowed_actions = {"VIEW", "BUY"}

        invalid_actions = dataframe.loc[
            ~dataframe["action"].isin(allowed_actions),
            "action",
        ]

        if not invalid_actions.empty:
            print("❌ Invalid action values detected.")
            validation_passed = False

    elif dataset_name == "products":

        if (dataframe["price"] <= 0).any():
            print("❌ Invalid product prices detected.")
            validation_passed = False

        if not dataframe["final_quality"].between(0, 1).all():
            print("❌ Invalid final_quality values detected.")
            validation_passed = False

        if (dataframe["rating_count"] < 0).any():
            print("❌ Invalid rating_count values detected.")
            validation_passed = False

    elif dataset_name == "users":

        if not dataframe["loyalty"].between(0, 1).all():
            print("❌ Invalid loyalty values detected.")
            validation_passed = False

        if not dataframe["price_sensitivity"].between(0, 1).all():
            print("❌ Invalid price_sensitivity values detected.")
            validation_passed = False

    elif dataset_name == "sellers":

        if (dataframe["quality"] <= 0).any():
            print("❌ Invalid seller quality values detected.")
            validation_passed = False

    if validation_passed:
        print("✅ Business rule validation passed.")

    return validation_passed

def main() -> None:
    """
    Validate all datasets in the raw data directory.
    """

    overall_status = True

    for csv_file in sorted(RAW_DATA_DIR.glob("*.csv")):

        dataset_name = csv_file.stem
        dataframe = pd.read_csv(csv_file)

        schema_valid = validate_dataset_schema(
            dataset_name,
            dataframe,
        )

        missing_valid = validate_missing_values(
            dataset_name,
            dataframe,
        )

        duplicate_valid = validate_duplicate_rows(
            dataset_name,
            dataframe,
        )

        business_valid = validate_business_rules(
            dataset_name,
            dataframe,
        )

        overall_status = (
            overall_status
            and schema_valid
            and missing_valid
            and duplicate_valid
            and business_valid
        )

    print("\n" + "=" * 60)

    if overall_status:
        print("✅ All datasets passed schema validation.")
    else:
        print("❌ Schema validation failed.")

    print("=" * 60)


if __name__ == "__main__":
    main()