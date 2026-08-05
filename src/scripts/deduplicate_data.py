import pandas as pd
import numpy as np
import json
import os
from datetime import datetime


# ============================================================
# TASK 1 - Detect Exact Duplicates
# ============================================================

def detect_exact_duplicates(df):
    """
    Find rows where all values are identical.

    Returns:
        Tuple of exact duplicate count and duplicate rows.
    """

    exact_dups = df.duplicated().sum()

    dup_rows = df[
        df.duplicated(keep=False)
    ].sort_values(by=df.columns.tolist())

    print("\nEXACT DUPLICATE DETECTION")
    print("=" * 60)

    print(f"Exact duplicates found: {exact_dups}")
    print(
        f"Total duplicate rows including originals: "
        f"{len(dup_rows)}"
    )

    if len(dup_rows) > 0:
        print("\nSample duplicate rows:")
        print(dup_rows.head(10).to_string())

    return exact_dups, dup_rows


# ============================================================
# TASK 2 - Detect Near-Duplicates Using Key Columns
# ============================================================

def detect_near_duplicates(df, key_columns):
    """
    Find rows with the same key values but potentially
    different other fields.
    """

    duplicate_keys = df[
        df.duplicated(
            subset=key_columns,
            keep=False
        )
    ]

    print("\nNEAR-DUPLICATE DETECTION")
    print("=" * 60)

    print(
        f"Records with duplicate keys: "
        f"{len(duplicate_keys)}"
    )

    unique_groups = duplicate_keys.groupby(
        key_columns
    )

    print(
        f"Unique key combinations with duplicates: "
        f"{len(unique_groups)}"
    )

    if len(duplicate_keys) > 0:

        print("\nSample groups with duplicate keys:")

        for keys, group in list(unique_groups)[:3]:

            print(f"\nKey: {keys}")
            print(f"Records in group: {len(group)}")
            print(group.to_string())

    return duplicate_keys


# ============================================================
# TASK 3 - Remove Exact Duplicates
# ============================================================

def remove_exact_duplicates(df, keep="first"):
    """
    Remove exact duplicates.

    keep options:
        first - keep first record
        last  - keep last record
        False - remove all duplicate records
    """

    rows_before = len(df)

    df_dedup = df.drop_duplicates(
        keep=keep
    ).copy()

    rows_after = len(df_dedup)

    rows_removed = rows_before - rows_after

    if rows_before > 0:
        removal_pct = (
            rows_removed / rows_before
        ) * 100
    else:
        removal_pct = 0

    print("\nEXACT DUPLICATE REMOVAL")
    print("=" * 60)

    print(f"Keep strategy: {keep}")
    print(f"Rows before: {rows_before:,}")
    print(f"Rows after:  {rows_after:,}")
    print(
        f"Rows removed: {rows_removed:,} "
        f"({removal_pct:.2f}%)"
    )

    return df_dedup


# ============================================================
# TASK 4 - Remove Near-Duplicates
# ============================================================

def remove_near_duplicates(
    df,
    key_columns,
    keep_strategy="most_complete"
):
    """
    Remove near-duplicates based on key columns.

    Strategies:
        most_complete - keep record with fewest nulls
        last          - keep last record
        first         - keep first record
    """

    rows_before = len(df)

    if keep_strategy == "most_complete":

        # Calculate number of missing values in each row
        null_counts = df.isnull().sum(axis=1)

        temp_df = df.copy()

        temp_df["_null_count"] = null_counts

        # Sort so most complete record comes first
        temp_df = temp_df.sort_values(
            by=key_columns + ["_null_count"]
        )

        # Keep most complete record
        df_dedup = temp_df.drop_duplicates(
            subset=key_columns,
            keep="first"
        ).drop(
            columns=["_null_count"]
        )

        # Restore normal index
        df_dedup = df_dedup.reset_index(drop=True)

    elif keep_strategy == "last":

        df_dedup = df.drop_duplicates(
            subset=key_columns,
            keep="last"
        ).reset_index(drop=True)

    else:

        df_dedup = df.drop_duplicates(
            subset=key_columns,
            keep="first"
        ).reset_index(drop=True)

    rows_after = len(df_dedup)

    rows_removed = rows_before - rows_after

    if rows_before > 0:
        removal_pct = (
            rows_removed / rows_before
        ) * 100
    else:
        removal_pct = 0

    print("\nNEAR-DUPLICATE REMOVAL")
    print("=" * 60)

    print(f"Keep strategy: {keep_strategy}")
    print(f"Key columns: {key_columns}")
    print(f"Rows before: {rows_before:,}")
    print(f"Rows after:  {rows_after:,}")

    print(
        f"Rows removed: {rows_removed:,} "
        f"({removal_pct:.2f}%)"
    )

    return df_dedup


# ============================================================
# TASK 5 - Log Removed Records
# ============================================================

