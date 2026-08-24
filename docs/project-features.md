# Project Features

## Project Purpose

The Seller Trust Analytics Platform (STAP) is an analytics workspace for monitoring e-commerce marketplace health and seller trust. It is intended to help operations managers, seller quality analysts, and business analysts inspect performance data, identify risks, and prepare reports.

## Current Dashboard Features

The runnable Streamlit dashboard is available from the repository root with `streamlit run app.py`.

### Sidebar Navigation

The sidebar provides a radio navigation control with three sections:

- **Business Overview**: Displays the main marketplace KPI snapshot.
- **Trend Analysis**: Provides the layout for revenue and customer trend views.
- **Data Explorer**: Accepts user datasets and provides interactive inspection.

Only the selected section is rendered in the main content area. Streamlit reruns the script when a navigation control or other widget changes.

### Business Overview

The Overview section places the most important information above the fold in five KPI cards:

- Revenue
- Users
- Average order value (AOV)
- Churn
- Net Promoter Score (NPS)

It also includes a performance summary using columns and an expander containing metric methodology notes.

The values currently shown in the KPI cards are shell placeholders. They should be connected to processed marketplace data when the analytics layer is integrated.

### Trend Analysis

The Trends section establishes the visual hierarchy for future time-series analysis:

- Monthly revenue
- Period comparison
- Active customers over time
- Retention movement

The content is arranged in side-by-side columns, separated with section dividers, and includes an expander for trend methodology. The chart areas are currently placeholders awaiting calculated metrics and chart data.

### CSV and JSON Uploads

Data Explorer accepts `.csv` and `.json` files through `st.file_uploader`. Uploaded files are loaded into a Pandas DataFrame immediately.

The upload workflow handles common invalid states safely:

- No upload: shows an instruction message.
- Malformed file: shows a readable error instead of a traceback.
- Empty file: shows a warning and stops processing that upload.
- Unsupported extension: shows an unsupported-file error.

The loaded DataFrame is stored in Streamlit session state as `uploaded_data` for downstream use during the session.

### Automatic Dataset Preview

After a successful upload, Data Explorer displays:

- Loaded filename and record count
- Number of rows
- Number of columns
- Overall null percentage
- First 10 rows
- Column names
- Pandas data types
- Non-null counts
- Null counts and null percentages

### Interactive Data Filters

When the uploaded dataset contains the expected fields, the sidebar provides three filters:

- **Date Range**: Filters a `date`, `datetime`, or `timestamp` column.
- **Segments**: Filters a `segment` column with a multi-select control.
- **Revenue Range**: Filters a numeric `revenue` column with a slider.

Each filter defaults to the complete available range, so the full dataset is visible on first load. The displayed row count, preview, statistics, and chart all use the filtered DataFrame.

Datasets without one of these conventional columns remain usable. The sidebar explains which corresponding filter is unavailable.

### Filter Reset and Empty Results

The **Reset Filters** button clears the widget state and restores the full dataset defaults. If a valid filter combination returns no records, Data Explorer shows a warning asking the user to broaden the selection instead of failing.

### Basic Statistics and Exploration

Data Explorer calculates descriptive statistics for numeric columns, including count, mean, standard deviation, minimum, quartiles, and maximum.

The Quick Exploration control lets the user choose a numeric column and view the most frequent values in a bar chart. This demonstrates that uploaded data can feed downstream visual analysis without manual preprocessing.

### Operational Analytics Additions

Data Explorer also includes several workflow improvements:

- Chart aggregation can be switched between sum, average, and count.
- A data-quality audit reports data types, unique values, missing values, and completeness for every column.
- Integrity checks identify duplicate rows, fully complete rows, and constant columns.
- The current filtered result can be downloaded as CSV or JSON.
- Reset Filters also restores the chart aggregation default.

## Data and Processing Components

The repository separates raw data, processing logic, analytics, and validation:

- `data/raw/`: Source CSV files for interactions, products, sellers, and users.
- `data/processed/`: Intended location for cleaned and transformed datasets.
- `data/sample/`: Sample data used for development or demonstrations.
- `src/preprocessing/cleaner.py`: Cleaning operations.
- `src/preprocessing/transformer.py`: Data transformation operations.
- `src/preprocessing/pipeline.py`: Processing pipeline coordination.
- `src/profiling/data_profiler.py`: Dataset profiling functionality.
- `src/utils/validation/data_validator.py`: Data quality validation utilities.
- `src/config/paths.py`: Centralized project path definitions.
- `src/config/schema.py`: Data schema definitions.

## KPI and Analytics Components

The `kpi/` directory contains KPI-specific material:

- `kpi/kpi_functions.py`: KPI calculation functions.
- `kpi/kpi_reference.md`: Definitions and business meaning of KPIs.
- `kpi/kpi_validation_targets.json`: Expected validation targets.

The `src/analytics/` directory is reserved for reusable analytical logic. The `src/scripts/` directory contains focused workflows for behavioural analysis, correlation analysis, funnel analysis, distribution analysis, deduplication, merging, feature engineering, rolling metrics, reporting, and email delivery.

## Trust and Business Metrics

The wider platform is designed to support these marketplace measures:

- Seller Trust Score
- Average seller rating
- Return rate
- Review sentiment
- Delivery performance
- Risk classification
- Marketplace health score

The intended trust classifications are:

| Trust Score | Classification |
| --- | --- |
| 85-100 | Healthy |
| 70-84 | Under Monitoring |
| Below 70 | High Risk |

## Reporting and Future Capabilities

The project roadmap includes report export, daily data refresh, seller-level analytics, historical performance views, search and filtering, and business insights. Longer-term enhancements described in the project README include fraud detection, predictive risk analysis, sales forecasting, role-based access control, alerts, real-time analytics, and external marketplace integrations.

These roadmap items are not presented as completed dashboard features until their corresponding implementation is connected to the application.

## Running the Project

From the repository root:

```powershell
pip install -r requirements.txt
streamlit run app.py
```

Open the local URL printed by Streamlit, select **Data Explorer**, and upload a CSV or JSON file to inspect it. For the full filter experience, use columns named `date`, `segment`, and `revenue`.

## Batch Data Pipeline

The root `pipeline.py` provides a command-line workflow for ingestion, cleaning, aggregation, and output. It accepts any input and output paths:

```powershell
python pipeline.py --input data/raw/interactions.csv --output output
```

The pipeline logs each stage with a timestamp and writes `cleaned.csv` and `aggregated.csv`. It recognizes common aliases such as `user_id` for `customer_id`, `price` for `amount`, and `category` for `segment`. The aggregate includes revenue, order count, and unique customer count by segment.

The scheduled workflow at `.github/workflows/pipeline.yml` runs every Monday at 06:00 UTC and can also be started manually with GitHub Actions. It refreshes the generated `output/` files and commits changes using the GitHub Actions bot.
