# =====================================================
# APP.PY - PART 1
# Imports + Config + Sidebar + Uploads
# =====================================================

import streamlit as st
import pandas as pd
import numpy as np
from datetime import datetime
import io
import os

# =====================================================
# MODULE IMPORTS
# =====================================================

from modules.teams import *
from modules.sequencing import *
from modules.production import *
from modules.printing import *
from modules.dispatch import *
from modules.procurement import *
from modules.inventory import *
from modules.reforecast import *
from modules.dashboard import *
from modules.exports import *

# =====================================================
# PAGE CONFIG
# =====================================================

st.set_page_config(
    page_title="Digital Wall Painting Supply Chain Planner",
    page_icon="📦",
    layout="wide"
)

# =====================================================
# LOGO
# =====================================================

LOGO_PATH = "assets/logo.png"

col1, col2 = st.columns([1, 5])

with col1:
    if os.path.exists(LOGO_PATH):
        st.image(LOGO_PATH, width=120)

with col2:
    st.title("Digital Wall Painting Supply Chain Planner")
    st.caption(
        "Production • Printing • Dispatch • Procurement • Inventory Planning"
    )

st.divider()

# =====================================================
# SESSION STATE
# =====================================================

if "project_loaded" not in st.session_state:
    st.session_state.project_loaded = False

if "team_plan_df" not in st.session_state:
    st.session_state.team_plan_df = None

# =====================================================
# SIDEBAR
# =====================================================

st.sidebar.header("Project Settings")

# =====================================================
# PROJECT MODE
# =====================================================

project_mode = st.sidebar.radio(
    "Project Mode",
    [
        "New Campaign",
        "Running Campaign"
    ]
)

# =====================================================
# PRODUCTIVITY SETTINGS
# =====================================================

st.sidebar.subheader("Team Productivity")

daily_productivity = st.sidebar.number_input(
    "Expected Sq Ft / Team / Day",
    min_value=1,
    value=500
)

achievement_factor = st.sidebar.slider(
    "Average Achievement %",
    min_value=50,
    max_value=100,
    value=85
)

travel_loss_days = st.sidebar.number_input(
    "Travel Days Lost Per Month",
    min_value=0,
    max_value=15,
    value=5
)

# =====================================================
# PRINTING SETTINGS
# =====================================================

st.sidebar.subheader("Printing Settings")

daily_print_capacity = st.sidebar.number_input(
    "Daily Print Capacity (Sq Ft)",
    min_value=1000,
    value=20000
)

printing_wastage = st.sidebar.slider(
    "Printing Wastage %",
    min_value=0,
    max_value=30,
    value=12
)

# =====================================================
# MEDIA SETTINGS
# =====================================================

st.sidebar.subheader("Media Roll Settings")

roll_size_sqft = st.sidebar.number_input(
    "Roll Size (Sq Ft)",
    min_value=100,
    value=1250
)

roll_lead_time = st.sidebar.number_input(
    "Roll Lead Time (Days)",
    min_value=1,
    value=3
)

# =====================================================
# GUM SETTINGS
# =====================================================

st.sidebar.subheader("Gum Settings")

gum_per_1000_sqft = st.sidebar.number_input(
    "Gum Required per 1000 Sq Ft (Kg)",
    min_value=1.0,
    value=5.0
)

gum_lead_time = st.sidebar.number_input(
    "Gum Lead Time (Days)",
    min_value=1,
    value=7
)

# =====================================================
# DISPATCH SETTINGS
# =====================================================

st.sidebar.subheader("Dispatch Settings")

dispatch_cycle_days = st.sidebar.number_input(
    "Dispatch Coverage Days",
    min_value=1,
    max_value=30,
    value=10
)

arrival_buffer_days = st.sidebar.number_input(
    "Arrival Buffer Days",
    min_value=0,
    max_value=10,
    value=2
)

# =====================================================
# INVENTORY SETTINGS
# =====================================================

st.sidebar.subheader("Inventory Settings")

opening_roll_stock = st.sidebar.number_input(
    "Opening Roll Inventory",
    min_value=0,
    value=100
)

opening_gum_stock = st.sidebar.number_input(
    "Opening Gum Inventory (Kg)",
    min_value=0,
    value=1000
)

safety_roll_stock = st.sidebar.number_input(
    "Safety Roll Stock",
    min_value=0,
    value=25
)

safety_gum_stock = st.sidebar.number_input(
    "Safety Gum Stock (Kg)",
    min_value=0,
    value=200
)

# =====================================================
# FILE UPLOAD SECTION
# =====================================================

st.header("Project Upload")

st.info(
    """
Upload the Team Planning File.

Required Columns:

- Team Name
- Team Start Date
- Sequence
- State
- District
- Wall Count
- Avg Wall Size
- Transit Days
- Travel Days
"""
)

