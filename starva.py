

import streamlit as st
import pandas as pd
import plotly.express as px

# ---------------------------------------------------
# PAGE CONFIGURATION
# ---------------------------------------------------

st.set_page_config(
    page_title="Bellabeat Fitness Analytics",
    page_icon="🐻",
    layout="wide"
)

# ---------------------------------------------------
# TITLE
# ---------------------------------------------------

st.title("🐻 Bellabeat Fitness Analytics Dashboard")
st.subheader("Smart Device Fitness & Wellness Data Analysis")

st.write(
    "Analyze user activity, steps, calories, sleep, and fitness behavior "
    "to identify useful insights for Bellabeat's marketing strategy."
)

# ---------------------------------------------------
# LOAD DATA
# ---------------------------------------------------

@st.cache_data
def load_data():

    df = pd.read_excel(
        "../data/4f82c2c2-06a5-42de-a60a-1473dd0da3b0.xlsx"
    )

    # Remove unwanted unnamed columns
    df = df.loc[:, ~df.columns.astype(str).str.contains("^Unnamed")]

    # Convert date
    if "ActivityDate" in df.columns:
        df["ActivityDate"] = pd.to_datetime(
            df["ActivityDate"],
            errors="coerce"
        )

    return df


df = load_data()

# ---------------------------------------------------
# DATA INFORMATION
# ---------------------------------------------------

st.success("Data loaded successfully!")

# ---------------------------------------------------
# SIDEBAR FILTERS
# ---------------------------------------------------

st.sidebar.header("🔎 Filters")

# User filter
if "Id" in df.columns:

    users = sorted(df["Id"].dropna().unique())

    selected_users = st.sidebar.multiselect(
        "Select Users",
        users,
        default=[]
    )

    if selected_users:
        filtered_df = df[df["Id"].isin(selected_users)]
    else:
        filtered_df = df.copy()

else:
    filtered_df = df.copy()


# Date filter
if "ActivityDate" in filtered_df.columns:

    min_date = filtered_df["ActivityDate"].min()
    max_date = filtered_df["ActivityDate"].max()

    date_range = st.sidebar.date_input(
        "Select Date Range",
        value=(min_date.date(), max_date.date())
    )

    if len(date_range) == 2:

        start_date = pd.to_datetime(date_range[0])
        end_date = pd.to_datetime(date_range[1])

        filtered_df = filtered_df[
            (filtered_df["ActivityDate"] >= start_date)
            & (filtered_df["ActivityDate"] <= end_date)
        ]


# ---------------------------------------------------
# KPI CALCULATIONS
# ---------------------------------------------------

if "Id" in filtered_df.columns:
    total_users = filtered_df["Id"].nunique()
else:
    total_users = 0


if "TotalSteps" in filtered_df.columns:
    avg_steps = filtered_df["TotalSteps"].mean()
else:
    avg_steps = 0


if "Calories" in filtered_df.columns:
    avg_calories = filtered_df["Calories"].mean()
else:
    avg_calories = 0


if "VeryActiveMinutes" in filtered_df.columns:
    avg_active = filtered_df["VeryActiveMinutes"].mean()
else:
    avg_active = 0


# ---------------------------------------------------
# KPI CARDS
# ---------------------------------------------------

st.markdown("## 📊 Key Performance Indicators")

col1, col2, col3, col4 = st.columns(4)

with col1:
    st.metric(
        "👥 Total Users",
        f"{total_users:,}"
    )

with col2:
    st.metric(
        "👣 Average Steps",
        f"{avg_steps:,.0f}"
    )

with col3:
    st.metric(
        "🔥 Average Calories",
        f"{avg_calories:,.0f}"
    )

with col4:
    st.metric(
        "🏃 Avg Very Active Minutes",
        f"{avg_active:,.0f}"
    )


st.divider()


# ---------------------------------------------------
# DAILY STEPS TREND
# ---------------------------------------------------

st.markdown("## 👣 Daily Steps Trend")

