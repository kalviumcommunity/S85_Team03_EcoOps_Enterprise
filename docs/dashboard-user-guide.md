# Dashboard User Guide

## Start the App

From the repository root, install the dependencies and launch Streamlit:

```powershell
pip install -r requirements.txt
streamlit run app.py
```

Open the local URL shown in the terminal, usually `http://localhost:8501`.

## Navigate the Dashboard

Use the **Navigation** control in the sidebar:

- **Business Overview** shows the KPI snapshot and metric notes.
- **Trend Analysis** shows the layout reserved for revenue and customer trends.
- **Data Explorer** is the interactive upload and filtering workspace.

Streamlit reruns the app when a navigation option or filter changes, so the visible content always reflects the latest selection.

## Explore Uploaded Data

1. Select **Data Explorer**.
2. Upload a CSV or JSON file.
3. Review the loaded filename, row count, column count, and null percentage.
4. Inspect the first 10 rows, column summary, descriptive statistics, and quick chart.

The uploaded DataFrame is stored in the current Streamlit session as `uploaded_data`.

## Use the Filters

For the complete filter experience, use these column names:

- `date`: date, datetime, or timestamp values
- `segment`: category labels such as Enterprise, Mid-Market, or SMB
- `revenue`: numeric revenue values

The sidebar defaults to the complete date range, every segment, and the full revenue range. The initial view therefore includes all valid records.

Every filter reruns the app and updates the record count, preview, statistics, and chart. Use **Reset Filters** to return to the original full-data view.

If a combination produces zero rows, the app displays a warning and asks you to broaden the selection. If a dataset lacks one of the conventional columns, the unavailable filter is explained in the sidebar.

## Try the Sample File

Use [`data/sample/dashboard_sample.csv`](../data/sample/dashboard_sample.csv) for a predictable demonstration. It contains all three filter fields and additional numeric columns for statistics and chart exploration.

## Supported Input Notes

- CSV files should have a header row.
- JSON files should be readable by `pandas.read_json`.
- Empty files and malformed files are rejected with a clear message.
- Numeric statistics exclude non-numeric columns automatically.
