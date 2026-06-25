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

# =====================================================
# PART 4
# PRINTING PLANNING ENGINE
# =====================================================

if st.session_state.project_loaded:

    st.header("Printing Planning")

    # =================================================
    # LOAD DATA
    # =================================================

    media_forecast_df = (
        st.session_state.media_forecast_df
    )

    project_start = (
        st.session_state.district_timeline_df[
            "District Start"
        ].min()
    )

    # =================================================
    # BUILD PRINTING REQUIREMENT
    # =================================================

    total_media_required = (

        media_forecast_df[
            "Media Requirement"
        ].sum()

    )

    total_rolls_required = int(

        np.ceil(

            total_media_required

            /

            roll_size_sqft

        )

    )

    # =================================================
    # PRINT DAYS REQUIRED
    # =================================================

    total_print_days = int(

        np.ceil(

            total_media_required

            /

            daily_print_capacity

        )

    )

    # =================================================
    # PRINT START / END
    # =================================================

    # Print must finish before project starts

    print_end_date = (
        project_start
        - pd.Timedelta(days=1)
    )

    print_start_date = (
        print_end_date
        - pd.Timedelta(
            days=total_print_days - 1
        )
    )

    # =================================================
    # DAILY PRINT SCHEDULE
    # =================================================

    print_rows = []

    remaining_qty = (
        total_media_required
    )

    current_date = (
        print_start_date
    )

    while remaining_qty > 0:

        daily_qty = min(
            daily_print_capacity,
            remaining_qty
        )

        utilization = (

            daily_qty

            /

            daily_print_capacity

            *

            100

        )

        rolls_consumed = (

            daily_qty

            /

            roll_size_sqft

        )

        print_rows.append({

            "Print Date":
                current_date,

            "Daily Print Qty":
                round(
                    daily_qty,
                    2
                ),

            "Capacity":
                daily_print_capacity,

            "Utilization %":
                round(
                    utilization,
                    2
                ),

            "Rolls Consumed":
                round(
                    rolls_consumed,
                    2
                )

        })

        remaining_qty -= daily_qty

        current_date += pd.Timedelta(
            days=1
        )

    daily_print_df = pd.DataFrame(
        print_rows
    )

    # =================================================
    # PRINT SUMMARY
    # =================================================

    print_schedule_df = pd.DataFrame([{

        "Print Start":
            print_start_date,

        "Print End":
            print_end_date,

        "Total Media":
            round(
                total_media_required,
                2
            ),

        "Total Rolls":
            total_rolls_required,

        "Capacity":
            daily_print_capacity,

        "Print Days":
            total_print_days

    }])

    # =================================================
    # PRINTER LOADING
    # =================================================

    printer_loading_df = (
        daily_print_df.copy()
    )

    # =================================================
    # CAPACITY ALERTS
    # =================================================

    alert_rows = []

    overloaded_days = daily_print_df[

        daily_print_df[
            "Utilization %"
        ] > 100

    ]

    if len(overloaded_days):

        for _, row in overloaded_days.iterrows():

            alert_rows.append({

                "Date":
                    row["Print Date"],

                "Alert":
                    "Printer Overloaded"

            })

    print_alert_df = pd.DataFrame(
        alert_rows
    )

    # =================================================
    # PRINTING KPIs
    # =================================================

    avg_utilization = (

        daily_print_df[
            "Utilization %"
        ]

        .mean()

    )

    printing_kpis = {

        "Print Days":
            total_print_days,

        "Print Start":
            print_start_date.date(),

        "Print End":
            print_end_date.date(),

        "Avg Utilization %":
            round(
                avg_utilization,
                2
            ),

        "Total Rolls":
            total_rolls_required

    }

    # =================================================
    # SAVE TO SESSION
    # =================================================

    st.session_state.print_schedule_df = (
        print_schedule_df
    )

    st.session_state.daily_print_df = (
        daily_print_df
    )

    st.session_state.printer_loading_df = (
        printer_loading_df
    )

    st.session_state.print_alert_df = (
        print_alert_df
    )

    st.session_state.printing_kpis = (
        printing_kpis
    )

    # =================================================
    # KPI CARDS
    # =================================================

    k1, k2, k3, k4, k5 = st.columns(5)

    with k1:

        st.metric(
            "Print Days",
            total_print_days
        )

    with k2:

        st.metric(
            "Total Media",
            f"{total_media_required:,.0f}"
        )

    with k3:

        st.metric(
            "Total Rolls",
            total_rolls_required
        )

    with k4:

        st.metric(
            "Avg Utilization %",
            round(
                avg_utilization,
                1
            )
        )

    with k5:

        st.metric(
            "Capacity / Day",
            f"{daily_print_capacity:,.0f}"
        )

    st.divider()

    # =================================================
    # PRINTING TABS
    # =================================================

    print_tab1, print_tab2, print_tab3, print_tab4 = st.tabs(

        [

            "Print Summary",

            "Daily Print Plan",

            "Printer Loading",

            "Alerts"

        ]

    )

    # =================================================
    # SUMMARY
    # =================================================

    with print_tab1:

        st.subheader(
            "Print Schedule Summary"
        )

        st.dataframe(
            print_schedule_df,
            use_container_width=True
        )

    # =================================================
    # DAILY PLAN
    # =================================================

    with print_tab2:

        st.subheader(
            "Daily Printing Plan"
        )

        st.dataframe(
            daily_print_df,
            use_container_width=True
        )

    # =================================================
    # LOADING
    # =================================================

    with print_tab3:

        st.subheader(
            "Printer Loading"
        )

        st.dataframe(
            printer_loading_df,
            use_container_width=True
        )

    # =================================================
    # ALERTS
    # =================================================

    with print_tab4:

        st.subheader(
            "Capacity Alerts"
        )

        if len(print_alert_df):

            st.dataframe(
                print_alert_df,
                use_container_width=True
            )

        else:

            st.success(
                "No capacity issues detected."
            )

    st.divider()