uploaded_file = st.file_uploader(
    "Upload Team Planning Excel",
    type=["xlsx", "xls", "csv"]
)

# =====================================================
# LOAD DATA
# =====================================================

team_plan_df = None

if uploaded_file is not None:

    try:

        if uploaded_file.name.endswith(".csv"):

            team_plan_df = pd.read_csv(
                uploaded_file
            )

        else:

            team_plan_df = pd.read_excel(
                uploaded_file
            )

        st.success(
            f"{len(team_plan_df):,} rows loaded successfully"
        )

        st.dataframe(
            team_plan_df.head(),
            use_container_width=True
        )

        st.session_state.team_plan_df = team_plan_df
        st.session_state.project_loaded = True

    except Exception as e:

        st.error(
            f"Error loading file: {e}"
        )

# =====================================================
# RUNNING CAMPAIGN INPUTS
# =====================================================

if project_mode == "Running Campaign":

    st.header("Current Project Status")

    col1, col2, col3 = st.columns(3)

    with col1:

        completed_sqft = st.number_input(
            "Completed Sq Ft",
            min_value=0,
            value=0
        )

    with col2:

        media_in_field = st.number_input(
            "Media in Field (Sq Ft)",
            min_value=0,
            value=0
        )

    with col3:

        gum_in_field = st.number_input(
            "Gum in Field (Kg)",
            min_value=0,
            value=0
        )

# =====================================================
# TEMPLATE DOWNLOADS
# =====================================================

st.header("Templates")

template_df = pd.DataFrame({

    "Team Name": ["Team A"],

    "Team Start Date": ["01-Jul-2026"],

    "Sequence": [1],

    "State": ["Maharashtra"],

    "District": ["Pune"],

    "Wall Count": [50],

    "Avg Wall Size": [250],

    "Transit Days": [2],

    "Travel Days": [1]

})

template_buffer = io.BytesIO()

with pd.ExcelWriter(
    template_buffer,
    engine="openpyxl"
) as writer:

    template_df.to_excel(
        writer,
        index=False,
        sheet_name="Template"
    )

template_buffer.seek(0)

st.download_button(
    label="📥 Download Upload Template",
    data=template_buffer.getvalue(),
    file_name="Team_Planning_Template.xlsx",
    mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
)

# =====================================================
# END OF PART 1
# =====================================================

# =====================================================
# PART 2
# VALIDATION + SEQUENCING + TEAM PLANNING
# =====================================================

