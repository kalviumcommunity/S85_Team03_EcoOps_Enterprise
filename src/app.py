import streamlit as st
import pandas as pd
from datetime import date

# --------------------------------------------------
# STREAMLIT SESSION STATE INITIALISATION
# --------------------------------------------------

# "selected_segment" stores the user's confirmed segment choice
# so it survives Streamlit reruns caused by other widget interactions.
if "selected_segment" not in st.session_state:
    st.session_state["selected_segment"] = "All"

# "workflow_step" tracks the user's progress through the workflow.
# Step 2 is shown only after Step 1 has been completed.
if "workflow_step" not in st.session_state:
    st.session_state["workflow_step"] = 1

# "analysis_result" stores the computed revenue from Step 2
# so the result persists across unrelated widget interactions.
if "analysis_result" not in st.session_state:
    st.session_state["analysis_result"] = None

# "filter_date_start" stores the selected start date
# and demonstrates that changing another widget does not reset the workflow.
if "filter_date_start" not in st.session_state:
    st.session_state["filter_date_start"] = date(2026, 1, 1)


# --------------------------------------------------
# SAMPLE DATA
# --------------------------------------------------

df = pd.DataFrame(
    {
        "segment": [
            "Enterprise",
            "Enterprise",
            "Mid-Market",
            "Mid-Market",
            "SMB",
            "SMB",
        ],
        "revenue": [50000, 75000, 30000, 45000, 10000, 15000],
    }
)


# --------------------------------------------------
# PAGE CONFIGURATION
# --------------------------------------------------

st.set_page_config(
    page_title="Session State Workflow",
    page_icon="📊",
)

st.title("📊 Streamlit Session State & Workflow Persistence")

st.write(
    "This app demonstrates how `st.session_state` preserves "
    "workflow progress and user selections across Streamlit reruns."
)


# --------------------------------------------------
# RESET WORKFLOW
# --------------------------------------------------

if st.sidebar.button("🔄 Reset Workflow"):
    # Clear only workflow-related session state.
    # Unrelated session state can remain untouched.
    for key in [
        "selected_segment",
        "workflow_step",
        "analysis_result",
        "filter_date_start",
    ]:
        if key in st.session_state:
            del st.session_state[key]

    st.rerun()


# --------------------------------------------------
# ANOTHER WIDGET - DATE FILTER
# --------------------------------------------------

st.sidebar.header("Filters")

selected_date = st.sidebar.date_input(
    "Select analysis date",
    value=st.session_state["filter_date_start"],
)

# Save the date selection so it also persists across reruns.
st.session_state["filter_date_start"] = selected_date

st.sidebar.info(
    f"Selected date: {st.session_state['filter_date_start']}"
)


# --------------------------------------------------
# STEP 1 - SELECT SEGMENT
# --------------------------------------------------

st.header("Step 1: Select Customer Segment")

segments = ["All", "Enterprise", "Mid-Market", "SMB"]

segment = st.selectbox(
    "Choose a segment",
    options=segments,
    index=segments.index(st.session_state["selected_segment"]),
)

if st.button("Confirm Segment"):
    # Save the user's choice in session state.
    st.session_state["selected_segment"] = segment

    # Move the workflow forward to Step 2.
    st.session_state["workflow_step"] = 2

    st.success(f"Segment confirmed: {segment}")


# --------------------------------------------------
# STEP 2 - ANALYSIS
# --------------------------------------------------

if st.session_state["workflow_step"] >= 2:

    st.header("Step 2: Segment Analysis")

    # Read the value selected and confirmed in Step 1.
    chosen = st.session_state["selected_segment"]

    st.write(f"### Analysing: {chosen}")

    # Filter the data using the persisted segment selection.
    if chosen == "All":
        analysis_df = df
    else:
        analysis_df = df[df["segment"] == chosen]

    # Compute the revenue for the selected segment.
    result = analysis_df["revenue"].sum()

    # Store the intermediate/computed result in session state.
    st.session_state["analysis_result"] = result

    # Display the persisted analysis result.
    st.metric(
        "Total Revenue",
        f"${st.session_state['analysis_result']:,.0f}",
    )

    st.subheader("Filtered Data")
    st.dataframe(analysis_df, use_container_width=True)

    st.success(
        "Try changing the date filter in the sidebar. "
        "The confirmed segment and workflow progress will remain."
    )


# --------------------------------------------------
# SESSION STATE DEBUG / DEMONSTRATION
# --------------------------------------------------

st.divider()

st.subheader("Current Session State")

st.write(
    {
        "selected_segment": st.session_state["selected_segment"],
        "workflow_step": st.session_state["workflow_step"],
        "analysis_result": st.session_state["analysis_result"],
        "filter_date_start": str(st.session_state["filter_date_start"]),
    }
)