# =====================================================
# END OF PART 4
# =====================================================

# =====================================================
# PART 5
# PROCUREMENT + DISPATCH ENGINE
# =====================================================

if st.session_state.project_loaded:

    st.header("Procurement & Dispatch Planning")

    # =================================================
    # LOAD DATA
    # =================================================

    district_timeline_df = (
        st.session_state.district_timeline_df
    )

    weekly_production_df = (
        st.session_state.weekly_production_df
    )

    media_forecast_df = (
        st.session_state.media_forecast_df
    )

    gum_forecast_df = (
        st.session_state.gum_forecast_df
    )

    production_df = (
        st.session_state.production_df
    )

    # =================================================
    # WEEKLY ROLL PROCUREMENT
    # =================================================

    roll_procurement_df = (
        media_forecast_df.copy()
    )

    roll_procurement_df[
        "Rolls Required"
    ] = np.ceil(

        roll_procurement_df[
            "Media Requirement"
        ]

        /

        roll_size_sqft

    )

    # =================================================
    # WEEKLY GUM PROCUREMENT
    # =================================================

    gum_procurement_df = (
        gum_forecast_df.copy()
    )

    # =================================================
    # PURCHASE PLAN
    # =================================================

    po_rows = []

    # ---------------------------------------------
    # ROLL PROCUREMENT
    # ---------------------------------------------

    for _, row in roll_procurement_df.iterrows():

        week_start = pd.to_datetime(
            row["Week"].split("/")[0]
        )

        order_date = (
            week_start
            - pd.Timedelta(
                days=roll_lead_time
            )
        )

        po_rows.append({

            "Order Type":
                "Media Roll",

            "Order Date":
                order_date,

            "Required Date":
                week_start,

            "Quantity":
                int(
                    row[
                        "Rolls Required"
                    ]
                )

        })

    # ---------------------------------------------
    # GUM PROCUREMENT
    # ---------------------------------------------

    for _, row in gum_procurement_df.iterrows():

        week_start = pd.to_datetime(
            row["Week"].split("/")[0]
        )

        order_date = (
            week_start
            - pd.Timedelta(
                days=gum_lead_time
            )
        )

        po_rows.append({

            "Order Type":
                "Gum",

            "Order Date":
                order_date,

            "Required Date":
                week_start,

            "Quantity":
                round(
                    row[
                        "Gum Required (Kg)"
                    ],
                    2
                )

        })

    purchase_plan_df = pd.DataFrame(
        po_rows
    )

    # =================================================
    # PO TRACKER
    # =================================================

    po_tracker_rows = []

    for _, row in purchase_plan_df.iterrows():

        if row["Order Type"] == "Media Roll":

            arrival_date = (

                row["Order Date"]

                +

                pd.Timedelta(
                    days=roll_lead_time
                )

            )

        else:

            arrival_date = (

                row["Order Date"]

                +

                pd.Timedelta(
                    days=gum_lead_time
                )

            )

        po_tracker_rows.append({

            "Item":
                row["Order Type"],

            "Quantity":
                row["Quantity"],

            "Order Date":
                row["Order Date"],

            "Expected Arrival":
                arrival_date

        })

    po_tracker_df = pd.DataFrame(
        po_tracker_rows
    )

    # =================================================
    # TEAM DISPATCH PLAN
    # =================================================

    dispatch_rows = []

    team_names = (
        district_timeline_df[
            "Team Name"
        ].unique()
    )

    dispatch_no = 1

    for team in team_names:

        team_df = (

            district_timeline_df[
                district_timeline_df[
                    "Team Name"
                ] == team
            ]

            .sort_values(
                "District Start"
            )

        )

        team_start = (
            team_df[
                "District Start"
            ].min()
        )

        team_end = (
            team_df[
                "District Finish"
            ].max()
        )

        current_cycle_start = (
            team_start
        )

        while current_cycle_start < team_end:

            cycle_end = (

                current_cycle_start

                +

                pd.Timedelta(
                    days=dispatch_cycle_days
                )

            )

            media_qty = (

                real_productivity

                *

                dispatch_cycle_days

                *

                (
                    1 +
                    printing_wastage / 100
                )

            )

            gum_qty = (

                real_productivity

                *

                dispatch_cycle_days

                /

                1000

                *

                gum_per_1000_sqft

            )

            dispatch_date = (

                cycle_end

                -

                pd.Timedelta(
                    days=arrival_buffer_days
                )

                -

                pd.Timedelta(
                    days=3
                )

            )

            arrival_date = (

                cycle_end

                -

                pd.Timedelta(
                    days=arrival_buffer_days
                )

            )

            dispatch_rows.append({

                "Team Name":
                    team,

                "Dispatch No":
                    dispatch_no,

                "Cycle Start":
                    current_cycle_start,

                "Cycle End":
                    cycle_end,

                "Dispatch Date":
                    dispatch_date,

                "Arrival Date":
                    arrival_date,

                "Media Qty (Sq Ft)":
                    round(
                        media_qty,
                        2
                    ),

                "Gum Qty (Kg)":
                    round(
                        gum_qty,
                        2
                    )

            })

            dispatch_no += 1

            current_cycle_start = (
                cycle_end
            )

    dispatch_df = pd.DataFrame(
        dispatch_rows
    )

    # =================================================
    # DISPATCH CALENDAR
    # =================================================

    dispatch_calendar_df = (

        dispatch_df

        .groupby(
            "Dispatch Date",
            as_index=False
        )

        .agg({

            "Media Qty (Sq Ft)":
                "sum",

            "Gum Qty (Kg)":
                "sum",

            "Team Name":
                "nunique"

        })

    )

    dispatch_calendar_df.rename(

        columns={

            "Team Name":
                "Teams Covered"

        },

        inplace=True

    )

    # =================================================
    # ARRIVAL CALENDAR
    # =================================================

    arrival_calendar_df = (

        dispatch_df

        .groupby(
            "Arrival Date",
            as_index=False
        )

        .agg({

            "Media Qty (Sq Ft)":
                "sum",

            "Gum Qty (Kg)":
                "sum"

        })

    )

    # =================================================
    # TEAM EXHAUSTION TRACKER
    # =================================================

    exhaustion_tracker_df = (
        dispatch_df[
            [

                "Team Name",
                "Dispatch No",
                "Cycle End"

            ]

        ]

        .copy()
    )

    exhaustion_tracker_df.rename(

        columns={

            "Cycle End":
                "Expected Exhaustion"

        },

        inplace=True

    )

    # =================================================
    # PROCUREMENT KPIs
    # =================================================

    total_rolls = int(

        roll_procurement_df[
            "Rolls Required"
        ].sum()

    )

    total_gum = round(

        gum_procurement_df[
            "Gum Required (Kg)"
        ].sum(),

        2

    )

    procurement_kpis = {

        "Rolls Required":
            total_rolls,

        "Gum Required":
            total_gum,

        "PO Count":
            len(
                purchase_plan_df
            ),

        "Dispatch Count":
            len(
                dispatch_df
            )

    }

    # =================================================
    # SAVE TO SESSION
    # =================================================

    st.session_state.roll_procurement_df = (
        roll_procurement_df
    )

    st.session_state.gum_procurement_df = (
        gum_procurement_df
    )

    st.session_state.purchase_plan_df = (
        purchase_plan_df
    )

    st.session_state.po_tracker_df = (
        po_tracker_df
    )

    st.session_state.dispatch_df = (
        dispatch_df
    )

    st.session_state.dispatch_calendar_df = (
        dispatch_calendar_df
    )

    st.session_state.arrival_calendar_df = (
        arrival_calendar_df
    )

    st.session_state.exhaustion_tracker_df = (
        exhaustion_tracker_df
    )

    st.session_state.procurement_kpis = (
        procurement_kpis
    )

    # =================================================
    # KPI CARDS
    # =================================================

    k1, k2, k3, k4 = st.columns(4)

    with k1:
        st.metric(
            "Rolls Required",
            total_rolls
        )

    with k2:
        st.metric(
            "Gum Required (Kg)",
            f"{total_gum:,.0f}"
        )

    with k3:
        st.metric(
            "Purchase Orders",
            len(
                purchase_plan_df
            )
        )

    with k4:
        st.metric(
            "Dispatches",
            len(dispatch_df)
        )

    st.divider()

    # =================================================
    # PROCUREMENT TABS
    # =================================================

    tab1, tab2, tab3, tab4, tab5 = st.tabs(

        [

            "Roll Procurement",

            "Gum Procurement",

            "Purchase Orders",

            "Dispatch Plan",

            "Exhaustion Tracker"

        ]

    )

    with tab1:

        st.dataframe(
            roll_procurement_df,
            use_container_width=True
        )

    with tab2:

        st.dataframe(
            gum_procurement_df,
            use_container_width=True
        )

    with tab3:

        st.dataframe(
            purchase_plan_df,
            use_container_width=True
        )

    with tab4:

        st.dataframe(
            dispatch_df,
            use_container_width=True
        )

    with tab5:

        st.dataframe(
            exhaustion_tracker_df,
            use_container_width=True
        )

    st.divider()

