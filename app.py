import streamlit as st

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

    st.header("Explore Marketplace Data")
    filter_col, table_col = st.columns(2)
    with filter_col:
        st.subheader("Filter Controls")
        st.write("Filter controls will be added here.")
    with table_col:
        st.subheader("Result Preview")
        st.write("Data table placeholder")

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
