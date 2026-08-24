import streamlit as st
import pandas as pd

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
            if uploaded_file.name.lower().endswith(".csv"):
                df = pd.read_csv(uploaded_file)
            elif uploaded_file.name.lower().endswith(".json"):
                df = pd.read_json(uploaded_file)
            else:
                st.error("Unsupported file type.")
                st.stop()
        except (ValueError, TypeError, pd.errors.ParserError, OSError):
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

        date_columns = [
            column
            for column in df.columns
            if column.lower() in {"date", "datetime", "timestamp"}
        ]
        segment_columns = [
            column for column in df.columns if column.lower() == "segment"
        ]
        revenue_columns = [
            column for column in df.columns if column.lower() == "revenue"
        ]
        date_column = date_columns[0] if date_columns else None
        segment_column = segment_columns[0] if segment_columns else None
        revenue_column = revenue_columns[0] if revenue_columns else None

        st.sidebar.header("Filters")
        if st.sidebar.button("Reset Filters", key="reset_filters"):
            for filter_key in [
                "filter_date_range",
                "filter_segments",
                "filter_revenue_range",
            ]:
                st.session_state.pop(filter_key, None)
            st.rerun()

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
        numeric_cols = filtered_df.select_dtypes(include="number").columns.tolist()
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