# =====================================================
# END OF PART 5
# =====================================================

# =====================================================
# PART 6
# INVENTORY ENGINE
# =====================================================

if st.session_state.project_loaded:

    st.header("Inventory Planning")

    # =================================================
    # LOAD DATA
    # =================================================

    purchase_plan_df = (
        st.session_state.purchase_plan_df
    )

    po_tracker_df = (
        st.session_state.po_tracker_df
    )

    roll_procurement_df = (
        st.session_state.roll_procurement_df
    )

    gum_procurement_df = (
        st.session_state.gum_procurement_df
    )

    # =================================================
    # BUILD INVENTORY CALENDAR
    # =================================================

    all_weeks = sorted(

        list(

            set(
                roll_procurement_df["Week"]
            )

            |

            set(
                gum_procurement_df["Week"]
            )

        )

    )

    # =================================================
    # ROLL INVENTORY
    # =================================================

    roll_inventory_rows = []

    opening_stock = opening_roll_stock

    for week in all_weeks:

        # -----------------------------------------
        # RECEIPTS
        # -----------------------------------------

        receipts = 0

        receipt_rows = po_tracker_df[

            po_tracker_df["Item"]
            == "Media Roll"

        ]

        if len(receipt_rows):

            receipts = (

                roll_procurement_df[
                    roll_procurement_df[
                        "Week"
                    ] == week
                ][
                    "Rolls Required"
                ]

                .sum()

            )

        # -----------------------------------------
        # CONSUMPTION
        # -----------------------------------------

        consumption = (

            roll_procurement_df[
                roll_procurement_df[
                    "Week"
                ] == week
            ][
                "Rolls Required"
            ]

            .sum()

        )

        closing_stock = (

            opening_stock

            + receipts

            - consumption

        )

        stockout = (
            closing_stock < 0
        )

        safety_breach = (
            closing_stock <
            safety_roll_stock
        )

        roll_inventory_rows.append({

            "Week":
                week,

            "Opening Stock":
                round(
                    opening_stock,
                    2
                ),

            "Receipts":
                round(
                    receipts,
                    2
                ),

            "Consumption":
                round(
                    consumption,
                    2
                ),

            "Closing Stock":
                round(
                    closing_stock,
                    2
                ),

            "Safety Stock":
                safety_roll_stock,

            "Safety Breach":
                safety_breach,

            "Stockout":
                stockout

        })

        opening_stock = (
            closing_stock
        )

    roll_inventory_df = pd.DataFrame(
        roll_inventory_rows
    )

    # =================================================
    # GUM INVENTORY
    # =================================================

    gum_inventory_rows = []

    opening_stock = opening_gum_stock

    for week in all_weeks:

        receipts = (

            gum_procurement_df[
                gum_procurement_df[
                    "Week"
                ] == week
            ][
                "Gum Required (Kg)"
            ]

            .sum()

        )

        consumption = (

            gum_procurement_df[
                gum_procurement_df[
                    "Week"
                ] == week
            ][
                "Gum Required (Kg)"
            ]

            .sum()

        )

        closing_stock = (

            opening_stock

            + receipts

            - consumption

        )

        stockout = (
            closing_stock < 0
        )

        safety_breach = (
            closing_stock <
            safety_gum_stock
        )

        gum_inventory_rows.append({

            "Week":
                week,

            "Opening Stock":
                round(
                    opening_stock,
                    2
                ),

            "Receipts":
                round(
                    receipts,
                    2
                ),

            "Consumption":
                round(
                    consumption,
                    2
                ),

            "Closing Stock":
                round(
                    closing_stock,
                    2
                ),

            "Safety Stock":
                safety_gum_stock,

            "Safety Breach":
                safety_breach,

            "Stockout":
                stockout

        })

        opening_stock = (
            closing_stock
        )

    gum_inventory_df = pd.DataFrame(
        gum_inventory_rows
    )

    # =================================================
    # ALERTS
    # =================================================

    roll_alert_df = roll_inventory_df[

        (
            roll_inventory_df[
                "Safety Breach"
            ]
        )

        |

        (
            roll_inventory_df[
                "Stockout"
            ]
        )

    ]

    gum_alert_df = gum_inventory_df[

        (
            gum_inventory_df[
                "Safety Breach"
            ]
        )

        |

        (
            gum_inventory_df[
                "Stockout"
            ]
        )

    ]

    # =================================================
    # INVENTORY KPIs
    # =================================================

    inventory_kpis = {

        "Opening Rolls":
            opening_roll_stock,

        "Opening Gum":
            opening_gum_stock,

        "Roll Alerts":
            len(
                roll_alert_df
            ),

        "Gum Alerts":
            len(
                gum_alert_df
            )

    }

    # =================================================
    # SAVE TO SESSION
    # =================================================

    st.session_state.roll_inventory_df = (
        roll_inventory_df
    )

    st.session_state.gum_inventory_df = (
        gum_inventory_df
    )

    st.session_state.roll_alert_df = (
        roll_alert_df
    )

    st.session_state.gum_alert_df = (
        gum_alert_df
    )

    st.session_state.inventory_kpis = (
        inventory_kpis
    )

    # =================================================
    # KPI CARDS
    # =================================================

    k1, k2, k3, k4 = st.columns(4)

    with k1:
        st.metric(
            "Opening Rolls",
            opening_roll_stock
        )

    with k2:
        st.metric(
            "Opening Gum (Kg)",
            opening_gum_stock
        )

    with k3:
        st.metric(
            "Roll Alerts",
            len(
                roll_alert_df
            )
        )

    with k4:
        st.metric(
            "Gum Alerts",
            len(
                gum_alert_df
            )
        )

    st.divider()

    # =================================================
    # INVENTORY TABS
    # =================================================

    inv_tab1, inv_tab2, inv_tab3, inv_tab4 = st.tabs(

        [

            "Roll Inventory",

            "Gum Inventory",

            "Roll Alerts",

            "Gum Alerts"

        ]

    )

    # =================================================
    # ROLL INVENTORY
    # =================================================

    with inv_tab1:

        st.subheader(
            "Media Roll Inventory"
        )

        st.dataframe(
            roll_inventory_df,
            use_container_width=True
        )

    # =================================================
    # GUM INVENTORY
    # =================================================

    with inv_tab2:

        st.subheader(
            "Gum Inventory"
        )

        st.dataframe(
            gum_inventory_df,
            use_container_width=True
        )

    # =================================================
    # ROLL ALERTS
    # =================================================

    with inv_tab3:

        if len(roll_alert_df):

            st.warning(
                "Roll Inventory Issues Detected"
            )

            st.dataframe(
                roll_alert_df,
                use_container_width=True
            )

        else:

            st.success(
                "No Roll Inventory Issues"
            )

    # =================================================
    # GUM ALERTS
    # =================================================

    with inv_tab4:

        if len(gum_alert_df):

            st.warning(
                "Gum Inventory Issues Detected"
            )

            st.dataframe(
                gum_alert_df,
                use_container_width=True
            )

        else:

            st.success(
                "No Gum Inventory Issues"
            )

    st.divider()

