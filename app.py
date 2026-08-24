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

        st.header("Dataset Preview")
        row_count, column_count, null_count = st.columns(3)
        with row_count:
            st.metric("Rows", f"{len(df):,}")
        with column_count:
            st.metric("Columns", f"{len(df.columns):,}")
        with null_count:
            total_cells = df.shape[0] * df.shape[1]
            null_pct = df.isnull().sum().sum() / total_cells * 100
            st.metric("Null %", f"{null_pct:.1f}%")

        st.subheader("First 10 Rows")
        st.dataframe(df.head(10), use_container_width=True)

        st.subheader("Column Summary")
        summary = pd.DataFrame(
            {
                "Column": df.columns,
                "Type": df.dtypes.astype(str).values,
                "Non-Null": df.notnull().sum().values,
                "Null Count": df.isnull().sum().values,
                "Null %": (df.isnull().sum() / len(df) * 100).round(1).values,
            }
        )
        st.dataframe(summary, use_container_width=True)

        st.subheader("Descriptive Statistics")
        numeric_cols = df.select_dtypes(include="number").columns.tolist()
        if numeric_cols:
            st.dataframe(df[numeric_cols].describe(), use_container_width=True)
        else:
            st.info("No numeric columns are available for descriptive statistics.")

        st.subheader("Quick Exploration")
        if numeric_cols:
            selected_col = st.selectbox(
                "Select a column to visualise",
                numeric_cols,
            )
            st.bar_chart(df[selected_col].value_counts().head(20))
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
