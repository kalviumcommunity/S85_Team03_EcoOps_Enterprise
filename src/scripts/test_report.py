import pandas as pd
from datetime import datetime
from report_generator import generate_report

data = {
    "revenue": [1000, 2000, 1500, 3000],
    "customer_id": [101, 102, 103, 101],
    "segment": ["Technology", "Retail", "Technology", "Retail"]
}

df = pd.DataFrame(data)

report = generate_report(
    df,
    datetime.now().date()
)

print(report)