if "ActivityDate" in filtered_df.columns and "TotalSteps" in filtered_df.columns:

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
        title="Average Daily Steps"
    )

    fig_steps.update_layout(
        xaxis_title="Date",
        yaxis_title="Average Steps"
    )

    st.plotly_chart(
        fig_steps,
        use_container_width=True
    )


# ---------------------------------------------------
# ACTIVITY INTENSITY
# ---------------------------------------------------

st.markdown("## 🏃 Activity Intensity")

activity_columns = [
    "VeryActiveMinutes",
    "FairlyActiveMinutes",
    "LightlyActiveMinutes",
    "SedentaryMinutes"
]

available_columns = [
    col for col in activity_columns
    if col in filtered_df.columns
]

if available_columns:

    activity_avg = (
        filtered_df[available_columns]
        .mean()
        .reset_index()
    )

    activity_avg.columns = [
        "Activity Type",
        "Average Minutes"
    ]

    fig_activity = px.bar(
        activity_avg,
        x="Activity Type",
        y="Average Minutes",
        title="Average Minutes by Activity Type",
        text_auto=".0f"
    )

    st.plotly_chart(
        fig_activity,
        use_container_width=True
    )


# ---------------------------------------------------
# CALORIES VS STEPS
# ---------------------------------------------------

st.markdown("## 🔥 Calories vs Steps")

if "TotalSteps" in filtered_df.columns and "Calories" in filtered_df.columns:

    fig_calories = px.scatter(
        filtered_df,
        x="TotalSteps",
        y="Calories",
        title="Relationship Between Steps and Calories",
        hover_data=["Id"] if "Id" in filtered_df.columns else None
    )

    st.plotly_chart(
        fig_calories,
        use_container_width=True
    )


# ---------------------------------------------------
# SEDENTARY VS ACTIVE
# ---------------------------------------------------

st.markdown("## 🪑 Sedentary vs Active Time")

if (
    "SedentaryMinutes" in filtered_df.columns
    and "VeryActiveMinutes" in filtered_df.columns
):

    comparison = pd.DataFrame({
        "Category": [
            "Very Active",
            "Sedentary"
        ],
        "Minutes": [
            filtered_df["VeryActiveMinutes"].mean(),
            filtered_df["SedentaryMinutes"].mean()
        ]
    })

    fig_comparison = px.bar(
        comparison,
        x="Category",
        y="Minutes",
        title="Average Active vs Sedentary Minutes",
        text_auto=".0f"
    )

    st.plotly_chart(
        fig_comparison,
        use_container_width=True
    )


# ---------------------------------------------------
# DATA TABLE
# ---------------------------------------------------

st.markdown("## 📋 Data Preview")

st.dataframe(
    filtered_df.head(100),
    use_container_width=True
)


# ---------------------------------------------------
# BUSINESS INSIGHTS
# ---------------------------------------------------

st.markdown("## 💡 Business Insights")

if len(filtered_df) > 0:

    st.write(
        f"• The dashboard currently contains data for "
        f"**{total_users:,} unique users**."
    )

    st.write(
        f"• Average daily steps are approximately "
        f"**{avg_steps:,.0f} steps**."
    )

    st.write(
        f"• Average daily calorie expenditure is approximately "
        f"**{avg_calories:,.0f} calories**."
    )

    st.write(
        f"• Users record approximately "
        f"**{avg_active:,.0f} very active minutes** on average."
    )


# ---------------------------------------------------
# CONCLUSION
# ---------------------------------------------------

st.markdown("## 🎯 Conclusion")

st.write(
    "Fitness-device usage data can help identify patterns in physical "
    "activity, sedentary behavior, calorie expenditure, and user engagement. "
    "These insights can support Bellabeat's marketing analytics and "
    "wellness-product strategy."
)

# ---------------------------------------------------
# FOOTER
# ---------------------------------------------------

st.divider()

st.caption(
    "Bellabeat Fitness Analytics Project | Python + Streamlit + SQL"
)
```
