import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
from pathlib import Path


# =========================================================
# PAGE CONFIGURATION
# =========================================================

st.set_page_config(
    page_title="Starva Fitness Analytics",
    page_icon="🐻",
    layout="wide"
)


# =========================================================
# TITLE
# =========================================================

st.title("🐻 Starva Fitness Analytics Dashboard")

st.subheader("Smart Device Fitness & Wellness Data Analysis")

st.write(
    "Analyze user activity, steps, calories, intensity, "
    "and sedentary behavior to identify useful business insights."
)

st.divider()


# =========================================================
# LOAD DATA
# =========================================================

@st.cache_data
def load_data():

    # Folder containing starva.py
    project_folder = Path(__file__).parent

    # Actual Excel file
    file_path = project_folder / "dailyActivity_merged.csv.xlsx"

    # Check file
    if not file_path.exists():
        st.error("❌ Excel file not found.")

        st.write("Expected file:")
        st.code(str(file_path))

        st.write("Files available in the project folder:")

        for file in project_folder.iterdir():
            st.write(file.name)

        st.stop()

    # Read Excel
    df = pd.read_excel(file_path)

    # Remove unnamed columns
    df = df.loc[
        :,
        ~df.columns.astype(str).str.contains("^Unnamed")
    ]

    # Convert date
    if "ActivityDate" in df.columns:
        df["ActivityDate"] = pd.to_datetime(
            df["ActivityDate"],
            errors="coerce"
        )

    return df


# Load data
df = load_data()


# =========================================================
# DATA INFORMATION
# =========================================================

st.success("✅ Activity data loaded successfully!")

with st.expander("📋 View Dataset Information"):

    col1, col2 = st.columns(2)

    with col1:
        st.write("**Rows:**", df.shape[0])
        st.write("**Columns:**", df.shape[1])

    with col2:
        st.write("**Users:**", df["Id"].nunique()
                 if "Id" in df.columns else "N/A")

    st.dataframe(
        df.head(10),
        use_container_width=True
    )


# =========================================================
# SIDEBAR FILTERS
# =========================================================

st.sidebar.header("🔎 Filters")


# User filter
if "Id" in df.columns:

    users = sorted(df["Id"].dropna().unique())

    selected_users = st.sidebar.multiselect(
        "Select User",
        users,
        default=[]
    )

    if selected_users:
        filtered_df = df[
            df["Id"].isin(selected_users)
        ].copy()
    else:
        filtered_df = df.copy()

else:

    filtered_df = df.copy()


# Date filter
if "ActivityDate" in filtered_df.columns:

    min_date = filtered_df["ActivityDate"].min()
    max_date = filtered_df["ActivityDate"].max()

    if pd.notna(min_date) and pd.notna(max_date):

        date_range = st.sidebar.date_input(
            "Select Date Range",
            value=(min_date.date(), max_date.date()),
            min_value=min_date.date(),
            max_value=max_date.date()
        )

        if len(date_range) == 2:

            start_date = pd.to_datetime(date_range[0])
            end_date = pd.to_datetime(date_range[1])

            filtered_df = filtered_df[
                (filtered_df["ActivityDate"] >= start_date)
                &
                (filtered_df["ActivityDate"] <= end_date)
            ]


# =========================================================
# KPI CALCULATIONS
# =========================================================

total_users = (
    filtered_df["Id"].nunique()
    if "Id" in filtered_df.columns
    else 0
)

avg_steps = (
    filtered_df["TotalSteps"].mean()
    if "TotalSteps" in filtered_df.columns
    else 0
)

avg_calories = (
    filtered_df["Calories"].mean()
    if "Calories" in filtered_df.columns
    else 0
)

avg_sedentary = (
    filtered_df["SedentaryMinutes"].mean()
    if "SedentaryMinutes" in filtered_df.columns
    else 0
)

avg_active = 0

active_columns = [
    "VeryActiveMinutes",
    "FairlyActiveMinutes",
    "LightlyActiveMinutes"
]

available_active_columns = [
    col for col in active_columns
    if col in filtered_df.columns
]

if available_active_columns:

    avg_active = filtered_df[
        available_active_columns
    ].sum(axis=1).mean()


# =========================================================
# KPI CARDS
# =========================================================

st.subheader("📊 Key Performance Indicators")

col1, col2, col3, col4, col5 = st.columns(5)

with col1:
    st.metric(
        "👥 Total Users",
        f"{total_users:,}"
    )

with col2:
    st.metric(
        "👣 Avg Steps",
        f"{avg_steps:,.0f}"
    )

with col3:
    st.metric(
        "🔥 Avg Calories",
        f"{avg_calories:,.0f}"
    )

with col4:
    st.metric(
        "🏃 Avg Active Minutes",
        f"{avg_active:,.0f}"
    )

with col5:
    st.metric(
        "🪑 Avg Sedentary Minutes",
        f"{avg_sedentary:,.0f}"
    )