if st.session_state.project_loaded:

    team_plan_df = st.session_state.team_plan_df

    # =================================================
    # VALIDATE INPUT FILE
    # =================================================

    valid, missing_cols = validate_sequence_columns(
        team_plan_df
    )

    if not valid:

        st.error(
            f"Missing required columns: {', '.join(missing_cols)}"
        )

        st.stop()

    # =================================================
    # PREPARE DATA
    # =================================================

    try:

        prepared_df = prepare_sequence_plan(
            team_plan_df
        )

    except Exception as e:

        st.error(
            f"Preparation Error: {e}"
        )

        st.stop()

    # =================================================
    # CALCULATE REAL PRODUCTIVITY
    # =================================================

    # Achievement factor adjustment

    effective_productivity = (

        daily_productivity

        *

        (achievement_factor / 100)

    )

    # Travel loss adjustment

    working_days_per_month = max(
        30 - travel_loss_days,
        1
    )

    utilization_factor = (

        working_days_per_month / 30

    )

    real_productivity = (

        effective_productivity

        *

        utilization_factor

    )

    # =================================================
    # BUILD DISTRICT TIMELINE
    # =================================================

    district_timeline_df = build_district_timeline(
        prepared_df,
        real_productivity
    )

    # =================================================
    # TEAM SUMMARY
    # =================================================

    team_summary_df = build_team_completion_summary(
        district_timeline_df
    )

    # =================================================
    # DISTRICT COMPLETION
    # =================================================

    district_completion_df = (
        build_district_completion_calendar(
            district_timeline_df
        )
    )

    # =================================================
    # MOVEMENT PLAN
    # =================================================

    movement_df = build_team_movement_plan(
        district_timeline_df
    )

    # =================================================
    # WEEKLY TEAM LOADING
    # =================================================

    weekly_loading_df = (
        build_weekly_team_loading(
            district_timeline_df
        )
    )

    # =================================================
    # TIMELINE KPIs
    # =================================================

    timeline_kpis = build_timeline_kpis(
        district_timeline_df
    )

    # =================================================
    # SAVE TO SESSION
    # =================================================

    st.session_state.prepared_df = prepared_df

    st.session_state.district_timeline_df = (
        district_timeline_df
    )

    st.session_state.team_summary_df = (
        team_summary_df
    )

    st.session_state.movement_df = (
        movement_df
    )

    st.session_state.weekly_loading_df = (
        weekly_loading_df
    )

    st.session_state.timeline_kpis = (
        timeline_kpis
    )

    # =================================================
    # PROJECT KPIs
    # =================================================

    st.header("Project Overview")

    kpi1, kpi2, kpi3, kpi4 = st.columns(4)

    with kpi1:

        st.metric(
            "Total Teams",
            timeline_kpis["Total Teams"]
        )

    with kpi2:

        st.metric(
            "Total Districts",
            timeline_kpis["Total Districts"]
        )

    with kpi3:

        st.metric(
            "Total Sq Ft",
            f"{timeline_kpis['Total Sq Ft']:,.0f}"
        )

    with kpi4:

        st.metric(
            "Project Duration (Days)",
            timeline_kpis["Project Duration"]
        )

    kpi5, kpi6, kpi7, kpi8 = st.columns(4)

    with kpi5:

        st.metric(
            "Target Productivity",
            round(daily_productivity, 0)
        )

    with kpi6:

        st.metric(
            "Achievement %",
            achievement_factor
        )

    with kpi7:

        st.metric(
            "Travel Loss Days",
            travel_loss_days
        )

    with kpi8:

        st.metric(
            "Real Productivity",
            round(real_productivity, 1)
        )

    st.divider()

    # =================================================
    # TEAM PLANNING SECTION
    # =================================================

    planning_tab1, planning_tab2, planning_tab3, planning_tab4 = st.tabs(

        [

            "Team Summary",

            "District Timeline",

            "Team Movements",

            "Weekly Loading"

        ]

    )

    # =================================================
    # TEAM SUMMARY
    # =================================================

    with planning_tab1:

        st.subheader(
            "Team Completion Summary"
        )

        st.dataframe(
            team_summary_df,
            use_container_width=True
        )

        st.caption(
            f"Total Teams: {len(team_summary_df)}"
        )

    # =================================================
    # DISTRICT TIMELINE
    # =================================================

    with planning_tab2:

        st.subheader(
            "District Timeline"
        )

        st.dataframe(
            district_timeline_df,
            use_container_width=True
        )

        st.caption(
            f"Total District Records: {len(district_timeline_df)}"
        )

    # =================================================
    # MOVEMENTS
    # =================================================

    with planning_tab3:

        st.subheader(
            "Team Movement Plan"
        )

        if len(movement_df):

            st.dataframe(
                movement_df,
                use_container_width=True
            )

        else:

            st.info(
                "No team movement records found."
            )

    # =================================================
    # WEEKLY LOADING
    # =================================================

    with planning_tab4:

        st.subheader(
            "Weekly Active Team Loading"
        )

        st.dataframe(
            weekly_loading_df,
            use_container_width=True
        )

        st.caption(
            f"Project Weeks: {len(weekly_loading_df)}"
        )

    st.divider()

# =====================================================
# END OF PART 2
# =====================================================

# =====================================================
# PART 3
# PRODUCTION PLANNING ENGINE
# =====================================================