# =====================================================
# END OF PART 6
# =====================================================

# =====================================================
# PART 7
# REFORECAST ENGINE
# =====================================================

if (
    st.session_state.project_loaded
    and project_mode == "Running Campaign"
):

    st.header("Running Campaign Reforecast")

    # =================================================
    # LOAD DATA
    # =================================================

    production_kpis = (
        st.session_state.production_kpis
    )

    timeline_kpis = (
        st.session_state.timeline_kpis
    )

    total_project_sqft = (
        production_kpis[
            "Project Sq Ft"
        ]
    )

    # =================================================
    # CURRENT STATUS INPUTS
    # =================================================

    st.subheader(
        "Current Progress"
    )

    col1, col2, col3 = st.columns(3)

    with col1:

        actual_completed_sqft = st.number_input(
            "Actual Completed Sq Ft",
            min_value=0.0,
            value=float(completed_sqft)
        )

    with col2:

        actual_media_in_field = st.number_input(
            "Media Available in Field (Sq Ft)",
            min_value=0.0,
            value=float(media_in_field)
        )

    with col3:

        actual_gum_in_field = st.number_input(
            "Gum Available in Field (Kg)",
            min_value=0.0,
            value=float(gum_in_field)
        )

    # =================================================
    # REMAINING WORK
    # =================================================

    remaining_sqft = max(

        total_project_sqft

        -

        actual_completed_sqft,

        0

    )

    completion_pct = 0

    if total_project_sqft > 0:

        completion_pct = (

            actual_completed_sqft

            /

            total_project_sqft

            *

            100

        )

    # =================================================
    # REMAINING MATERIALS
    # =================================================

    remaining_media_required = (

        remaining_sqft

        *

        (
            1 +
            printing_wastage / 100
        )

    )

    remaining_gum_required = (

        remaining_sqft

        /

        1000

        *

        gum_per_1000_sqft

    )

    remaining_rolls_required = int(

        np.ceil(

            remaining_media_required

            /

            roll_size_sqft

        )

    )

    # =================================================
    # NET REQUIREMENT
    # =================================================

    net_media_requirement = max(

        remaining_media_required

        -

        actual_media_in_field,

        0

    )

    net_gum_requirement = max(

        remaining_gum_required

        -

        actual_gum_in_field,

        0

    )

    # =================================================
    # CURRENT ACTIVE TEAMS
    # =================================================

    current_team_count = (
        timeline_kpis[
            "Total Teams"
        ]
    )

    # =================================================
    # DAYS REMAINING
    # =================================================

    daily_campaign_capacity = (

        current_team_count

        *

        real_productivity

    )

    if daily_campaign_capacity > 0:

        remaining_days = int(

            np.ceil(

                remaining_sqft

                /

                daily_campaign_capacity

            )

        )

    else:

        remaining_days = 0

    revised_completion_date = (

        pd.Timestamp.today()

        +

        pd.Timedelta(
            days=remaining_days
        )

    )

    # =================================================
    # RECOVERY ANALYSIS
    # =================================================

    recovery_rows = []

    for additional_teams in range(0, 11):

        new_team_count = (

            current_team_count

            +

            additional_teams

        )

        new_capacity = (

            new_team_count

            *

            real_productivity

        )

        if new_capacity > 0:

            new_days = int(

                np.ceil(

                    remaining_sqft

                    /

                    new_capacity

                )

            )

        else:

            new_days = 0

        recovery_rows.append({

            "Additional Teams":
                additional_teams,

            "Total Teams":
                new_team_count,

            "Campaign Capacity":
                round(
                    new_capacity,
                    2
                ),

            "Days Remaining":
                new_days,

            "Completion Date":
                (
                    pd.Timestamp.today()
                    +
                    pd.Timedelta(days=new_days)
                ).date()

        })

    recovery_df = pd.DataFrame(
        recovery_rows
    )

    # =================================================
    # DELAY ANALYSIS
    # =================================================

    delay_rows = []

    for delay_days in [

        0, 7, 14, 21, 30

    ]:

        delay_rows.append({

            "Delay":
                delay_days,

            "New Completion":

                (
                    revised_completion_date

                    +

                    pd.Timedelta(
                        days=delay_days
                    )

                ).date()

        })

    delay_df = pd.DataFrame(
        delay_rows
    )

    # =================================================
    # REVISED PROCUREMENT
    # =================================================

    revised_procurement_df = pd.DataFrame([{

        "Remaining Sq Ft":
            round(
                remaining_sqft,
                2
            ),

        "Media Required":
            round(
                net_media_requirement,
                2
            ),

        "Gum Required (Kg)":
            round(
                net_gum_requirement,
                2
            ),

        "Rolls Required":
            remaining_rolls_required

    }])

    # =================================================
    # SAVE TO SESSION
    # =================================================

    st.session_state.recovery_df = (
        recovery_df
    )

    st.session_state.delay_df = (
        delay_df
    )

    st.session_state.revised_procurement_df = (
        revised_procurement_df
    )

    # =================================================
    # KPI CARDS
    # =================================================

    k1, k2, k3, k4 = st.columns(4)

    with k1:

        st.metric(
            "Completion %",
            f"{completion_pct:.1f}%"
        )

    with k2:

        st.metric(
            "Remaining Sq Ft",
            f"{remaining_sqft:,.0f}"
        )

    with k3:

        st.metric(
            "Days Remaining",
            remaining_days
        )

    with k4:

        st.metric(
            "Current Teams",
            current_team_count
        )

    k5, k6, k7, k8 = st.columns(4)

    with k5:

        st.metric(
            "Media Needed",
            f"{net_media_requirement:,.0f}"
        )

    with k6:

        st.metric(
            "Gum Needed (Kg)",
            f"{net_gum_requirement:,.0f}"
        )

    with k7:

        st.metric(
            "Rolls Needed",
            remaining_rolls_required
        )

    with k8:

    st.metric(
        "Forecast Finish",
        revised_completion_date.strftime("%d-%b-%Y")
        )

    st.divider()

    # =================================================
    # REFORECAST TABS
    # =================================================

    tab1, tab2, tab3 = st.tabs(

        [

            "Recovery Scenarios",

            "Delay Analysis",

            "Revised Procurement"

        ]

    )

    # =================================================
    # RECOVERY
    # =================================================

    with tab1:

        st.subheader(
            "Add Teams Scenario"
        )

        st.dataframe(
            recovery_df,
            use_container_width=True
        )

    # =================================================
    # DELAY
    # =================================================

    with tab2:

        st.subheader(
            "Delay Impact"
        )

        st.dataframe(
            delay_df,
            use_container_width=True
        )

    # =================================================
    # PROCUREMENT
    # =================================================

    with tab3:

        st.subheader(
            "Remaining Material Requirement"
        )

        st.dataframe(
            revised_procurement_df,
            use_container_width=True
        )

    st.divider()

