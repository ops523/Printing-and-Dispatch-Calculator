# app.py

import streamlit as st
import pandas as pd

from modules.calculations import (
    validate_deployment_file,
    calculate_effective_productivity,
    calculate_total_teams,
    calculate_daily_campaign_production,
    calculate_dispatch_requirement,
    calculate_gum_requirement,
    build_campaign_summary,
    build_state_allocation
)

from modules.dispatch import (
    generate_dispatch_schedule,
    generate_dispatch_manifest,
    generate_dispatch_summary
)

from modules.printing import (
    generate_printing_plan,
    build_roll_summary,
    generate_printer_loading_dashboard
)

from modules.exports import (
    create_excel_export,
    build_kpi_dashboard,
    create_sample_upload_template
)

# --------------------------------------------------
# PAGE CONFIG
# --------------------------------------------------

st.set_page_config(
    page_title="Media Production & Dispatch Planner",
    page_icon="🚚",
    layout="wide"
)

# --------------------------------------------------
# LOGO
# --------------------------------------------------

try:
    st.image(
        "assets/logo.png",
        width=300
    )
except:
    pass

st.title("Media Production & Dispatch Planner V1")
st.caption(
    "Digital Wall Campaign Printing, Dispatch & Gum Planning"
)

# --------------------------------------------------
# SAMPLE TEMPLATE
# --------------------------------------------------

sample_template = create_sample_upload_template()

st.download_button(
    label="📥 Download Deployment Template",
    data=sample_template,
    file_name="deployment_template.xlsx",
    mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
)

st.divider()

# --------------------------------------------------
# CAMPAIGN DETAILS
# --------------------------------------------------

st.header("Campaign Inputs")

c1, c2 = st.columns(2)

with c1:

    campaign_name = st.text_input(
        "Campaign Name",
        value="New Campaign"
    )

    total_campaign_sqft = st.number_input(
        "Total Campaign Sq Ft",
        min_value=1.0,
        value=500000.0
    )

with c2:

    campaign_start_date = st.date_input(
        "Campaign Start Date"
    )

# --------------------------------------------------
# PRODUCTIVITY
# --------------------------------------------------

st.header("Team Productivity")

c1, c2, c3 = st.columns(3)

with c1:

    target_sqft_per_team_day = st.number_input(
        "Target Sq Ft / Team / Day",
        min_value=1.0,
        value=500.0
    )

with c2:

    efficiency_pct = st.number_input(
        "Efficiency %",
        min_value=1.0,
        max_value=100.0,
        value=85.0
    )

with c3:

    gum_per_1000_sqft = st.number_input(
        "Gum Kg / 1000 Sq Ft",
        min_value=0.0,
        value=5.0
    )

# --------------------------------------------------
# LOGISTICS
# --------------------------------------------------

st.header("Logistics Planning")

c1, c2, c3, c4 = st.columns(4)

with c1:

    dispatch_cycle_days = st.selectbox(
        "Dispatch Cycle",
        [7, 8, 9, 10],
        index=0
    )

with c2:

    transit_days = st.number_input(
        "Transit Time (Days)",
        min_value=1,
        value=3
    )

with c3:

    arrival_buffer_days = st.number_input(
        "Arrival Buffer (Days)",
        min_value=1,
        value=2
    )

with c4:

    field_inventory_buffer = st.number_input(
        "Field Inventory Buffer (Days)",
        min_value=0,
        value=2
    )

# --------------------------------------------------
# PRINTING
# --------------------------------------------------

st.header("Printing Parameters")

p1, p2, p3, p4 = st.columns(4)

with p1:

    printing_lead_days = st.number_input(
        "Printing Lead Time",
        min_value=1,
        value=2
    )

with p2:

    printer_capacity_per_day = st.number_input(
        "Printer Capacity / Day",
        min_value=1.0,
        value=25000.0
    )

with p3:

    media_width_ft = st.number_input(
        "Media Width (Ft)",
        min_value=1.0,
        value=4.0
    )

with p4:

    media_gsm = st.number_input(
        "Media GSM",
        min_value=1.0,
        value=110.0
    )

roll_length_ft = st.number_input(
    "Roll Length (Ft)",
    min_value=1.0,
    value=500.0
)

# --------------------------------------------------
# DEPLOYMENT FILE
# --------------------------------------------------

st.header("Deployment Plan Upload")

uploaded_file = st.file_uploader(
    "Upload Excel File",
    type=["xlsx"]
)

if uploaded_file is None:
    st.info(
        "Upload deployment file to continue."
    )
    st.stop()

deployment_df = pd.read_excel(
    uploaded_file
)

valid, missing = validate_deployment_file(
    deployment_df
)