def log_removed_duplicates(
    df_original,
    df_dedup
):
    """
    Save removed duplicate rows to an audit file.
    """

    # Add temporary IDs so we can track original rows
    original = df_original.copy()
    dedup = df_dedup.copy()

    original["_original_row_id"] = range(
        len(original)
    )

    # Since deduplication can change indexes,
    # identify removed records by comparing row values.
    original_compare = original.drop(
        columns=["_original_row_id"]
    )

    dedup_compare = dedup.copy()

    removed_records = original[
        ~original_compare.apply(
            tuple,
            axis=1
        ).isin(
            dedup_compare.apply(
                tuple,
                axis=1
            )
        )
    ].copy()

    removed_records = removed_records.drop(
        columns=["_original_row_id"]
    )

    os.makedirs(
        "output",
        exist_ok=True
    )

    removed_records.to_csv(
        "output/removed_duplicates_audit.csv",
        index=False
    )

    print("\nAUDIT LOGGING")
    print("=" * 60)

    print(
        f"Total records removed: "
        f"{len(removed_records)}"
    )

    print(
        "Removed records saved to "
        "output/removed_duplicates_audit.csv"
    )

    audit_summary = {
        "removal_timestamp": datetime.now().isoformat(),
        "total_removed": int(
            len(removed_records)
        ),
        "reason": (
            "Duplicate detection and "
            "deduplication"
        ),
        "audit_file": (
            "output/removed_duplicates_audit.csv"
        ),
        "audit_note": (
            "All removed records logged for "
            "compliance and recovery if needed"
        )
    }

    with open(
        "output/dedup_audit_summary.json",
        "w"
    ) as f:

        json.dump(
            audit_summary,
            f,
            indent=2
        )

    print(
        "Audit summary saved to "
        "output/dedup_audit_summary.json"
    )

    return removed_records, audit_summary


# ============================================================
# TASK 6 - Compare Before and After
# ============================================================

def compare_before_after(
    df_original,
    df_dedup
):
    """
    Compare dataset before and after deduplication.
    """

    rows_before = len(df_original)
    rows_after = len(df_dedup)

    rows_removed = (
        rows_before - rows_after
    )

    if rows_before > 0:
        removal_percentage = round(
            (rows_removed / rows_before) * 100,
            2
        )
    else:
        removal_percentage = 0

    comparison = {
        "rows_before": rows_before,
        "rows_after": rows_after,
        "rows_removed": rows_removed,
        "removal_percentage": removal_percentage,
        "columns": len(df_original.columns),
        "nulls_before": int(
            df_original.isnull().sum().sum()
        ),
        "nulls_after": int(
            df_dedup.isnull().sum().sum()
        ),
        "timestamp": datetime.now().isoformat()
    }

    print("\n" + "=" * 70)
    print("DEDUPLICATION FINAL SUMMARY")
    print("=" * 70)

    print(
        f"Rows before: {rows_before:,}"
    )

    print(
        f"Rows after:  {rows_after:,}"
    )

    print(
        f"Removed:     {rows_removed:,} "
        f"({removal_percentage}%)"
    )

    print(
        f"\nNulls before: "
        f"{comparison['nulls_before']:,}"
    )

    print(
        f"Nulls after:  "
        f"{comparison['nulls_after']:,}"
    )

    print(
        f"Null change:  "
        f"{comparison['nulls_before'] - comparison['nulls_after']:,}"
    )

    print("=" * 70)

    with open(
        "output/dedup_summary.json",
        "w"
    ) as f:

        json.dump(
            comparison,
            f,
            indent=2
        )

    return comparison


# ============================================================
# TASK 7 - Main Workflow
# ============================================================

if __name__ == "__main__":

    # Create output directories
    os.makedirs("output", exist_ok=True)
    os.makedirs("data/processed", exist_ok=True)

    # Load raw data
    df = pd.read_csv(
        "data/raw/data_with_dupes.csv"
    )

    print("\n" + "=" * 70)
    print("STARTING DEDUPLICATION WORKFLOW")
    print("=" * 70)

    print(
        f"Initial record count: "
        f"{len(df):,}"
    )

    # Keep original copy for audit
    df_original = df.copy()

    # ----------------------------------------
    # Step 1
    # ----------------------------------------

    print(
        "\n[Step 1/4] "
        "Detecting exact duplicates..."
    )

    exact_count, exact_rows = (
        detect_exact_duplicates(df)
    )

    # ----------------------------------------
    # Step 2
    # ----------------------------------------

    print(
        "\n[Step 2/4] "
        "Detecting near-duplicates by key..."
    )

    near_dups = detect_near_duplicates(
        df,
        key_columns=[
            "customer_id",
            "transaction_date"
        ]
    )

    # ----------------------------------------
    # Step 3
    # ----------------------------------------

    print(
        "\n[Step 3/4] "
        "Removing exact duplicates..."
    )

    df = remove_exact_duplicates(
        df,
        keep="first"
    )

    # ----------------------------------------
    # Step 4
    # ----------------------------------------

    print(
        "\n[Step 4/4] "
        "Removing near-duplicates..."
    )

    df = remove_near_duplicates(
        df,
        key_columns=[
            "customer_id",
            "transaction_date"
        ],
        keep_strategy="most_complete"
    )

    # ----------------------------------------
    # Audit
    # ----------------------------------------

    print(
        "\n[Audit] "
        "Logging removed records..."
    )

    log_removed_duplicates(
        df_original,
        df
    )

    # ----------------------------------------
    # Comparison
    # ----------------------------------------

    compare_before_after(
        df_original,
        df
    )

    # ----------------------------------------
    # Save final dataset
    # ----------------------------------------

    output_path = (
        "data/processed/"
        "deduplicated_data.csv"
    )

    df.to_csv(
        output_path,
        index=False
    )

    print(
        f"\nDeduplicated data saved to "
        f"{output_path}"
    )

    print("\nWORKFLOW COMPLETED SUCCESSFULLY!")