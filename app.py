from io import BytesIO

import plotly.express as px
import streamlit as st
import pandas as pd

from src.analytics.dashboard_metrics import (
    aggregate_values,
    build_quality_summary,
    calculate_kpis,
    find_column,
)
from src.analytics.alerts import get_breached_alerts
from src.config.alerts import ALERT_THRESHOLDS


@st.cache_data
def load_data(file_bytes, file_name):
    """Load an uploaded dataset once per file and reuse it across reruns."""
    file_stream = BytesIO(file_bytes)
    if file_name.lower().endswith(".csv"):
        return pd.read_csv(file_stream)
    if file_name.lower().endswith(".json"):
        return pd.read_json(file_stream)
    raise ValueError("Unsupported file type.")


st.set_page_config(page_title="Analytics Dashboard", page_icon="📊", layout="wide")

st.sidebar.title("Navigation")
page = st.sidebar.radio("Go to", ["Overview", "Trends", "Data Explorer"])

if page == "Overview":
    st.title("Business Overview")

    st.header("Marketplace Snapshot")
    col1, col2, col3, col4, col5 = st.columns(5)
    with col1:
        st.metric("Revenue", "$5.2M", "+12.5%")
    with col2:
        st.metric("Users", "2,500", "+5.2%")
    with col3:
        st.metric("AOV", "$45", "+2.1%")
    with col4:
        st.metric("Churn", "5.2%", "-2.8%", delta_color="inverse")
    with col5:
        st.metric("NPS", "72", "+4")

    st.divider()

    st.header("Performance Summary")
    summary_col, action_col = st.columns(2)
    with summary_col:
        st.subheader("Current Position")
        st.write("Core marketplace KPIs are ready for analysis.")
    with action_col:
        st.subheader("Next Focus")
        st.write("Use Trends to inspect movement over time.")

    with st.expander("About These Metrics"):
        st.write(
            "Revenue is calculated as the sum of order amounts for the current "
            "month. Churn is the percentage of customers who did not return "
            "within 30 days."
        )

elif page == "Trends":
    st.title("Trend Analysis")

    st.header("Revenue Trends")
    trend_col, comparison_col = st.columns(2)
    with trend_col:
        st.subheader("Monthly Revenue")
        st.write("Time-series chart placeholder")
    with comparison_col:
        st.subheader("Period Comparison")
        st.write("Comparison chart placeholder")

    st.divider()

    st.header("Customer Metrics")
    customer_col, retention_col = st.columns(2)
    with customer_col:
        st.subheader("Active Customers Over Time")
        st.write("Customer trend placeholder")
    with retention_col:
        st.subheader("Retention Movement")
        st.write("Retention chart placeholder")

    with st.expander("Trend Methodology"):
        st.write(
            "Trend views will compare completed reporting periods using the "
            "same metric definitions as the Overview section."
        )

