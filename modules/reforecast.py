# modules/reforecast.py

import pandas as pd
import math


# --------------------------------------------------
# REMAINING CAMPAIGN
# --------------------------------------------------

def calculate_remaining_campaign(
    total_campaign_sqft,
    completed_sqft
):
    """
    Remaining project work.
    """

    remaining = max(
        total_campaign_sqft - completed_sqft,
        0
    )

    pct_complete = 0

    if total_campaign_sqft > 0:

        pct_complete = (
            completed_sqft
            / total_campaign_sqft
            * 100
        )

    return {

        "Total Campaign Sq Ft":
            round(total_campaign_sqft, 2),

        "Completed Sq Ft":
            round(completed_sqft, 2),

        "Remaining Sq Ft":
            round(remaining, 2),

        "Completion %":
            round(pct_complete, 2)

    }


# --------------------------------------------------
# AVAILABLE MEDIA
# --------------------------------------------------

def calculate_available_media(
    rolls_in_warehouse,
    media_in_field_sqft,
    roll_size_sqft=1250
):
    """
    Total available media.
    """

    warehouse_media = (
        rolls_in_warehouse
        * roll_size_sqft
    )

    total_media = (
        warehouse_media
        + media_in_field_sqft
    )

    return {

        "Warehouse Media Sq Ft":
            round(warehouse_media, 2),

        "Field Media Sq Ft":
            round(media_in_field_sqft, 2),

        "Total Available Media":
            round(total_media, 2)

    }


# --------------------------------------------------
# AVAILABLE GUM
# --------------------------------------------------

def calculate_available_gum(
    gum_in_warehouse,
    gum_in_field
):
    """
    Total available gum.
    """

    total = (
        gum_in_warehouse
        + gum_in_field
    )

    return {

        "Warehouse Gum":
            round(gum_in_warehouse, 2),

        "Field Gum":
            round(gum_in_field, 2),

        "Total Available Gum":
            round(total, 2)

    }


# --------------------------------------------------
# REMAINING PROCUREMENT
# --------------------------------------------------

def calculate_remaining_procurement(
    remaining_sqft,
    available_media_sqft,
    available_gum_kg,
    wastage_pct=12,
    gum_per_1000_sqft=5,
    roll_size_sqft=1250
):
    """
    Revised procurement requirement.
    """

    media_required = (

        remaining_sqft

        *

        (1 + wastage_pct / 100)

    )

    net_media_required = max(
        media_required
        - available_media_sqft,
        0
    )

    gum_required = (
        remaining_sqft
        / 1000
        * gum_per_1000_sqft
    )

    net_gum_required = max(
        gum_required
        - available_gum_kg,
        0
    )

    rolls_required = math.ceil(
        net_media_required
        / roll_size_sqft
    )

    return {

        "Remaining Media Required":
            round(media_required, 2),

        "Net Media To Procure":
            round(net_media_required, 2),

        "Rolls To Procure":
            int(rolls_required),

        "Remaining Gum Required":
            round(gum_required, 2),

        "Net Gum To Procure":
            round(net_gum_required, 2)

    }


# --------------------------------------------------
# TEAM REFORECAST
# --------------------------------------------------

def build_team_reforecast(
    team_production_df,
    current_date
):
    """
    Identify active and pending teams.
    """

    df = team_production_df.copy()

    current_date = pd.to_datetime(
        current_date
    )

    df["Status"] = "Pending"

    df.loc[
        (
            df["Team Start Date"]
            <= current_date
        )
        &
        (
            df["Projected Completion Date"]
            >= current_date
        ),
        "Status"
    ] = "Active"

    df.loc[
        (
            df["Projected Completion Date"]
            < current_date
        ),
        "Status"
    ] = "Completed"

    return df


# --------------------------------------------------
# FUTURE DISPATCH FILTER
# --------------------------------------------------

def filter_future_dispatches(
    dispatch_df,
    current_date
):
    """
    Keep only future dispatches.
    """

    current_date = pd.to_datetime(
        current_date
    )

    return dispatch_df[
        dispatch_df[
            "Dispatch Date"
        ] >= current_date
    ].copy()


# --------------------------------------------------
# FUTURE PURCHASE FILTER
# --------------------------------------------------

def filter_future_purchases(
    purchase_df,
    current_date
):
    """
    Keep only future POs.
    """

    current_date = pd.to_datetime(
        current_date
    )

    return purchase_df[
        purchase_df[
            "Order Date"
        ] >= current_date
    ].copy()


# --------------------------------------------------
# FUTURE PRINT FILTER
# --------------------------------------------------

def filter_future_print_schedule(
    print_schedule_df,
    current_date
):
    """
    Keep only future printing.
    """

    current_date = pd.to_datetime(
        current_date
    )

    return print_schedule_df[
        print_schedule_df[
            "Print End"
        ] >= current_date
    ].copy()


# --------------------------------------------------
# REVISED PROJECT END DATE
# --------------------------------------------------

def estimate_revised_completion(
    remaining_sqft,
    active_teams,
    productivity_per_team
):
    """
    Estimate remaining duration.
    """

    if active_teams <= 0:

        return {

            "Remaining Days":
                None,

            "Completion Date":
                None

        }

    daily_capacity = (
        active_teams
        * productivity_per_team
    )

    days_required = math.ceil(
        remaining_sqft
        / daily_capacity
    )

    completion_date = (
        pd.Timestamp.today()
        +
        pd.Timedelta(
            days=days_required
        )
    )

    return {

        "Remaining Days":
            int(days_required),

        "Completion Date":
            completion_date
        .date()
    }


# --------------------------------------------------
# REFORECAST DASHBOARD
# --------------------------------------------------

def build_reforecast_dashboard(
    campaign_summary,
    procurement_summary
):
    """
    Dashboard KPIs.
    """

    return {

        "Remaining Sq Ft":
            campaign_summary[
                "Remaining Sq Ft"
            ],

        "Completion %":
            campaign_summary[
                "Completion %"
            ],

        "Rolls To Procure":
            procurement_summary[
                "Rolls To Procure"
            ],

        "Net Gum To Procure":
            procurement_summary[
                "Net Gum To Procure"
            ]
    }


# --------------------------------------------------
# REFORECAST EXPORT DATA
# --------------------------------------------------

def build_reforecast_report(
    campaign_summary,
    media_summary,
    gum_summary,
    procurement_summary
):
    """
    Consolidated report.
    """

    rows = []

    for k, v in campaign_summary.items():

        rows.append({
            "Metric": k,
            "Value": v
        })

    for k, v in media_summary.items():

        rows.append({
            "Metric": k,
            "Value": v
        })

    for k, v in gum_summary.items():

        rows.append({
            "Metric": k,
            "Value": v
        })

    for k, v in procurement_summary.items():

        rows.append({
            "Metric": k,
            "Value": v
        })

    return pd.DataFrame(rows)
