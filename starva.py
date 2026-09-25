import streamlit as st
import pandas as pd
import plotly.express as px


# =========================================================
# PAGE CONFIGURATION
# =========================================================

st.set_page_config(
    page_title="Bellabeat Fitness Analytics",
    page_icon="🐻",
    layout="wide"
)


# =========================================================
# TITLE
# =========================================================

st.title("🐻 Bellabeat Fitness Analytics Dashboard")

st.subheader(
    "Smart Device Fitness & Wellness Data Analysis"
)

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

    file_path = "../data/4f82c2c2-06a5-42de-a60a-1473dd0da3b0.xlsx"

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


try:

    df = load_data()

    st.success("✅ Data loaded successfully!")

except Exception as e:

    st.error("❌ Unable to load the Excel file.")

    st.write("Error:", e)

    st.stop()


# =========================================================
# SIDEBAR
# =========================================================

st.sidebar.title("🔎 Filters")


# =========================================================
# USER FILTER
# =========================================================

filtered_df = df.copy()

if "Id" in df.columns:

    user_list = sorted(
        df["Id"].dropna().unique()
    )

    selected_users = st.sidebar.multiselect(
        "Select User",
        options=user_list
    )

    if selected_users:

        filtered_df = filtered_df[
            filtered_df["Id"].isin(selected_users)
        ]


# =========================================================
# DATE FILTER
# =========================================================

if "ActivityDate" in filtered_df.columns:

    min_date = filtered_df["ActivityDate"].min()
    max_date = filtered_df["ActivityDate"].max()

    if pd.notna(min_date) and pd.notna(max_date):

        date_range = st.sidebar.date_input(
            "Select Date Range",
            value=(
                min_date.date(),
                max_date.date()
            )
        )

        if len(date_range) == 2:

            start_date = pd.to_datetime(
                date_range[0]
            )

            end_date = pd.to_datetime(
                date_range[1]
            )

            filtered_df = filtered_df[
                (filtered_df["ActivityDate"] >= start_date)
                &
                (filtered_df["ActivityDate"] <= end_date)
            ]


# =========================================================
# KPIs
# =========================================================

st.header("📊 Key Performance Indicators")


if "Id" in filtered_df.columns:

    total_users = filtered_df["Id"].nunique()

else:

    total_users = 0


if "TotalSteps" in filtered_df.columns:

    average_steps = filtered_df[
        "TotalSteps"
    ].mean()

else:

    average_steps = 0


if "Calories" in filtered_df.columns:

    average_calories = filtered_df[
        "Calories"
    ].mean()

else:

    average_calories = 0


if "VeryActiveMinutes" in filtered_df.columns:

    average_active_minutes = filtered_df[
        "VeryActiveMinutes"
    ].mean()

else:

    average_active_minutes = 0


col1, col2, col3, col4 = st.columns(4)


with col1:

    st.metric(
        "👥 Total Users",
        f"{total_users:,}"
    )


with col2:

    st.metric(
        "👣 Average Steps",
        f"{average_steps:,.0f}"
    )


with col3:

    st.metric(
        "🔥 Average Calories",
        f"{average_calories:,.0f}"
    )


with col4:

    st.metric(
        "🏃 Active Minutes",
        f"{average_active_minutes:,.0f}"
    )


st.divider()


# =========================================================
# DAILY STEPS TREND
# =========================================================

st.header("👣 Daily Steps Trend")


