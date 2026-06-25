# modules/dashboard.py

import pandas as pd
import plotly.express as px
import plotly.graph_objects as go


# --------------------------------------------------
# ACTIVE TEAMS BY WEEK
# --------------------------------------------------

def plot_active_teams(weekly_loading_df):

    fig = px.line(
        weekly_loading_df,
        x="Week",
        y="Active Teams",
        markers=True,
        title="Active Teams by Week"
    )

    fig.update_layout(
        height=450
    )

    return fig


# --------------------------------------------------
# WEEKLY PRODUCTION
# --------------------------------------------------

def plot_weekly_production(
    campaign_forecast_df
):

    fig = px.bar(
        campaign_forecast_df,
        x="Week",
        y="Campaign Sq Ft",
        title="Weekly Production Forecast"
    )

    fig.update_layout(
        height=450
    )

    return fig


# --------------------------------------------------
# WEEKLY MEDIA REQUIREMENT
# --------------------------------------------------

def plot_media_requirement(
    media_forecast_df
):

    fig = px.bar(
        media_forecast_df,
        x="Week",
        y="Media Requirement",
        title="Weekly Media Requirement"
    )

    fig.update_layout(
        height=450
    )

    return fig


# --------------------------------------------------
# WEEKLY GUM REQUIREMENT
# --------------------------------------------------

def plot_gum_requirement(
    gum_forecast_df
):

    fig = px.bar(
        gum_forecast_df,
        x="Week",
        y="Gum Required (Kg)",
        title="Weekly Gum Requirement"
    )

    fig.update_layout(
        height=450
    )

    return fig


# --------------------------------------------------
# PRINTING LOAD
# --------------------------------------------------

def plot_printer_loading(
    printer_loading_df
):

    fig = go.Figure()

    fig.add_trace(

        go.Bar(

            x=printer_loading_df[
                "Print Date"
            ],

            y=printer_loading_df[
                "Daily Print Qty"
            ],

            name="Print Qty"

        )

    )

    fig.add_trace(

        go.Scatter(

            x=printer_loading_df[
                "Print Date"
            ],

            y=printer_loading_df[
                "Capacity"
            ],

            mode="lines",

            name="Capacity"

        )

    )

    fig.update_layout(

        title="Printer Loading vs Capacity",

        height=500

    )

    return fig


# --------------------------------------------------
# PRINTER UTILIZATION
# --------------------------------------------------

def plot_printer_utilization(
    printer_loading_df
):

    fig = px.line(

        printer_loading_df,

        x="Print Date",

        y="Utilization %",

        markers=True,

        title="Printer Utilization %"

    )

    fig.update_layout(
        height=450
    )

    return fig


# --------------------------------------------------
# DISPATCH CALENDAR
# --------------------------------------------------

def plot_dispatch_load(
    dispatch_calendar_df
):

    fig = px.bar(

        dispatch_calendar_df,

        x="Dispatch Date",

        y="Media Qty (Sq Ft)",

        title="Dispatch Load"

    )

    fig.update_layout(
        height=450
    )

    return fig


# --------------------------------------------------
# ARRIVAL LOAD
# --------------------------------------------------

def plot_arrival_load(
    arrival_calendar_df
):

    fig = px.bar(

        arrival_calendar_df,

        x="Required Arrival",

        y="Media Qty (Sq Ft)",

        title="Material Arrival Calendar"

    )

    fig.update_layout(
        height=450
    )

    return fig


# --------------------------------------------------
# ROLL INVENTORY TREND
# --------------------------------------------------

def plot_roll_inventory(
    roll_inventory_df
):

    fig = go.Figure()

    fig.add_trace(

        go.Scatter(

            x=roll_inventory_df["Week"],

            y=roll_inventory_df[
                "Closing Stock"
            ],

            mode="lines+markers",

            name="Closing Stock"

        )

    )

    fig.add_trace(

        go.Scatter(

            x=roll_inventory_df["Week"],

            y=roll_inventory_df[
                "Safety Stock"
            ],

            mode="lines",

            name="Safety Stock"

        )

    )

    fig.update_layout(

        title="Media Roll Inventory",

        height=450

    )

    return fig


# --------------------------------------------------
# GUM INVENTORY TREND
# --------------------------------------------------

def plot_gum_inventory(
    gum_inventory_df
):

    fig = go.Figure()

    fig.add_trace(

        go.Scatter(

            x=gum_inventory_df["Week"],

            y=gum_inventory_df[
                "Closing Stock"
            ],

            mode="lines+markers",

            name="Closing Stock"

        )

    )

    fig.add_trace(

        go.Scatter(

            x=gum_inventory_df["Week"],

            y=gum_inventory_df[
                "Safety Stock"
            ],

            mode="lines",

            name="Safety Stock"

        )

    )

    fig.update_layout(

        title="Gum Inventory",

        height=450

    )

    return fig


# --------------------------------------------------
# DISTRICT TIMELINE (GANTT)
# --------------------------------------------------

def plot_district_timeline(
    district_timeline_df
):

    fig = px.timeline(

        district_timeline_df,

        x_start="District Start",

        x_end="District Finish",

        y="District",

        color="Team Name",

        title="District Execution Timeline"

    )

    fig.update_yaxes(
        autorange="reversed"
    )

    fig.update_layout(
        height=700
    )

    return fig


# --------------------------------------------------
# TEAM TIMELINE
# --------------------------------------------------

def plot_team_timeline(
    team_summary_df
):

    fig = px.timeline(

        team_summary_df,

        x_start="Project Start",

        x_end="Project Finish",

        y="Team Name",

        color="Team Name",

        title="Team Timeline"

    )

    fig.update_yaxes(
        autorange="reversed"
    )

    fig.update_layout(
        height=600
    )

    return fig


# --------------------------------------------------
# TEAM MOVEMENT
# --------------------------------------------------

def plot_team_movements(
    movement_df
):

    if len(movement_df) == 0:

        return None

    fig = px.scatter(

        movement_df,

        x="Move Date",

        y="Team Name",

        color="From District",

        hover_data=[

            "To District",

            "Transit Days"

        ],

        title="Team Movement Schedule"

    )

    fig.update_layout(
        height=550
    )

    return fig


# --------------------------------------------------
# PROCUREMENT LOAD
# --------------------------------------------------

def plot_procurement_plan(
    purchase_plan_df
):

    fig = px.bar(

        purchase_plan_df,

        x="Order Date",

        y="Quantity",

        color="Order Type",

        title="Procurement Orders"

    )

    fig.update_layout(
        height=500
    )

    return fig


# --------------------------------------------------
# PROJECT KPI CARDS
# --------------------------------------------------

def build_dashboard_metrics(
    timeline_kpis,
    procurement_kpis,
    printing_kpis,
    inventory_kpis
):

    metrics = {}

    metrics.update(
        timeline_kpis
    )

    metrics.update(
        procurement_kpis
    )

    metrics.update(
        printing_kpis
    )

    metrics.update(
        inventory_kpis
    )

    return metrics
