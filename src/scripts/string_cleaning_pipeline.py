import pandas as pd


# ---------------------------------------------------------
# SAMPLE MESSY DATA
# ---------------------------------------------------------

data = {
    "name": [
        " John ",
        "JOHN",
        "john",
        " Sarah ",
        "SARAH",
        "sarah"
    ],
    "category": [
        " Electronics ",
        "electronics",
        "ELECTRONICS",
        " Clothing ",
        "clothing",
        "CLOTHING"
    ],
    "city": [
        "São Paulo",
        "Montréal",
        "New York!",
        "Delhi",
        " Mumbai ",
        "Bengaluru@"
    ],
    "segment": [
        "B2B",
        "b2b",
        "B 2 B",
        "business-to-business",
        "SME",
        "small medium enterprise"
    ]
}

df = pd.DataFrame(data)

print("\n========== ORIGINAL DATA ==========")
print(df)


# ---------------------------------------------------------
# TASK 1: STRIP WHITESPACE
# ---------------------------------------------------------

def strip_all_strings(df):
    """Remove leading and trailing whitespace from all text columns."""

    string_cols = df.select_dtypes(include=["object"]).columns

    print("\n========== WHITESPACE CLEANING ==========")

    for col in string_cols:

        before = df[col].nunique(dropna=False)

        # Count values containing leading/trailing whitespace
        whitespace_count = df[col].astype(str).apply(
            lambda x: x != x.strip()
        ).sum()

        df[col] = df[col].str.strip()

        after = df[col].nunique(dropna=False)

        print(
            f"{col}: {before} -> {after} unique values | "
            f"Whitespace fixed: {whitespace_count}"
        )

    return df


# Save before counts for comparison
print("\n========== BEFORE STRIP ==========")
print("Name:")
print(df["name"].value_counts())

print("\nCategory:")
print(df["category"].value_counts())

df = strip_all_strings(df)

print("\n========== AFTER STRIP ==========")
print("Name:")
print(df["name"].value_counts())

print("\nCategory:")
print(df["category"].value_counts())


# ---------------------------------------------------------
# TASK 2: NORMALIZE CASING
# ---------------------------------------------------------

def normalize_casing(df, columns_to_lower):
    """Convert selected text columns to lowercase."""

    for col in columns_to_lower:
        df[col] = df[col].str.lower()
        print(f"Normalized {col} to lowercase")

    return df


print("\n========== BEFORE CASING NORMALIZATION ==========")
print(df[["name", "category", "city"]].head())

# Business decision:
# Lowercase is used for consistent matching and grouping.
casing_columns = ["name", "category", "city"]

df = normalize_casing(df, casing_columns)

print("\n========== AFTER CASING NORMALIZATION ==========")
print(df[["name", "category", "city"]].head())


# ---------------------------------------------------------
# TASK 3: REMOVE SPECIAL CHARACTERS
# ---------------------------------------------------------

def remove_special_characters(df, columns):
    """
    Remove characters other than:
    A-Z, a-z, 0-9 and spaces.
    """

    pattern = r"[^a-zA-Z0-9 ]"

    for col in columns:
        df[col] = df[col].str.replace(
            pattern,
            "",
            regex=True
        )

        print(f"Removed special characters from {col}")

    return df


print("\n========== BEFORE SPECIAL CHARACTER CLEANING ==========")
print(df[["city"]].head(6))

df = remove_special_characters(df, ["city"])

print("\n========== AFTER SPECIAL CHARACTER CLEANING ==========")
print(df[["city"]].head(6))


# ---------------------------------------------------------
# TASK 4: STANDARDIZE CATEGORIES USING MAPPING
# ---------------------------------------------------------

segment_map = {
    "b2b": "B2B",
    "b 2 b": "B2B",
    "business-to-business": "B2B",

    "sme": "SMB",
    "small medium enterprise": "SMB",

    "enterprise": "Enterprise"
}

print("\n========== SEGMENT BEFORE MAPPING ==========")
print(df["segment"].value_counts())

df["segment"] = df["segment"].replace(segment_map)

print("\n========== SEGMENT AFTER MAPPING ==========")
print(df["segment"].value_counts())

print("\nMapping decision:")
print("B2B variations -> B2B")
print("SME variations -> SMB")
print("Enterprise -> Enterprise")


# ---------------------------------------------------------
# TASK 5: REUSABLE STRING CLEANING FUNCTION
# ---------------------------------------------------------

def clean_text_column(
    series,
    lowercase=True,
    strip=True,
    remove_special=False,
    mapping=None
):
    """
    Reusable function for cleaning any text column.

    Parameters:
        series: pandas Series
        lowercase: convert text to lowercase
        strip: remove leading/trailing spaces
        remove_special: remove special characters
        mapping: dictionary for standardizing values
    """

    result = series.copy()

    # Handle null values
    if result.isna().any():
        print(
            f"Warning: {result.isna().sum()} null values found"
        )

    if strip:
        result = result.str.strip()

    if lowercase:
        result = result.str.lower()

    if remove_special:
        result = result.str.replace(
            r"[^a-zA-Z0-9 ]",
            "",
            regex=True
        )

    if mapping:
        result = result.replace(mapping)

    return result


# Apply function to different columns
df["name"] = clean_text_column(
    df["name"],
    lowercase=True,
    strip=True
)

df["category"] = clean_text_column(
    df["category"],
    lowercase=True,
    strip=True
)

df["city"] = clean_text_column(
    df["city"],
    lowercase=True,
    strip=True,
    remove_special=True
)

df["segment"] = clean_text_column(
    df["segment"],
    lowercase=False,
    strip=True,
    mapping=segment_map
)


# ---------------------------------------------------------
# EDGE CASE TESTING
# ---------------------------------------------------------

print("\n========== EDGE CASE TESTING ==========")

test_cases = [
    "  Product A  ",
    "PRODUCT B",
    "Product_C",
    None,
    ""
]

test_series = pd.Series(test_cases)

result = clean_text_column(
    test_series,
    lowercase=True,
    strip=True,
    remove_special=True
)

print("\nBefore:")
print(test_series)

print("\nAfter:")
print(result)


# ---------------------------------------------------------
# FINAL DATA
# ---------------------------------------------------------

print("\n========== FINAL CLEAN DATA ==========")
print(df)

print("\n========== FINAL VALUE COUNTS ==========")

print("\nNames:")
print(df["name"].value_counts())

print("\nCategories:")
print(df["category"].value_counts())

print("\nCities:")
print(df["city"].value_counts())

print("\nSegments:")
print(df["segment"].value_counts())

print("\nString cleaning pipeline completed successfully!")