if (
    "ActivityDate" in filtered_df.columns
    and "TotalSteps" in filtered_df.columns
):

    steps_data = (
        filtered_df
        .groupby("ActivityDate", as_index=False)
        ["TotalSteps"]
        .mean()
    )

    fig_steps = px.line(
        steps_data,
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


# =========================================================
# ACTIVITY INTENSITY
# =========================================================

st.header("🏃 Activity Intensity")


activity_columns = [
    "VeryActiveMinutes",
    "FairlyActiveMinutes",
    "LightlyActiveMinutes",
    "SedentaryMinutes"
]


available_activity_columns = [
    column
    for column in activity_columns
    if column in filtered_df.columns
]


if available_activity_columns:

    activity_data = (
        filtered_df[
            available_activity_columns
        ]
        .mean()
        .reset_index()
    )

    activity_data.columns = [
        "Activity Type",
        "Average Minutes"
    ]

    fig_activity = px.bar(
        activity_data,
        x="Activity Type",
        y="Average Minutes",
        text_auto=".0f",
        title="Average Minutes by Activity Type"
    )

    fig_activity.update_layout(
        xaxis_title="Activity Type",
        yaxis_title="Average Minutes"
    )

    st.plotly_chart(
        fig_activity,
        use_container_width=True
    )


# =========================================================
# CALORIES VS STEPS
# =========================================================

st.header("🔥 Calories vs Steps")


if (
    "TotalSteps" in filtered_df.columns
    and "Calories" in filtered_df.columns
):

    fig_calories = px.scatter(
        filtered_df,
        x="TotalSteps",
        y="Calories",
        title="Relationship Between Steps and Calories",
        opacity=0.7
    )

    fig_calories.update_layout(
        xaxis_title="Total Steps",
        yaxis_title="Calories Burned"
    )

    st.plotly_chart(
        fig_calories,
        use_container_width=True
    )


# =========================================================
# ACTIVE VS SEDENTARY
# =========================================================

st.header("🪑 Active vs Sedentary Behavior")


if (
    "VeryActiveMinutes" in filtered_df.columns
    and "SedentaryMinutes" in filtered_df.columns
):

    comparison_data = pd.DataFrame({

        "Category": [
            "Very Active",
            "Sedentary"
        ],

        "Average Minutes": [
            filtered_df[
                "VeryActiveMinutes"
            ].mean(),

            filtered_df[
                "SedentaryMinutes"
            ].mean()
        ]
    })


    fig_comparison = px.bar(
        comparison_data,
        x="Category",
        y="Average Minutes",
        text_auto=".0f",
        title="Average Active vs Sedentary Minutes"
    )

    fig_comparison.update_layout(
        xaxis_title="Behavior",
        yaxis_title="Average Minutes"
    )

    st.plotly_chart(
        fig_comparison,
        use_container_width=True
    )


# =========================================================
# CALORIES TREND
# =========================================================

st.header("🔥 Daily Calories Trend")


if (
    "ActivityDate" in filtered_df.columns
    and "Calories" in filtered_df.columns
):

    calorie_data = (
        filtered_df
        .groupby("ActivityDate", as_index=False)
        ["Calories"]
        .mean()
    )

    fig_calories_trend = px.line(
        calorie_data,
        x="ActivityDate",
        y="Calories",
        markers=True,
        title="Average Daily Calories"
    )

    fig_calories_trend.update_layout(
        xaxis_title="Date",
        yaxis_title="Calories"
    )

    st.plotly_chart(
        fig_calories_trend,
        use_container_width=True
    )


# =========================================================
# DATA SUMMARY
# =========================================================

st.header("📋 Data Summary")

col1, col2 = st.columns(2)


with col1:

    st.write(
        "**Number of Records:**",
        len(filtered_df)
    )


with col2:

    st.write(
        "**Number of Columns:**",
        len(filtered_df.columns)
    )


# =========================================================
# DATA PREVIEW
# =========================================================

st.header("📄 Data Preview")

st.dataframe(
    filtered_df.head(100),
    use_container_width=True
)


# =========================================================
# BUSINESS INSIGHTS
# =========================================================

st.header("💡 Business Insights")


if len(filtered_df) > 0:

    st.write(
        f"• The selected data contains "
        f"**{total_users:,} unique users**."
    )

    st.write(
        f"• Average daily steps are approximately "
        f"**{average_steps:,.0f} steps**."
    )

    st.write(
        f"• Average daily calorie expenditure is "
        f"approximately **{average_calories:,.0f} calories**."
    )

    st.write(
        f"• Average very active time is "
        f"approximately **{average_active_minutes:,.0f} minutes**."
    )

    if "SedentaryMinutes" in filtered_df.columns:

        average_sedentary = (
            filtered_df[
                "SedentaryMinutes"
            ].mean()
        )

        st.write(
            f"• Average sedentary time is "
            f"approximately **{average_sedentary:,.0f} minutes**."
        )


# =========================================================
# MARKETING RECOMMENDATIONS
# =========================================================

st.header("🎯 Marketing Recommendations")

st.write(
    "1. Encourage users to increase daily physical activity "
    "through personalized activity goals."
)

st.write(
    "2. Use reminders and engagement campaigns to reduce "
    "long periods of sedentary behavior."
)

st.write(
    "3. Promote fitness tracking features that help users "
    "monitor steps, calories, and activity intensity."
)

st.write(
    "4. Use personalized wellness insights to increase "
    "long-term engagement with Bellabeat products."
)


# =========================================================
# CONCLUSION
# =========================================================

st.header("🏁 Conclusion")

st.write(
    "Smart-device fitness data provides useful information "
    "about physical activity, calorie expenditure, and "
    "sedentary behavior. These patterns can support "
    "Bellabeat's marketing analytics and wellness strategy."
)


# =========================================================
# FOOTER
# =========================================================

st.divider()

st.caption(
    "Bellabeat Fitness Analytics | "
    "Python • Pandas • Plotly • Streamlit"
)

