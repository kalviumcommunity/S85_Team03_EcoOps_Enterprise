import pandas as pd
import os

# ---------------------------------
# Sample Customer Dataset
# ---------------------------------

data = {
    "customer_id": [101, 102, None, 104, 105, 106],
    "age": [25, -5, 35, 180, 45, 29],
    "price": [250.0, -100.0, 500.0, 150.0, -20.0, 300.0],
    "birth_date": [
        "1999-05-20",
        "2050-01-01",
        "1988-11-15",
        "1975-06-30",
        "2035-08-10",
        "2000-12-25"
    ],
    "email": [
        "john@gmail.com",
        "alicegmail.com",
        "bob@yahoo.com",
        None,
        "emma@gmail.com",
        "test@example.com"
    ],
    "phone": [
        "9876543210",
        "12345",
        "9998887776",
        "abcdefghij",
        "9876501234",
        "9123456789"
    ],
    "start_date": [
        "2025-01-01",
        "2025-02-01",
        "2025-03-10",
        "2025-04-01",
        "2025-05-01",
        "2025-06-01"
    ],
    "end_date": [
        "2025-01-10",
        "2025-01-20",
        "2025-03-15",
        "2025-03-20",
        "2025-05-15",
        "2025-06-20"
    ]
}

df = pd.DataFrame(data)

# ---------------------------------
# Convert Date Columns
# ---------------------------------

df["birth_date"] = pd.to_datetime(df["birth_date"])
df["start_date"] = pd.to_datetime(df["start_date"])
df["end_date"] = pd.to_datetime(df["end_date"])

# ---------------------------------
# Task 1 - Range Checks
# ---------------------------------

df["valid_age"] = (df["age"] >= 0) & (df["age"] <= 150)

df["valid_price"] = df["price"] >= 0

df["valid_date"] = (
    (df["birth_date"] >= pd.Timestamp("1920-01-01")) &
    (df["birth_date"] <= pd.Timestamp.now())
)

print("Invalid Ages:", (~df["valid_age"]).sum())
print("Invalid Prices:", (~df["valid_price"]).sum())
print("Invalid Birth Dates:", (~df["valid_date"]).sum())

# ---------------------------------
# Task 2 - Null Constraints
# ---------------------------------

df["valid_customer_id"] = df["customer_id"].notna()
df["valid_email"] = df["email"].notna()

print("Missing Customer IDs:", (~df["valid_customer_id"]).sum())
print("Missing Emails:", (~df["valid_email"]).sum())

# ---------------------------------
# Task 3 - Format Validation
# ---------------------------------

df["valid_email_format"] = df["email"].str.contains("@", na=False)

df["valid_phone"] = df["phone"].str.match(r"^\d{10}$", na=False)

print("Invalid Email Format:", (~df["valid_email_format"]).sum())
print("Invalid Phone Numbers:", (~df["valid_phone"]).sum())

# ---------------------------------
# Task 4 - Business Rule
# ---------------------------------

df["valid_date_order"] = df["end_date"] >= df["start_date"]

print("Invalid Date Order:", (~df["valid_date_order"]).sum())

# ---------------------------------
# Task 5 - Validation Report
# ---------------------------------

validation_cols = [
    "valid_age",
    "valid_price",
    "valid_date",
    "valid_customer_id",
    "valid_email",
    "valid_email_format",
    "valid_phone",
    "valid_date_order"
]

df["passes_all_checks"] = df[validation_cols].all(axis=1)

os.makedirs("output", exist_ok=True)

failures = df[~df["passes_all_checks"]]

failures.to_csv(
    "output/validation_failures.csv",
    index=False
)

df_clean = df[df["passes_all_checks"]]

print("\n========== Validation Report ==========")
print("Total Records :", len(df))
print("Passed :", df["passes_all_checks"].sum())
print("Failed :", (~df["passes_all_checks"]).sum())
print("Clean Records :", len(df_clean))
print("Failure File : output/validation_failures.csv")

print("\nClean Dataset")
print(df_clean)