# =====================================================
# END OF PART 7
# =====================================================

# =====================================================
# PART 8
# EXECUTIVE DASHBOARD & CHARTS
# =====================================================

if st.session_state.project_loaded:

    st.header("Executive Dashboard")

    # =================================================
    # LOAD DATA
    # =================================================

    timeline_kpis = st.session_state.timeline_kpis
    production_kpis = st.session_state.production_kpis
    procurement_kpis = st.session_state.procurement_kpis
    printing_kpis = st.session_state.printing_kpis
    inventory_kpis = st.session_state.inventory_kpis

    weekly_loading_df = st.session_state.weekly_loading_df

    campaign_forecast_df = (
        st.session_state.campaign_forecast_df
    )

    media_forecast_df = (
        st.session_state.media_forecast_df
    )

    gum_forecast_df = (
        st.session_state.gum_forecast_df
    )

    printer_loading_df = (
        st.session_state.printer_loading_df
    )

    dispatch_calendar_df = (
        st.session_state.dispatch_calendar_df
    )

    arrival_calendar_df = (
        st.session_state.arrival_calendar_df
    )

    roll_inventory_df = (
        st.session_state.roll_inventory_df
    )

    gum_inventory_df = (
        st.session_state.gum_inventory_df
    )

    district_timeline_df = (
        st.session_state.district_timeline_df
    )

    team_summary_df = (
        st.session_state.team_summary_df
    )

    movement_df = (
        st.session_state.movement_df
    )

    purchase_plan_df = (
        st.session_state.purchase_plan_df
    )

    # =================================================
    # EXECUTIVE KPI STRIP
    # =================================================

    st.subheader("Executive KPIs")

    row1 = st.columns(5)

    with row1[0]:
        st.metric(
            "Teams",
            timeline_kpis["Total Teams"]
        )

    with row1[1]:
        st.metric(
            "Districts",
            timeline_kpis["Total Districts"]
        )

    with row1[2]:
        st.metric(
            "Project Sq Ft",
            f"{production_kpis['Project Sq Ft']:,.0f}"
        )

    with row1[3]:
        st.metric(
            "Rolls Required",
            procurement_kpis["Rolls Required"]
        )

    with row1[4]:
        st.metric(
            "Gum Required (Kg)",
            round(
                procurement_kpis["Gum Required"],
                0
            )
        )

    row2 = st.columns(5)

    with row2[0]:
        st.metric(
            "Print Days",
            printing_kpis["Print Days"]
        )

    with row2[1]:
        st.metric(
            "Dispatches",
            procurement_kpis["Dispatch Count"]
        )

    with row2[2]:
        st.metric(
            "Roll Alerts",
            inventory_kpis["Roll Alerts"]
        )

    with row2[3]:
        st.metric(
            "Gum Alerts",
            inventory_kpis["Gum Alerts"]
        )

    with row2[4]:
        st.metric(
            "Printer Utilization %",
            printing_kpis["Avg Utilization %"]
        )

    st.divider()

    # =================================================
    # CHART TABS
    # =================================================

    chart_tab1, chart_tab2, chart_tab3, chart_tab4 = st.tabs(
        [
            "Operations",
            "Printing",
            "Dispatch",
            "Inventory"
        ]
    )

    # =================================================
    # OPERATIONS
    # =================================================

    with chart_tab1:

        c1, c2 = st.columns(2)

        with c1:

            st.plotly_chart(
                plot_active_teams(
                    weekly_loading_df
                ),
                use_container_width=True
            )

        with c2:

            st.plotly_chart(
                plot_weekly_production(
                    campaign_forecast_df
                ),
                use_container_width=True
            )

        c3, c4 = st.columns(2)

        with c3:

            st.plotly_chart(
                plot_media_requirement(
                    media_forecast_df
                ),
                use_container_width=True
            )

        with c4:

            st.plotly_chart(
                plot_gum_requirement(
                    gum_forecast_df
                ),
                use_container_width=True
            )

    # =================================================
    # PRINTING
    # =================================================

    with chart_tab2:

        c1, c2 = st.columns(2)

        with c1:

            st.plotly_chart(
                plot_printer_loading(
                    printer_loading_df
                ),
                use_container_width=True
            )

        with c2:

            st.plotly_chart(
                plot_printer_utilization(
                    printer_loading_df
                ),
                use_container_width=True
            )

    # =================================================
    # DISPATCH
    # =================================================

    with chart_tab3:

        c1, c2 = st.columns(2)

        with c1:

            st.plotly_chart(
                plot_dispatch_load(
                    dispatch_calendar_df
                ),
                use_container_width=True
            )

        with c2:

            st.plotly_chart(
                plot_arrival_load(
                    arrival_calendar_df
                ),
                use_container_width=True
            )

    # =================================================
    # INVENTORY
    # =================================================

    with chart_tab4:

        c1, c2 = st.columns(2)

        with c1:

            st.plotly_chart(
                plot_roll_inventory(
                    roll_inventory_df
                ),
                use_container_width=True
            )

        with c2:

            st.plotly_chart(
                plot_gum_inventory(
                    gum_inventory_df
                ),
                use_container_width=True
            )

    st.divider()

    # =================================================
    # GANTT SECTION
    # =================================================

    st.subheader("Execution Timelines")

    gantt_tab1, gantt_tab2, gantt_tab3 = st.tabs(
        [
            "District Timeline",
            "Team Timeline",
            "Team Movement"
        ]
    )

    with gantt_tab1:

        st.plotly_chart(
            plot_district_timeline(
                district_timeline_df
            ),
            use_container_width=True
        )

    with gantt_tab2:

        st.plotly_chart(
            plot_team_timeline(
                team_summary_df
            ),
            use_container_width=True
        )

    with gantt_tab3:

        movement_chart = (
            plot_team_movements(
                movement_df
            )
        )

        if movement_chart is not None:

            st.plotly_chart(
                movement_chart,
                use_container_width=True
            )

        else:

            st.info(
                "No movement records available."
            )

    st.divider()

    # =================================================
    # PROCUREMENT DASHBOARD
    # =================================================

    st.subheader(
        "Procurement Dashboard"
    )

    st.plotly_chart(
        plot_procurement_plan(
            purchase_plan_df
        ),
        use_container_width=True
    )

    st.divider()

    # =================================================
    # EXECUTIVE SUMMARY TABLE
    # =================================================

    st.subheader(
        "Executive Summary"
    )

    executive_summary_df = pd.DataFrame({

        "Metric": [

            "Total Teams",
            "Total Districts",
            "Project Sq Ft",
            "Media Required",
            "Gum Required",
            "Rolls Required",
            "Print Days",
            "Dispatch Count",
            "Roll Alerts",
            "Gum Alerts"

        ],

        "Value": [

            timeline_kpis["Total Teams"],
            timeline_kpis["Total Districts"],
            production_kpis["Project Sq Ft"],
            production_kpis["Media Required"],
            production_kpis["Gum Required"],
            procurement_kpis["Rolls Required"],
            printing_kpis["Print Days"],
            procurement_kpis["Dispatch Count"],
            inventory_kpis["Roll Alerts"],
            inventory_kpis["Gum Alerts"]

        ]

    })

    st.dataframe(
        executive_summary_df,
        use_container_width=True
    )

    st.divider()