if st.session_state.project_loaded:

    st.header("Production Planning")

    # =================================================
    # LOAD DATA
    # =================================================

    district_timeline_df = (
        st.session_state.district_timeline_df
    )

    timeline_kpis = (
        st.session_state.timeline_kpis
    )

    total_project_sqft = (
        district_timeline_df[
            "District Sq Ft"
        ].sum()
    )

    # =================================================
    # PROJECT DATES
    # =================================================

    project_start = (
        district_timeline_df[
            "District Start"
        ].min()
    )

    project_end = (
        district_timeline_df[
            "District Finish"
        ].max()
    )

    # =================================================
    # BUILD DAILY PRODUCTION
    # =================================================

    production_rows = []

    date_range = pd.date_range(
        project_start,
        project_end,
        freq="D"
    )

    for current_date in date_range:

        active_records = district_timeline_df[

            (
                district_timeline_df[
                    "District Start"
                ] <= current_date
            )

            &

            (
                district_timeline_df[
                    "District Finish"
                ] >= current_date
            )

        ]

        active_teams = (
            active_records[
                "Team Name"
            ].nunique()
        )

        daily_sqft = (
            active_teams
            * real_productivity
        )

        production_rows.append({

            "Date":
                current_date,

            "Active Teams":
                active_teams,

            "Daily Production":
                round(daily_sqft, 2)

        })

    production_df = pd.DataFrame(
        production_rows
    )

    # =================================================
    # WEEKLY PRODUCTION
    # =================================================

    production_df["Week"] = (
        production_df["Date"]
        .dt.to_period("W")
        .astype(str)
    )

    weekly_production_df = (

        production_df

        .groupby(
            "Week",
            as_index=False
        )

        .agg({

            "Daily Production":
                "sum",

            "Active Teams":
                "max"

        })

    )

    weekly_production_df.rename(

        columns={

            "Daily Production":
                "Campaign Sq Ft"

        },

        inplace=True

    )

    # =================================================
    # MEDIA FORECAST
    # =================================================

    media_forecast_df = (
        weekly_production_df.copy()
    )

    media_forecast_df[
        "Media Requirement"
    ] = (

        media_forecast_df[
            "Campaign Sq Ft"
        ]

        *

        (
            1 +
            printing_wastage / 100
        )

    )

    # =================================================
    # GUM FORECAST
    # =================================================

    gum_forecast_df = (
        weekly_production_df.copy()
    )

    gum_forecast_df[
        "Gum Required (Kg)"
    ] = (

        gum_forecast_df[
            "Campaign Sq Ft"
        ]

        /

        1000

        *

        gum_per_1000_sqft

    )

    # =================================================
    # CUMULATIVE FORECAST
    # =================================================

    campaign_forecast_df = (
        weekly_production_df.copy()
    )

    campaign_forecast_df[
        "Cumulative Sq Ft"
    ] = (

        campaign_forecast_df[
            "Campaign Sq Ft"
        ]

        .cumsum()

    )

    campaign_forecast_df[
        "Completion %"
    ] = (

        campaign_forecast_df[
            "Cumulative Sq Ft"
        ]

        /

        total_project_sqft

        *

        100

    )

    # =================================================
    # PRODUCTION KPIs
    # =================================================

    total_media_required = (

        media_forecast_df[
            "Media Requirement"
        ]

        .sum()

    )

    total_gum_required = (

        gum_forecast_df[
            "Gum Required (Kg)"
        ]

        .sum()

    )

    total_rolls_required = int(

        np.ceil(

            total_media_required

            /

            roll_size_sqft

        )

    )

    production_kpis = {

        "Project Sq Ft":
            round(
                total_project_sqft,
                2
            ),

        "Media Required":
            round(
                total_media_required,
                2
            ),

        "Gum Required":
            round(
                total_gum_required,
                2
            ),

        "Rolls Required":
            total_rolls_required

    }

    # =================================================
    # SAVE TO SESSION
    # =================================================

    st.session_state.production_df = (
        production_df
    )

    st.session_state.weekly_production_df = (
        weekly_production_df
    )

    st.session_state.media_forecast_df = (
        media_forecast_df
    )

    st.session_state.gum_forecast_df = (
        gum_forecast_df
    )

    st.session_state.campaign_forecast_df = (
        campaign_forecast_df
    )

    st.session_state.production_kpis = (
        production_kpis
    )

    # =================================================
    # KPI CARDS
    # =================================================

    k1, k2, k3, k4 = st.columns(4)

    with k1:

        st.metric(
            "Project Sq Ft",
            f"{total_project_sqft:,.0f}"
        )

    with k2:

        st.metric(
            "Media Required",
            f"{total_media_required:,.0f}"
        )

    with k3:

        st.metric(
            "Gum Required (Kg)",
            f"{total_gum_required:,.0f}"
        )

    with k4:

        st.metric(
            "Rolls Required",
            f"{total_rolls_required:,}"
        )

    st.divider()

    # =================================================
    # PRODUCTION TABS
    # =================================================

    prod_tab1, prod_tab2, prod_tab3, prod_tab4 = st.tabs(

        [

            "Daily Production",

            "Weekly Production",

            "Media Forecast",

            "Gum Forecast"

        ]

    )

    # =================================================
    # DAILY PRODUCTION
    # =================================================

    with prod_tab1:

        st.subheader(
            "Daily Production Plan"
        )

        st.dataframe(
            production_df,
            use_container_width=True
        )

    # =================================================
    # WEEKLY PRODUCTION
    # =================================================

    with prod_tab2:

        st.subheader(
            "Weekly Production Forecast"
        )

        st.dataframe(
            weekly_production_df,
            use_container_width=True
        )

    # =================================================
    # MEDIA FORECAST
    # =================================================

    with prod_tab3:

        st.subheader(
            "Media Requirement Forecast"
        )

        st.dataframe(
            media_forecast_df,
            use_container_width=True
        )

    # =================================================
    # GUM FORECAST
    # =================================================

    with prod_tab4:

        st.subheader(
            "Gum Requirement Forecast"
        )

        st.dataframe(
            gum_forecast_df,
            use_container_width=True
        )

    st.divider()

# =====================================================
# END OF PART 3
# =====================================================
