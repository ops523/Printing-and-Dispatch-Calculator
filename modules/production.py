# modules/production.py

import pandas as pd
import math


# --------------------------------------------------
# EFFECTIVE PRODUCTIVITY
# --------------------------------------------------

def calculate_real_productivity(
    target_sqft_per_day,
    efficiency_pct=85,
    travel_days_per_month=5
):
    """
    Real-world productivity.

    Incorporates:
    - Team efficiency
    - Travel/non-production days
    """

    efficiency_factor = (
        efficiency_pct / 100
    )

    working_factor = (
        (30 - travel_days_per_month)
        / 30
    )

    productivity = (

        target_sqft_per_day

        *

        efficiency_factor

        *

        working_factor

    )

    return productivity


# --------------------------------------------------
# TEAM PRODUCTION PLAN
# --------------------------------------------------

def build_team_production_plan(
    team_summary_df,
    target_sqft_per_day,
    efficiency_pct=85,
    travel_days_per_month=5
):
    """
    Calculate realistic completion dates.
    """

    productivity = (
        calculate_real_productivity(
            target_sqft_per_day,
            efficiency_pct,
            travel_days_per_month
        )
    )

    df = team_summary_df.copy()

    df["Real Productivity"] = (
        productivity
    )

    df["Real Completion Days"] = (

        df["Total Sq Ft"]

        /

        productivity

    ).apply(math.ceil)

    df["Projected Completion Date"] = (

        df["Team Start Date"]

        +

        pd.to_timedelta(

            df["Real Completion Days"],

            unit="D"

        )

    )

    return df


# --------------------------------------------------
# WEEKLY PRODUCTION FORECAST
# --------------------------------------------------

def generate_weekly_production_forecast(
    team_production_df,
    target_sqft_per_day,
    efficiency_pct=85,
    travel_days_per_month=5
):
    """
    Weekly production requirement
    by team.
    """

    productivity = (
        calculate_real_productivity(
            target_sqft_per_day,
            efficiency_pct,
            travel_days_per_month
        )
    )

    rows = []

    for _, row in team_production_df.iterrows():

        team = row["Team Name"]

        start_date = row["Team Start Date"]

        completion_date = row[
            "Projected Completion Date"
        ]

        remaining_sqft = row[
            "Total Sq Ft"
        ]

        week_no = 1

        current_date = start_date

        while (
            remaining_sqft > 0
        ):

            weekly_capacity = (
                productivity * 7
            )

            weekly_production = min(
                remaining_sqft,
                weekly_capacity
            )

            rows.append({

                "Team Name":
                    team,

                "Week":
                    week_no,

                "Week Start":
                    current_date,

                "Week End":
                    current_date +
                    pd.Timedelta(days=6),

                "Planned Sq Ft":
                    round(
                        weekly_production,
                        2
                    )

            })

            remaining_sqft -= (
                weekly_production
            )

            current_date += (
                pd.Timedelta(days=7)
            )

            week_no += 1

            if current_date > completion_date:
                break

    return pd.DataFrame(rows)


# --------------------------------------------------
# WEEKLY CAMPAIGN FORECAST
# --------------------------------------------------

def build_campaign_weekly_forecast(
    weekly_production_df
):
    """
    Combined weekly production.
    """

    forecast = (

        weekly_production_df

        .groupby(
            "Week",
            as_index=False
        )

        .agg({

            "Planned Sq Ft":
                "sum"

        })

    )

    forecast.rename(

        columns={

            "Planned Sq Ft":
                "Campaign Sq Ft"

        },

        inplace=True

    )

    return forecast


# --------------------------------------------------
# MEDIA FORECAST
# --------------------------------------------------

def generate_weekly_media_forecast(
    campaign_forecast_df,
    wastage_pct=12
):
    """
    Printing requirement.
    Includes wastage.
    """

    df = campaign_forecast_df.copy()

    df["Media Requirement"] = (

        df["Campaign Sq Ft"]

        *

        (
            1 +
            wastage_pct / 100
        )

    )

    return df


# --------------------------------------------------
# GUM FORECAST
# --------------------------------------------------

def generate_weekly_gum_forecast(
    media_forecast_df,
    gum_per_1000_sqft=5
):
    """
    Weekly gum consumption.
    """

    df = media_forecast_df.copy()

    df["Gum Required (Kg)"] = (

        df["Campaign Sq Ft"]

        /

        1000

        *

        gum_per_1000_sqft

    )

    return df


# --------------------------------------------------
# ACTIVE TEAM FORECAST
# --------------------------------------------------

def build_active_team_forecast(
    weekly_production_df
):
    """
    Weekly active team count.
    """

    active = (

        weekly_production_df

        .groupby(
            "Week",
            as_index=False
        )

        .agg({

            "Team Name":
                "nunique"

        })

    )

    active.rename(

        columns={

            "Team Name":
                "Active Teams"

        },

        inplace=True

    )

    return active


# --------------------------------------------------
# PRODUCTION KPI
# --------------------------------------------------

def build_production_kpis(
    team_production_df,
    campaign_weekly_df,
    media_forecast_df,
    gum_forecast_df
):
    """
    Dashboard metrics.
    """

    total_sqft = (

        team_production_df[
            "Total Sq Ft"
        ]

        .sum()

    )

    total_media = (

        media_forecast_df[
            "Media Requirement"
        ]

        .sum()

    )

    total_gum = (

        gum_forecast_df[
            "Gum Required (Kg)"
        ]

        .sum()

    )

    project_start = (

        team_production_df[
            "Team Start Date"
        ]

        .min()

    )

    project_end = (

        team_production_df[
            "Projected Completion Date"
        ]

        .max()

    )

    duration_days = (
        project_end -
        project_start
    ).days

    return {

        "Total Sq Ft":
            round(total_sqft, 2),

        "Total Media Required":
            round(total_media, 2),

        "Total Gum Required":
            round(total_gum, 2),

        "Project Duration":
            duration_days

    }