elif page == "Data Explorer":
    st.title("Data Explorer")

    st.header("Upload Dataset")
    uploaded_file = st.file_uploader(
        "Upload your dataset",
        type=["csv", "json"],
        help="CSV and JSON files are supported.",
    )

    if uploaded_file is None:
        st.info("Upload a CSV or JSON file to begin.")
    else:
        try:
            df = load_data(uploaded_file.getvalue(), uploaded_file.name)
        except Exception:
            st.error("Could not read this file. Check the format and try again.")
            st.stop()

        if df.empty:
            st.warning("Uploaded file is empty.")
            st.stop()

        st.session_state["uploaded_data"] = df
        st.success(
            f"Loaded: {uploaded_file.name} ({len(df):,} rows, "
            f"{len(df.columns):,} columns)"
        )

        date_column = find_column(df, ("date", "datetime", "timestamp"))
        segment_column = find_column(df, ("segment",))
        revenue_column = find_column(df, ("revenue",))

        st.sidebar.header("Filters")
        if st.sidebar.button("Reset Filters", key="reset_filters"):
            for filter_key in [
                "filter_date_range",
                "filter_segments",
                "filter_revenue_range",
                "chart_aggregation",
            ]:
                st.session_state.pop(filter_key, None)
            st.rerun()

        aggregation = st.sidebar.selectbox(
            "Chart aggregation",
            options=["Sum", "Average", "Count"],
            key="chart_aggregation",
            help="Choose how numeric values are summarized in the charts.",
        )

        filtered_df = df.copy()
        if date_column:
            parsed_dates = pd.to_datetime(df[date_column], errors="coerce")
            valid_dates = parsed_dates.dropna()
            if valid_dates.empty:
                st.sidebar.warning("No valid dates found; date filtering is disabled.")
            else:
                date_range = st.sidebar.date_input(
                    "Date Range",
                    value=(valid_dates.min().date(), valid_dates.max().date()),
                    key="filter_date_range",
                )
                if isinstance(date_range, tuple) and len(date_range) == 2:
                    start_date, end_date = date_range
                    filtered_df = filtered_df[
                        parsed_dates.between(
                            pd.Timestamp(start_date),
                            pd.Timestamp(end_date) + pd.Timedelta(days=1),
                            inclusive="left",
                        )
                    ]
        else:
            st.sidebar.info("No date column found; date filtering is unavailable.")

        if segment_column:
            all_segments = sorted(df[segment_column].dropna().unique().tolist())
            selected_segments = st.sidebar.multiselect(
                "Segments",
                options=all_segments,
                default=all_segments,
                key="filter_segments",
            )
            filtered_df = filtered_df[
                filtered_df[segment_column].isin(selected_segments)
            ]
        else:
            st.sidebar.info(
                "No segment column found; segment filtering is unavailable."
            )

        if revenue_column and pd.api.types.is_numeric_dtype(df[revenue_column]):
            minimum_revenue = int(df[revenue_column].min())
            maximum_revenue = int(df[revenue_column].max())
            if minimum_revenue < maximum_revenue:
                revenue_range = st.sidebar.slider(
                    "Revenue Range",
                    min_value=minimum_revenue,
                    max_value=maximum_revenue,
                    value=(minimum_revenue, maximum_revenue),
                    key="filter_revenue_range",
                )
                filtered_df = filtered_df[
                    filtered_df[revenue_column].between(*revenue_range)
                ]
            else:
                st.sidebar.metric("Revenue", f"{minimum_revenue:,}")
        else:
            st.sidebar.info(
                "No numeric revenue column found; revenue filtering is unavailable."
            )

        st.write(f"Showing {len(filtered_df):,} of {len(df):,} records")
        if filtered_df.empty:
            st.warning(
                "No data matches the current filters. "
                "Try broadening your selection."
            )
            st.stop()

        numeric_cols = filtered_df.select_dtypes(include="number").columns.tolist()
        metric_value_column = revenue_column or (
            numeric_cols[0] if numeric_cols else None
        )
        kpis = calculate_kpis(filtered_df, metric_value_column)
        total_revenue = kpis["total_value"]
        average_value = kpis["average_value"]
        unique_customers = kpis["customers"]
        null_pct = 100 - kpis["quality"]

        churn_column = find_column(
            filtered_df, ("churn_rate", "churn", "churn percentage")
        )
        churn_rate = None
        if churn_column and pd.api.types.is_numeric_dtype(
            filtered_df[churn_column]
        ):
            churn_rate = filtered_df[churn_column].mean()
        current_metrics = {
            "churn_rate": churn_rate,
            "avg_order_value": average_value,
            "null_percentage": null_pct,
        }

        st.header("Operational Alerts")
        breached_alerts = get_breached_alerts(current_metrics, ALERT_THRESHOLDS)
        for alert in breached_alerts:
            config = alert["config"]
            alert_text = (
                f"ALERT: {config['metric']} is {alert['value']:.1f} "
                f"(threshold: {config['threshold']:.1f}). {config['message']}"
            )
            if config["severity"] == "critical":
                st.error(alert_text)
            else:
                st.warning(alert_text)
        if not breached_alerts:
            st.success("All monitored metrics are within configured thresholds.")
        if churn_rate is None:
            st.caption(
                "Churn alerts are activated when the uploaded dataset contains "
                "a numeric churn_rate or churn column."
            )

        st.header("Key Performance Indicators")
        kpi_revenue, kpi_average, kpi_records, kpi_customers, kpi_quality = (
            st.columns(5)
        )
        with kpi_revenue:
            st.metric(
                "Revenue",
                f"${total_revenue:,.0f}" if total_revenue is not None else "N/A",
            )
        with kpi_average:
            st.metric(
                "Avg Value",
                f"${average_value:,.0f}" if average_value is not None else "N/A",
            )
        with kpi_records:
            st.metric("Records", f"{len(filtered_df):,}")
        with kpi_customers:
            st.metric("Customers", f"{unique_customers:,}")
        with kpi_quality:
            st.metric("Quality", f"{100 - null_pct:.1f}%")

        st.header("Filtered Analytics")
        chart_col, segment_col = st.columns(2)
        with chart_col:
            st.subheader("Revenue Over Time")
            if date_column and metric_value_column:
                chart_dates = pd.to_datetime(
                    filtered_df[date_column], errors="coerce"
                )
                trend_source = pd.DataFrame(
                    {"date": chart_dates, "value": filtered_df[metric_value_column]}
                ).dropna()
                trend_group = trend_source.groupby("date")["value"]
                if aggregation == "Average":
                    trend = trend_group.mean()
                elif aggregation == "Count":
                    trend = trend_group.count()
                else:
                    trend = trend_group.sum()
                st.line_chart(trend)
            else:
                st.info("A date and numeric column are required for this chart.")
        with segment_col:
            st.subheader("Revenue by Segment")
            if segment_column and metric_value_column:
                segment_values = aggregate_values(
                    filtered_df,
                    segment_column,
                    metric_value_column,
                    aggregation,
                )
                st.bar_chart(segment_values)
            else:
                st.info("Segment and numeric columns are required for this chart.")

        st.subheader("Value Distribution")
        if metric_value_column:
            distribution = px.histogram(
                filtered_df,
                x=metric_value_column,
                nbins=30,
                title=f"Distribution of {metric_value_column}",
            )
            st.plotly_chart(distribution, use_container_width=True)
        else:
            st.info("A numeric column is required for the distribution chart.")

        st.header("Dataset Preview")
        row_count, column_count, null_count = st.columns(3)
        with row_count:
            st.metric("Rows", f"{len(filtered_df):,}")
        with column_count:
            st.metric("Columns", f"{len(filtered_df.columns):,}")
        with null_count:
            total_cells = filtered_df.shape[0] * filtered_df.shape[1]
            null_pct = filtered_df.isnull().sum().sum() / total_cells * 100
            st.metric("Null %", f"{null_pct:.1f}%")

        st.subheader("First 10 Rows")
        st.dataframe(filtered_df.head(10), use_container_width=True)

        st.subheader("Column Summary")
        summary = pd.DataFrame(
            {
                "Column": filtered_df.columns,
                "Type": filtered_df.dtypes.astype(str).values,
                "Non-Null": filtered_df.notnull().sum().values,
                "Null Count": filtered_df.isnull().sum().values,
                "Null %": (
                    filtered_df.isnull().sum() / len(filtered_df) * 100
                ).round(1).values,
            }
        )
        st.dataframe(summary, use_container_width=True)

        st.subheader("Descriptive Statistics")
        if numeric_cols:
            st.dataframe(
                filtered_df[numeric_cols].describe(), use_container_width=True
            )
        else:
            st.info("No numeric columns are available for descriptive statistics.")

        st.subheader("Quick Exploration")
        if numeric_cols:
            selected_col = st.selectbox(
                "Select a column to visualise",
                numeric_cols,
            )
            st.bar_chart(filtered_df[selected_col].value_counts().head(20))
        else:
            st.info("Add a numeric column to enable the quick exploration chart.")

        st.header("Data Quality Audit")
        quality_col, duplicate_col = st.columns(2)
        with quality_col:
            st.subheader("Column Completeness")
            quality_summary = build_quality_summary(filtered_df)
            st.dataframe(quality_summary, use_container_width=True)
        with duplicate_col:
            st.subheader("Integrity Checks")
            duplicate_rows = int(filtered_df.duplicated().sum())
            constant_columns = [
                column
                for column in filtered_df.columns
                if filtered_df[column].nunique(dropna=False) <= 1
            ]
            st.metric("Duplicate Rows", f"{duplicate_rows:,}")
            st.metric("Complete Rows", f"{filtered_df.dropna().shape[0]:,}")
            if constant_columns:
                st.warning(
                    "Constant columns: " + ", ".join(map(str, constant_columns))
                )
            else:
                st.success("No constant columns detected.")

        st.header("Export Filtered Data")
        export_csv, export_json = st.columns(2)
        with export_csv:
            st.download_button(
                "Download CSV",
                data=filtered_df.to_csv(index=False).encode("utf-8"),
                file_name="filtered_dataset.csv",
                mime="text/csv",
                use_container_width=True,
            )
        with export_json:
            st.download_button(
                "Download JSON",
                data=filtered_df.to_json(orient="records", date_format="iso"),
                file_name="filtered_dataset.json",
                mime="application/json",
                use_container_width=True,
            )

    st.divider()

    st.header("Export")
    export_col, status_col = st.columns(2)
    with export_col:
        st.subheader("Available Formats")
        st.write("CSV and Excel export options will be added here.")
    with status_col:
        st.subheader("Selection Summary")
        st.write("Selected rows and active filters will appear here.")

    with st.expander("Data Dictionary"):
        st.write(
            "Field definitions, source details, and refresh timestamps will be "
            "documented here."
        )
