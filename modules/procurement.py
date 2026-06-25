# modules/procurement.py

import pandas as pd
import math


# --------------------------------------------------
# MEDIA ROLL REQUIREMENT
# --------------------------------------------------

def calculate_roll_requirement(
    media_sqft,
    roll_capacity_sqft=1250
):
    """
    Rolls required.
    Always rounded up.
    """

    return math.ceil(
        media_sqft /
        roll_capacity_sqft
    )


# --------------------------------------------------
# WEEKLY ROLL PLAN
# --------------------------------------------------

def generate_roll_procurement_plan(
    media_forecast_df,
    roll_capacity_sqft=1250,
    roll_lead_time_days=3
):
    """
    Weekly media roll ordering plan.
    """

    rows = []

    for _, row in media_forecast_df.iterrows():

        media_required = row[
            "Media Requirement"
        ]

        rolls_required = (
            calculate_roll_requirement(
                media_required,
                roll_capacity_sqft
            )
        )

        week_start = row[
            "Week Start"
        ]

        order_date = (
            week_start -
            pd.Timedelta(
                days=roll_lead_time_days
            )
        )

        rows.append({

            "Week":
                row["Week"],

            "Week Start":
                week_start,

            "Media Requirement":
                round(
                    media_required,
                    2
                ),

            "Rolls Required":
                rolls_required,

            "Roll Order Date":
                order_date

        })

    return pd.DataFrame(rows)


# --------------------------------------------------
# WEEKLY GUM PLAN
# --------------------------------------------------

def generate_gum_procurement_plan(
    gum_forecast_df,
    gum_lead_time_days=7
):
    """
    Weekly gum ordering plan.
    """

    rows = []

    for _, row in gum_forecast_df.iterrows():

        gum_required = row[
            "Gum Required (Kg)"
        ]

        week_start = row[
            "Week Start"
        ]

        order_date = (
            week_start -
            pd.Timedelta(
                days=gum_lead_time_days
            )
        )

        rows.append({

            "Week":
                row["Week"],

            "Week Start":
                week_start,

            "Gum Required (Kg)":
                round(
                    gum_required,
                    2
                ),

            "Gum Order Date":
                order_date

        })

    return pd.DataFrame(rows)


# --------------------------------------------------
# ROLL INVENTORY
# --------------------------------------------------

def build_roll_inventory_plan(
    roll_plan_df,
    opening_roll_stock
):
    """
    Roll inventory projection.
    """

    rows = []

    stock = opening_roll_stock

    for _, row in roll_plan_df.iterrows():

        opening = stock

        consumed = row[
            "Rolls Required"
        ]

        closing = (
            opening -
            consumed
        )

        reorder = 0

        if closing < 0:

            reorder = abs(
                closing
            )

            closing = 0

        rows.append({

            "Week":
                row["Week"],

            "Opening Stock":
                opening,

            "Consumption":
                consumed,

            "Reorder Qty":
                reorder,

            "Closing Stock":
                closing

        })

        stock = closing

    return pd.DataFrame(rows)


# --------------------------------------------------
# GUM INVENTORY
# --------------------------------------------------

def build_gum_inventory_plan(
    gum_plan_df,
    opening_gum_stock
):
    """
    Gum inventory projection.
    """

    rows = []

    stock = opening_gum_stock

    for _, row in gum_plan_df.iterrows():

        opening = stock

        consumed = row[
            "Gum Required (Kg)"
        ]

        closing = (
            opening -
            consumed
        )

        reorder = 0

        if closing < 0:

            reorder = abs(
                closing
            )

            closing = 0

        rows.append({

            "Week":
                row["Week"],

            "Opening Stock":
                round(opening, 2),

            "Consumption":
                round(consumed, 2),

            "Reorder Qty":
                round(reorder, 2),

            "Closing Stock":
                round(closing, 2)

        })

        stock = closing

    return pd.DataFrame(rows)


# --------------------------------------------------
# CONSOLIDATED PURCHASE PLAN
# --------------------------------------------------

def build_purchase_plan(
    roll_plan_df,
    gum_plan_df
):
    """
    Combined procurement plan.
    """

    purchase_rows = []

    for _, row in roll_plan_df.iterrows():

        purchase_rows.append({

            "Order Type":
                "Media Roll",

            "Week":
                row["Week"],

            "Order Date":
                row["Roll Order Date"],

            "Quantity":
                row["Rolls Required"]

        })

    for _, row in gum_plan_df.iterrows():

        purchase_rows.append({

            "Order Type":
                "Gum",

            "Week":
                row["Week"],

            "Order Date":
                row["Gum Order Date"],

            "Quantity":
                row["Gum Required (Kg)"]

        })

    purchase_df = pd.DataFrame(
        purchase_rows
    )

    purchase_df = (
        purchase_df
        .sort_values(
            "Order Date"
        )
        .reset_index(drop=True)
    )

    return purchase_df


# --------------------------------------------------
# PROCUREMENT KPI
# --------------------------------------------------

def build_procurement_kpis(
    roll_plan_df,
    gum_plan_df
):
    """
    Procurement dashboard metrics.
    """

    total_rolls = (

        roll_plan_df[
            "Rolls Required"
        ]

        .sum()

    )

    total_media = (

        roll_plan_df[
            "Media Requirement"
        ]

        .sum()

    )

    total_gum = (

        gum_plan_df[
            "Gum Required (Kg)"
        ]

        .sum()

    )

    return {

        "Total Rolls Required":
            int(total_rolls),

        "Total Media Requirement":
            round(total_media, 2),

        "Total Gum Requirement":
            round(total_gum, 2)

    }


# --------------------------------------------------
# WEEKLY SUPPLY SNAPSHOT
# --------------------------------------------------

def build_weekly_supply_snapshot(
    roll_plan_df,
    gum_plan_df
):
    """
    Weekly supply dashboard.
    """

    snapshot = pd.merge(

        roll_plan_df[

            [
                "Week",
                "Rolls Required",
                "Media Requirement"
            ]

        ],

        gum_plan_df[

            [
                "Week",
                "Gum Required (Kg)"
            ]

        ],

        on="Week",

        how="left"

    )

    return snapshot