st.divider()


# =========================================================
# DAILY STEPS TREND
# =========================================================

if (
    "ActivityDate" in filtered_df.columns
    and "TotalSteps" in filtered_df.columns
):

    daily_steps = (
        filtered_df
        .groupby("ActivityDate", as_index=False)["TotalSteps"]
        .mean()
    )

    fig_steps = px.line(
        daily_steps,
        x="ActivityDate",
        y="TotalSteps",
        markers=True,
        title="📈 Average Daily Steps Trend"
    )

    fig_steps.update_layout(
        xaxis_title="Date",
        yaxis_title="Average Steps"
    )

    st.plotly_chart(
        fig_steps,
        use_container_width=True
    )


# =========================================================
# STEPS VS CALORIES
# =========================================================

if (
    "TotalSteps" in filtered_df.columns
    and "Calories" in filtered_df.columns
):

    fig_scatter = px.scatter(
        filtered_df,
        x="TotalSteps",
        y="Calories",
        title="👣 Steps vs Calories Burned",
        opacity=0.7
    )

    fig_scatter.update_layout(
        xaxis_title="Total Steps",
        yaxis_title="Calories Burned"
    )

    st.plotly_chart(
        fig_scatter,
        use_container_width=True
    )


# =========================================================
# ACTIVITY INTENSITY
# =========================================================

intensity_columns = [
    "VeryActiveMinutes",
    "FairlyActiveMinutes",
    "LightlyActiveMinutes",
    "SedentaryMinutes"
]

available_intensity = [
    col for col in intensity_columns
    if col in filtered_df.columns
]

if available_intensity:

    intensity_data = pd.DataFrame({
        "Activity Type": available_intensity,
        "Average Minutes": [
            filtered_df[col].mean()
            for col in available_intensity
        ]
    })

    fig_intensity = px.bar(
        intensity_data,
        x="Activity Type",
        y="Average Minutes",
        title="🏃 Average Activity Intensity"
    )

    fig_intensity.update_layout(
        xaxis_title="Activity Type",
        yaxis_title="Average Minutes"
    )

    st.plotly_chart(
        fig_intensity,
        use_container_width=True
    )


# =========================================================
# CALORIES DISTRIBUTION
# =========================================================

if "Calories" in filtered_df.columns:

    fig_calories = px.histogram(
        filtered_df,
        x="Calories",
        nbins=30,
        title="🔥 Calories Burned Distribution"
    )

    fig_calories.update_layout(
        xaxis_title="Calories",
        yaxis_title="Number of Records"
    )

    st.plotly_chart(
        fig_calories,
        use_container_width=True
    )


# =========================================================
# DISTANCE ANALYSIS
# =========================================================

distance_columns = [
    "TotalDistance",
    "TrackerDistance",
    "LoggedActivitiesDistance"
]

available_distance = [
    col for col in distance_columns
    if col in filtered_df.columns
]

if available_distance:

    distance_column = available_distance[0]

    fig_distance = px.histogram(
        filtered_df,
        x=distance_column,
        nbins=30,
        title=f"📍 {distance_column} Distribution"
    )

    st.plotly_chart(
        fig_distance,
        use_container_width=True
    )


# =========================================================
# SEDENTARY VS ACTIVE
# =========================================================

if (
    "SedentaryMinutes" in filtered_df.columns
    and available_active_columns
):

    sedentary_avg = filtered_df[
        "SedentaryMinutes"
    ].mean()

    active_avg = filtered_df[
        available_active_columns
    ].sum(axis=1).mean()

    behavior_data = pd.DataFrame({
        "Behavior": [
            "Active Minutes",
            "Sedentary Minutes"
        ],
        "Average Minutes": [
            active_avg,
            sedentary_avg
        ]
    })

    fig_behavior = px.bar(
        behavior_data,
        x="Behavior",
        y="Average Minutes",
        title="⚖️ Active vs Sedentary Behavior"
    )

    st.plotly_chart(
        fig_behavior,
        use_container_width=True
    )


# =========================================================
# BUSINESS INSIGHTS
# =========================================================

st.divider()

st.subheader("💡 Business Insights")

st.markdown(
    """
### Key Areas Identified

- 👣 **Daily Steps:** Monitor changes in users' daily movement.
- 🔥 **Calories:** Compare calorie expenditure with activity levels.
- 🏃 **Activity Intensity:** Understand very active, fairly active,
  and lightly active behavior.
- 🪑 **Sedentary Behavior:** Identify how much time users spend inactive.
- 📈 **Trends:** Track daily activity patterns over time.
"""
)


# =========================================================
# DATA TABLE
# =========================================================

st.divider()

st.subheader("📋 Filtered Activity Data")

st.dataframe(
    filtered_df,
    use_container_width=True
)


# =========================================================
# FOOTER
# =========================================================

st.divider()

st.caption(
    "Starva Fitness Analytics | Python • Pandas • Plotly • Streamlit"
)