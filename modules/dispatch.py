# modules/dispatch.py

import pandas as pd
import math


# --------------------------------------------------
# TEAM DISPATCH REQUIREMENT
# --------------------------------------------------

def generate_team_dispatch_plan(
    team_production_df,
    dispatch_coverage_days=10,
    transit_days=3,
    arrival_buffer_days=2,
    wastage_pct=12,
    gum_per_1000_sqft=5
):
    """
    Dispatch plan by team.
    """

    rows = []

    for _, row in team_production_df.iterrows():

        team = row["Team Name"]

        start_date = row["Team Start Date"]

        completion_date = row[
            "Projected Completion Date"
        ]

        productivity = row[
            "Real Productivity"
        ]

        current_start = start_date

        dispatch_no = 1

        while current_start < completion_date:

            cycle_production = (
                productivity *
                dispatch_coverage_days
            )

            media_qty = (
                cycle_production *
                (1 + wastage_pct / 100)
            )

            gum_qty = (
                cycle_production /
                1000 *
                gum_per_1000_sqft
            )

            exhaustion_date = (
                current_start +
                pd.Timedelta(
                    days=dispatch_coverage_days
                )
            )

            required_arrival = (
                exhaustion_date -
                pd.Timedelta(
                    days=arrival_buffer_days
                )
            )

            dispatch_date = (
                required_arrival -
                pd.Timedelta(
                    days=transit_days
                )
            )

            rows.append({

                "Team Name":
                    team,

                "Dispatch No":
                    dispatch_no,

                "Cycle Start":
                    current_start,

                "Cycle End":
                    exhaustion_date,

                "Dispatch Date":
                    dispatch_date,

                "Required Arrival":
                    required_arrival,

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

            current_start = exhaustion_date

            dispatch_no += 1

    return pd.DataFrame(rows)


# --------------------------------------------------
# TEAM + DISTRICT DISPATCH
# --------------------------------------------------

def generate_team_district_dispatch_plan(
    team_plan_df,
    team_production_df,
    dispatch_coverage_days=10,
    transit_days=3,
    arrival_buffer_days=2,
    wastage_pct=12,
    gum_per_1000_sqft=5
):
    """
    Dispatch planning with district visibility.
    """

    dispatch_df = generate_team_dispatch_plan(
        team_production_df,
        dispatch_coverage_days,
        transit_days,
        arrival_buffer_days,
        wastage_pct,
        gum_per_1000_sqft
    )

    merged = dispatch_df.merge(

        team_plan_df[

            [
                "Team Name",
                "State",
                "District"
            ]

        ],

        on="Team Name",

        how="left"

    )

    return merged


# --------------------------------------------------
# DAILY DISPATCH CALENDAR
# --------------------------------------------------

def generate_dispatch_calendar(
    dispatch_df
):
    """
    Daily dispatch schedule.
    """

    calendar = (

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

    calendar.rename(

        columns={

            "Team Name":
                "Teams Covered"

        },

        inplace=True

    )

    return calendar


# --------------------------------------------------
# ARRIVAL CALENDAR
# --------------------------------------------------

def generate_arrival_calendar(
    dispatch_df
):
    """
    Material arrival calendar.
    """

    arrivals = (

        dispatch_df

        .groupby(
            "Required Arrival",
            as_index=False
        )

        .agg({

            "Media Qty (Sq Ft)":
                "sum",

            "Gum Qty (Kg)":
                "sum"

        })

    )

    return arrivals


# --------------------------------------------------
# TEAM MEDIA CONSUMPTION
# --------------------------------------------------

def generate_team_consumption_plan(
    team_production_df,
    gum_per_1000_sqft=5
):
    """
    Daily consumption rates.
    """

    df = team_production_df.copy()

    df["Daily Media Consumption"] = (
        df["Real Productivity"]
    )

    df["Daily Gum Consumption"] = (

        df["Real Productivity"]

        /

        1000

        *

        gum_per_1000_sqft

    )

    return df


# --------------------------------------------------
# FIELD INVENTORY REQUIREMENT
# --------------------------------------------------

def calculate_field_inventory_requirement(
    team_production_df,
    safety_days=2,
    gum_per_1000_sqft=5
):
    """
    Minimum inventory to keep at field.
    """

    rows = []

    for _, row in team_production_df.iterrows():

        daily_media = row[
            "Real Productivity"
        ]

        daily_gum = (

            daily_media /
            1000 *
            gum_per_1000_sqft

        )

        rows.append({

            "Team Name":
                row["Team Name"],

            "Safety Media":
                round(
                    daily_media *
                    safety_days,
                    2
                ),

            "Safety Gum":
                round(
                    daily_gum *
                    safety_days,
                    2
                )

        })

    return pd.DataFrame(rows)


# --------------------------------------------------
# DISPATCH SUMMARY
# --------------------------------------------------

def build_dispatch_summary(
    dispatch_df
):
    """
    High-level dispatch KPIs.
    """

    total_dispatches = len(
        dispatch_df
    )

    total_media = (

        dispatch_df[
            "Media Qty (Sq Ft)"
        ]

        .sum()

    )

    total_gum = (

        dispatch_df[
            "Gum Qty (Kg)"
        ]

        .sum()

    )

    first_dispatch = (

        dispatch_df[
            "Dispatch Date"
        ]

        .min()

    )

    last_dispatch = (

        dispatch_df[
            "Dispatch Date"
        ]

        .max()

    )

    return {

        "Total Dispatches":
            total_dispatches,

        "Total Media":
            round(total_media, 2),

        "Total Gum":
            round(total_gum, 2),

        "First Dispatch":
            first_dispatch,

        "Last Dispatch":
            last_dispatch

    }


# --------------------------------------------------
# WAREHOUSE DISPATCH LOAD
# --------------------------------------------------

def generate_warehouse_loading(
    dispatch_df
):
    """
    Daily warehouse loading.
    """

    warehouse = (

        dispatch_df

        .groupby(
            "Dispatch Date",
            as_index=False
        )

        .agg({

            "Media Qty (Sq Ft)":
                "sum",

            "Gum Qty (Kg)":
                "sum"

        })

    )

    return warehouse


# --------------------------------------------------
# TEAM EXHAUSTION TRACKER
# --------------------------------------------------

def generate_exhaustion_tracker(
    dispatch_df
):
    """
    Track when teams run out of stock.
    """

    tracker = dispatch_df[

        [

            "Team Name",
            "Dispatch No",
            "Cycle End"

        ]

    ].copy()

    tracker.rename(

        columns={

            "Cycle End":
                "Expected Exhaustion"

        },

        inplace=True

    )

    return tracker