if not valid:

    st.error(
        f"Missing Columns: {', '.join(missing)}"
    )

    st.stop()

# --------------------------------------------------
# CALCULATIONS
# --------------------------------------------------

effective_productivity = (
    calculate_effective_productivity(
        target_sqft_per_team_day,
        efficiency_pct
    )
)

total_teams = calculate_total_teams(
    deployment_df
)

daily_campaign_production = (
    calculate_daily_campaign_production(
        total_teams,
        effective_productivity
    )
)

dispatch_media_qty = (
    calculate_dispatch_requirement(
        daily_campaign_production,
        dispatch_cycle_days
    )
)

dispatch_gum_qty = (
    calculate_gum_requirement(
        dispatch_media_qty,
        gum_per_1000_sqft
    )
)

summary_df = build_campaign_summary(
    campaign_name,
    total_campaign_sqft,
    total_teams,
    effective_productivity,
    daily_campaign_production,
    dispatch_cycle_days,
    dispatch_media_qty,
    dispatch_gum_qty
)

state_allocation_df = (
    build_state_allocation(
        deployment_df,
        effective_productivity,
        dispatch_cycle_days,
        gum_per_1000_sqft
    )
)

dispatch_schedule_df = (
    generate_dispatch_schedule(
        campaign_start_date,
        total_campaign_sqft,
        daily_campaign_production,
        dispatch_cycle_days,
        transit_days,
        arrival_buffer_days,
        gum_per_1000_sqft
    )
)

dispatch_manifest_df = (
    generate_dispatch_manifest(
        dispatch_schedule_df,
        state_allocation_df
    )
)

printing_plan_df = (
    generate_printing_plan(
        dispatch_schedule_df,
        printing_lead_days,
        printer_capacity_per_day,
        media_width_ft,
        media_gsm
    )
)

roll_summary_df = (
    build_roll_summary(
        printing_plan_df,
        media_width_ft,
        roll_length_ft
    )
)

# --------------------------------------------------
# KPI DASHBOARD
# --------------------------------------------------

dispatch_summary = (
    generate_dispatch_summary(
        dispatch_schedule_df
    )
)

printer_dashboard = (
    generate_printer_loading_dashboard(
        printing_plan_df,
        printer_capacity_per_day
    )
)

kpi_dashboard = build_kpi_dashboard(

    total_campaign_sqft=
        total_campaign_sqft,

    total_teams=
        total_teams,

    daily_campaign_production=
        daily_campaign_production,

    dispatch_media_qty=
        dispatch_media_qty,

    dispatch_gum_qty=
        dispatch_gum_qty,

    total_dispatches=
        dispatch_summary[
            "Total Dispatches"
        ],

    total_media_weight=
        printer_dashboard[
            "Total Media Weight"
        ],

    total_running_feet=
        printer_dashboard[
            "Total Running Feet"
        ],

    avg_printer_utilization=
        printer_dashboard[
            "Average Utilization %"
        ]
)

# --------------------------------------------------
# KPI DISPLAY
# --------------------------------------------------

st.header("Campaign Dashboard")

k1, k2, k3, k4 = st.columns(4)

k1.metric(
    "Teams",
    total_teams
)

k2.metric(
    "Daily Production",
    f"{daily_campaign_production:,.0f}"
)

k3.metric(
    "Media/Dispatch",
    f"{dispatch_media_qty:,.0f}"
)

k4.metric(
    "Gum/Dispatch",
    f"{dispatch_gum_qty:,.1f} Kg"
)

# --------------------------------------------------
# DATA TABLES
# --------------------------------------------------

st.header("Campaign Summary")
st.dataframe(
    summary_df,
    use_container_width=True
)

st.header("District Allocation")
st.dataframe(
    deployment_df,
    use_container_width=True
)

st.header("State Allocation")
st.dataframe(
    state_allocation_df,
    use_container_width=True
)

st.header("Dispatch Schedule")
st.dataframe(
    dispatch_schedule_df,
    use_container_width=True
)

st.header("Dispatch Manifest")
st.dataframe(
    dispatch_manifest_df,
    use_container_width=True
)

st.header("Printing Plan")
st.dataframe(
    printing_plan_df,
    use_container_width=True
)

st.header("Roll Summary")
st.dataframe(
    roll_summary_df,
    use_container_width=True
)

# --------------------------------------------------
# EXCEL EXPORT
# --------------------------------------------------

excel_file = create_excel_export(
    summary_df,
    deployment_df,
    state_allocation_df,
    dispatch_schedule_df,
    dispatch_manifest_df,
    printing_plan_df,
    roll_summary_df,
    kpi_dashboard
)

st.download_button(
    label="📊 Download Planning Workbook",
    data=excel_file,
    file_name="media_dispatch_planner.xlsx",
    mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
)
