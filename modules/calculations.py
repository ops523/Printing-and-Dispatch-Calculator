# modules/calculations.py

import math
import pandas as pd


def calculate_effective_productivity(
    target_sqft_per_team_day,
    efficiency_pct
):
    """
    Calculate effective daily production per team.
    """

    return (
        target_sqft_per_team_day *
        efficiency_pct / 100
    )


def calculate_total_teams(
    deployment_df
):
    """
    Sum total teams from uploaded deployment sheet.
    """

    return int(
        deployment_df["Teams"].sum()
    )


def calculate_daily_campaign_production(
    total_teams,
    effective_productivity
):
    """
    Total daily campaign production.
    """

    return (
        total_teams *
        effective_productivity
    )


def calculate_dispatch_requirement(
    daily_campaign_production,
    dispatch_cycle_days
):
    """
    Media requirement for one dispatch cycle.
    """

    return (
        daily_campaign_production *
        dispatch_cycle_days
    )


def calculate_gum_requirement(
    media_sqft,
    gum_per_1000_sqft=5
):
    """
    Gum requirement in KG.
    Default:
    5 KG per 1000 Sq Ft
    """

    return (
        media_sqft /
        1000
    ) * gum_per_1000_sqft


def calculate_media_running_feet(
    media_sqft,
    media_width_ft
):
    """
    Running feet calculation.
    """

    if media_width_ft <= 0:
        return 0

    return (
        media_sqft /
        media_width_ft
    )


def calculate_media_weight(
    media_sqft,
    gsm
):
    """
    Estimate media weight.

    Formula:
    1 Sq Ft = 0.092903 Sq Meter

    Weight(Kg)
    =
    Area Sq M × GSM / 1000
    """

    sqm = (
        media_sqft *
        0.092903
    )

    weight_kg = (
        sqm *
        gsm
    ) / 1000

    return weight_kg


def calculate_dispatch_weight(
    media_sqft,
    gsm,
    gum_qty
):
    """
    Total shipment weight.
    """

    media_weight = calculate_media_weight(
        media_sqft,
        gsm
    )

    total_weight = (
        media_weight +
        gum_qty
    )

    return (
        media_weight,
        total_weight
    )


def build_campaign_summary(
    campaign_name,
    total_sqft,
    total_teams,
    effective_productivity,
    daily_campaign_production,
    dispatch_cycle_days,
    dispatch_media_qty,
    gum_qty
):
    """
    Campaign summary dataframe.
    """

    summary = pd.DataFrame({

        "Metric": [

            "Campaign Name",

            "Total Campaign Sq Ft",

            "Total Teams",

            "Effective Productivity / Team / Day",

            "Daily Campaign Production",

            "Dispatch Cycle (Days)",

            "Media Per Dispatch",

            "Gum Per Dispatch"

        ],

        "Value": [

            campaign_name,

            round(total_sqft, 2),

            total_teams,

            round(
                effective_productivity,
                2
            ),

            round(
                daily_campaign_production,
                2
            ),

            dispatch_cycle_days,

            round(
                dispatch_media_qty,
                2
            ),

            round(
                gum_qty,
                2
            )

        ]

    })

    return summary


def build_state_allocation(
    deployment_df,
    effective_productivity,
    dispatch_cycle_days,
    gum_per_1000_sqft=5
):
    """
    State-wise media and gum allocation.
    """

    state_df = (

        deployment_df

        .groupby(
            "State",
            as_index=False
        )["Teams"]

        .sum()

    )

    allocations = []

    for _, row in state_df.iterrows():

        state = row["State"]

        teams = row["Teams"]

        media_qty = (

            teams *

            effective_productivity *

            dispatch_cycle_days

        )

        gum_qty = (

            media_qty /
            1000

        ) * gum_per_1000_sqft

        allocations.append({

            "State": state,

            "Teams": teams,

            "Media Qty (Sq Ft)": round(
                media_qty,
                2
            ),

            "Gum Qty (Kg)": round(
                gum_qty,
                2
            )

        })

    return pd.DataFrame(
        allocations
    )


def validate_deployment_file(
    deployment_df
):
    """
    Validate uploaded Excel file.
    Required columns:
    State
    District
    Teams
    """

    required_columns = [

        "State",
        "District",
        "Teams"

    ]

    missing = [

        col

        for col in required_columns

        if col not in deployment_df.columns

    ]

    if len(missing) > 0:

        return False, missing

    return True, []
