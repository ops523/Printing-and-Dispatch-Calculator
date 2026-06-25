# modules/printing.py

import pandas as pd
from datetime import timedelta


def generate_printing_plan(
    dispatch_schedule_df,
    printing_lead_days,
    printer_capacity_per_day,
    media_width_ft,
    media_gsm
):
    """
    Generate printing plan from dispatch schedule.
    """

    rows = []

    for _, row in dispatch_schedule_df.iterrows():

        dispatch_no = row["Dispatch No"]

        dispatch_date = row["Dispatch Date"]

        media_qty = row["Media Qty (Sq Ft)"]

        print_start = (
            dispatch_date -
            timedelta(days=printing_lead_days)
        )

        print_days_required = max(
            1,
            round(
                media_qty /
                printer_capacity_per_day,
                2
            )
        )

        print_end = (
            dispatch_date -
            timedelta(days=1)
        )

        running_feet = calculate_running_feet(
            media_qty,
            media_width_ft
        )

        media_weight = calculate_media_weight(
            media_qty,
            media_gsm
        )

        utilization_pct = min(
            100,
            round(
                (
                    media_qty /
                    (
                        printer_capacity_per_day *
                        max(1, printing_lead_days)
                    )
                ) * 100,
                1
            )
        )

        rows.append({

            "Dispatch No":
                dispatch_no,

            "Print Start":
                print_start,

            "Print End":
                print_end,

            "Dispatch Date":
                dispatch_date,

            "Media Qty (Sq Ft)":
                round(media_qty, 2),

            "Running Feet":
                round(running_feet, 2),

            "Media Weight (Kg)":
                round(media_weight, 2),

            "Print Days Required":
                print_days_required,

            "Printer Utilization %":
                utilization_pct

        })

    return pd.DataFrame(rows)


def calculate_running_feet(
    media_sqft,
    media_width_ft
):
    """
    Running feet requirement.
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
    Media weight estimation.

    1 sqft = 0.092903 sqm
    """

    sqm = (
        media_sqft *
        0.092903
    )

    weight = (
        sqm *
        gsm
    ) / 1000

    return weight


def generate_daily_print_load(
    printing_plan_df,
    printer_capacity_per_day
):
    """
    Daily print load analysis.
    """

    rows = []

    for _, row in printing_plan_df.iterrows():

        media_qty = row[
            "Media Qty (Sq Ft)"
        ]

        required_days = (
            media_qty /
            printer_capacity_per_day
        )

        rows.append({

            "Dispatch No":
                row["Dispatch No"],

            "Media Qty":
                round(media_qty, 2),

            "Printer Capacity":
                printer_capacity_per_day,

            "Days Required":
                round(required_days, 2)

        })

    return pd.DataFrame(rows)


def generate_printer_loading_dashboard(
    printing_plan_df,
    printer_capacity_per_day
):
    """
    Printer KPI Summary.
    """

    total_media = (
        printing_plan_df[
            "Media Qty (Sq Ft)"
        ]
        .sum()
    )

    avg_utilization = (
        printing_plan_df[
            "Printer Utilization %"
        ]
        .mean()
    )

    total_running_feet = (
        printing_plan_df[
            "Running Feet"
        ]
        .sum()
    )

    total_weight = (
        printing_plan_df[
            "Media Weight (Kg)"
        ]
        .sum()
    )

    return {

        "Total Media Qty":
            round(total_media, 2),

        "Printer Capacity/Day":
            printer_capacity_per_day,

        "Average Utilization %":
            round(avg_utilization, 2),

        "Total Running Feet":
            round(total_running_feet, 2),

        "Total Media Weight":
            round(total_weight, 2)

    }


def generate_roll_requirement(
    media_qty_sqft,
    media_width_ft,
    roll_length_ft
):
    """
    Estimate roll requirement.

    Example:
    Roll Length = 500 ft
    Width = 4 ft
    """

    if media_width_ft <= 0:
        return 0

    running_feet = (
        media_qty_sqft /
        media_width_ft
    )

    rolls = (
        running_feet /
        roll_length_ft
    )

    return round(
        rolls,
        2
    )


def build_roll_summary(
    printing_plan_df,
    media_width_ft,
    roll_length_ft
):
    """
    Roll consumption summary.
    """

    rows = []

    for _, row in (
        printing_plan_df.iterrows()
    ):

        rolls = generate_roll_requirement(

            row[
                "Media Qty (Sq Ft)"
            ],

            media_width_ft,

            roll_length_ft

        )

        rows.append({

            "Dispatch No":
                row["Dispatch No"],

            "Media Qty":
                row[
                    "Media Qty (Sq Ft)"
                ],

            "Rolls Required":
                rolls

        })

    return pd.DataFrame(rows)