# =====================================================
# END OF PART 8
# =====================================================

# =====================================================
# PART 9
# EXPORT CENTER
# =====================================================

if st.session_state.project_loaded:

    st.header("Export Center")

    # =================================================
    # LOAD DATA
    # =================================================

    district_timeline_df = (
        st.session_state.district_timeline_df
    )

    team_summary_df = (
        st.session_state.team_summary_df
    )

    movement_df = (
        st.session_state.movement_df
    )

    weekly_loading_df = (
        st.session_state.weekly_loading_df
    )

    production_df = (
        st.session_state.production_df
    )

    weekly_production_df = (
        st.session_state.weekly_production_df
    )

    media_forecast_df = (
        st.session_state.media_forecast_df
    )

    gum_forecast_df = (
        st.session_state.gum_forecast_df
    )

    daily_print_df = (
        st.session_state.daily_print_df
    )

    print_schedule_df = (
        st.session_state.print_schedule_df
    )

    dispatch_df = (
        st.session_state.dispatch_df
    )

    dispatch_calendar_df = (
        st.session_state.dispatch_calendar_df
    )

    arrival_calendar_df = (
        st.session_state.arrival_calendar_df
    )

    purchase_plan_df = (
        st.session_state.purchase_plan_df
    )

    po_tracker_df = (
        st.session_state.po_tracker_df
    )

    roll_inventory_df = (
        st.session_state.roll_inventory_df
    )

    gum_inventory_df = (
        st.session_state.gum_inventory_df
    )

    roll_alert_df = (
        st.session_state.roll_alert_df
    )

    gum_alert_df = (
        st.session_state.gum_alert_df
    )

    # =================================================
    # KPI DATA
    # =================================================

    timeline_kpis = (
        st.session_state.timeline_kpis
    )

    production_kpis = (
        st.session_state.production_kpis
    )

    procurement_kpis = (
        st.session_state.procurement_kpis
    )

    printing_kpis = (
        st.session_state.printing_kpis
    )

    inventory_kpis = (
        st.session_state.inventory_kpis
    )

    # =================================================
    # EXECUTIVE SUMMARY
    # =================================================

    executive_summary_df = pd.DataFrame({

        "Metric": [

            "Total Teams",
            "Total Districts",
            "Project Sq Ft",
            "Media Required",
            "Gum Required",
            "Rolls Required",
            "Print Days",
            "Dispatch Count",
            "Roll Alerts",
            "Gum Alerts"

        ],

        "Value": [

            timeline_kpis["Total Teams"],
            timeline_kpis["Total Districts"],
            production_kpis["Project Sq Ft"],
            production_kpis["Media Required"],
            production_kpis["Gum Required"],
            procurement_kpis["Rolls Required"],
            printing_kpis["Print Days"],
            procurement_kpis["Dispatch Count"],
            inventory_kpis["Roll Alerts"],
            inventory_kpis["Gum Alerts"]

        ]

    })

    # =================================================
    # BUILD MASTER WORKBOOK
    # =================================================

    workbook_buffer = io.BytesIO()

    with pd.ExcelWriter(
        workbook_buffer,
        engine="xlsxwriter"
    ) as writer:

        # ---------------------------------------------
        # EXECUTIVE
        # ---------------------------------------------

        executive_summary_df.to_excel(
            writer,
            sheet_name="Executive Summary",
            index=False
        )

        # ---------------------------------------------
        # TEAM PLANNING
        # ---------------------------------------------

        team_summary_df.to_excel(
            writer,
            sheet_name="Team Summary",
            index=False
        )

        district_timeline_df.to_excel(
            writer,
            sheet_name="District Timeline",
            index=False
        )

        movement_df.to_excel(
            writer,
            sheet_name="Movement Plan",
            index=False
        )

        weekly_loading_df.to_excel(
            writer,
            sheet_name="Weekly Loading",
            index=False
        )

        # ---------------------------------------------
        # PRODUCTION
        # ---------------------------------------------

        production_df.to_excel(
            writer,
            sheet_name="Daily Production",
            index=False
        )

        weekly_production_df.to_excel(
            writer,
            sheet_name="Weekly Production",
            index=False
        )

        media_forecast_df.to_excel(
            writer,
            sheet_name="Media Forecast",
            index=False
        )

        gum_forecast_df.to_excel(
            writer,
            sheet_name="Gum Forecast",
            index=False
        )

        # ---------------------------------------------
        # PRINTING
        # ---------------------------------------------

        print_schedule_df.to_excel(
            writer,
            sheet_name="Print Summary",
            index=False
        )

        daily_print_df.to_excel(
            writer,
            sheet_name="Daily Printing",
            index=False
        )

        # ---------------------------------------------
        # PROCUREMENT
        # ---------------------------------------------

        purchase_plan_df.to_excel(
            writer,
            sheet_name="Purchase Orders",
            index=False
        )

        po_tracker_df.to_excel(
            writer,
            sheet_name="PO Tracker",
            index=False
        )

        # ---------------------------------------------
        # DISPATCH
        # ---------------------------------------------

        dispatch_df.to_excel(
            writer,
            sheet_name="Dispatch Plan",
            index=False
        )

        dispatch_calendar_df.to_excel(
            writer,
            sheet_name="Dispatch Calendar",
            index=False
        )

        arrival_calendar_df.to_excel(
            writer,
            sheet_name="Arrival Calendar",
            index=False
        )

        # ---------------------------------------------
        # INVENTORY
        # ---------------------------------------------

        roll_inventory_df.to_excel(
            writer,
            sheet_name="Roll Inventory",
            index=False
        )

        gum_inventory_df.to_excel(
            writer,
            sheet_name="Gum Inventory",
            index=False
        )

        roll_alert_df.to_excel(
            writer,
            sheet_name="Roll Alerts",
            index=False
        )

        gum_alert_df.to_excel(
            writer,
            sheet_name="Gum Alerts",
            index=False
        )

        # ---------------------------------------------
        # REFORECAST
        # ---------------------------------------------

        if project_mode == "Running Campaign":

            if "recovery_df" in st.session_state:

                st.session_state.recovery_df.to_excel(
                    writer,
                    sheet_name="Recovery Scenarios",
                    index=False
                )

            if "delay_df" in st.session_state:

                st.session_state.delay_df.to_excel(
                    writer,
                    sheet_name="Delay Analysis",
                    index=False
                )

            if "revised_procurement_df" in st.session_state:

                st.session_state.revised_procurement_df.to_excel(
                    writer,
                    sheet_name="Reforecast Procurement",
                    index=False
                )

    workbook_buffer.seek(0)

    # =================================================
    # DOWNLOAD MASTER WORKBOOK
    # =================================================

    st.subheader("Full Workbook")

    st.download_button(
        label="📥 Download Full Planning Workbook",
        data=workbook_buffer.getvalue(),
        file_name="Campaign_Supply_Chain_Planner.xlsx",
        mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
    )

    # =================================================
    # DOWNLOAD EXECUTIVE SUMMARY
    # =================================================

    summary_buffer = io.BytesIO()

    with pd.ExcelWriter(
        summary_buffer,
        engine="xlsxwriter"
    ) as writer:

        executive_summary_df.to_excel(
            writer,
            sheet_name="Summary",
            index=False
        )

    summary_buffer.seek(0)

    st.download_button(
        label="📥 Download Executive Summary",
        data=summary_buffer.getvalue(),
        file_name="Executive_Summary.xlsx",
        mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
    )

    # =================================================
    # DOWNLOAD TEMPLATES
    # =================================================

    st.subheader("Templates")

    # ---------------------------------------------
    # TEAM TEMPLATE
    # ---------------------------------------------

    team_template = pd.DataFrame({

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

    team_template_buffer = io.BytesIO()

    with pd.ExcelWriter(
        team_template_buffer,
        engine="xlsxwriter"
    ) as writer:

        team_template.to_excel(
            writer,
            sheet_name="Template",
            index=False
        )

    team_template_buffer.seek(0)

    st.download_button(
        label="📥 Download Team Planning Template",
        data=team_template_buffer.getvalue(),
        file_name="Team_Planning_Template.xlsx",
        mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
    )

    # ---------------------------------------------
    # RUNNING PROJECT TEMPLATE
    # ---------------------------------------------

    running_template = pd.DataFrame({

        "Team Name": ["Team A"],

        "Completed Sq Ft": [0],

        "Media In Field": [0],

        "Gum In Field": [0]

    })

    running_template_buffer = io.BytesIO()

    with pd.ExcelWriter(
        running_template_buffer,
        engine="xlsxwriter"
    ) as writer:

        running_template.to_excel(
            writer,
            sheet_name="Running Project",
            index=False
        )

    running_template_buffer.seek(0)

    st.download_button(
        label="📥 Download Running Campaign Template",
        data=running_template_buffer.getvalue(),
        file_name="Running_Campaign_Template.xlsx",
        mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
    )

    st.success(
        "Export package ready."
    )

# =====================================================
# END OF PART 9
# =====================================================
