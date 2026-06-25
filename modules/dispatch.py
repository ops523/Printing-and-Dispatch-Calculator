# modules/dispatch.py

import pandas as pd
from datetime import timedelta


def generate_dispatch_schedule(
    campaign_start_date,
    total_campaign_sqft,
    daily_campaign_production,
    dispatch_cycle_days,
    transit_days,
    arrival_buffer_days,
    gum_per_1000_sqft=5
):
    """
    Generate complete dispatch schedule.

    Logic:

    Dispatch Qty
    =
    Daily Production × Dispatch Cycle

    Replenishment Dispatch Date
    =
    Exhaustion Date
    -
    Arrival Buffer
    -
    Transit Time
    """

    dispatch_qty = (
        daily_campaign_production *
        dispatch_cycle_days
    )

    total_cycles = max(
        1,
        int(
            (
                total_campaign_sqft +
                dispatch_qty - 1
            ) // dispatch_qty
        )
    )

    rows = []

    remaining_sqft = total_campaign_sqft

    current_dispatch_date = campaign_start_date

    for dispatch_no in range(
        1,
        total_cycles + 1
    ):

        media_qty = min(
            dispatch_qty,
            remaining_sqft
        )

        gum_qty = (
            media_qty /
            1000
        ) * gum_per_1000_sqft

        arrival_date = (
            current_dispatch_date +
            timedelta(
                days=transit_days
            )
        )

        coverage_start = arrival_date

        coverage_end = (
            coverage_start +
            timedelta(
                days=dispatch_cycle_days
            )
        )

        exhaustion_date = coverage_end

        next_dispatch_trigger = (
            exhaustion_date -
            timedelta(
                days=arrival_buffer_days
            ) -
            timedelta(
                days=transit_days
            )
        )

        rows.append({

            "Dispatch No":
                dispatch_no,

            "Dispatch Date":
                current_dispatch_date,

            "Arrival Date":
                arrival_date,

            "Coverage Start":
                coverage_start,

            "Coverage End":
                coverage_end,

            "Media Exhaustion":
                exhaustion_date,

            "Next Dispatch Trigger":
                next_dispatch_trigger,

            "Media Qty (Sq Ft)":
                round(media_qty, 2),

            "Gum Qty (Kg)":
                round(gum_qty, 2)

        })

        remaining_sqft -= media_qty

        current_dispatch_date = (
            next_dispatch_trigger
        )

        if remaining_sqft <= 0:
            break

    return pd.DataFrame(rows)


def generate_dispatch_manifest(
    dispatch_schedule_df,
    state_allocation_df
):
    """
    Create detailed dispatch manifest
    for every dispatch cycle.
    """

    manifest_rows = []

    for _, dispatch in (
        dispatch_schedule_df.iterrows()
    ):

        dispatch_no = (
            dispatch["Dispatch No"]
        )

        dispatch_date = (
            dispatch["Dispatch Date"]
        )

        for _, state in (
            state_allocation_df.iterrows()
        ):

            manifest_rows.append({

                "Dispatch No":
                    dispatch_no,

                "Dispatch Date":
                    dispatch_date,

                "State":
                    state["State"],

                "Teams":
                    state["Teams"],

                "Media Qty (Sq Ft)":
                    state[
                        "Media Qty (Sq Ft)"
                    ],

                "Gum Qty (Kg)":
                    state[
                        "Gum Qty (Kg)"
                    ]

            })

    return pd.DataFrame(
        manifest_rows
    )


def calculate_field_inventory_days(
    dispatch_cycle_days,
    arrival_buffer_days
):
    """
    Inventory available at site.

    Example:

    Dispatch Cycle
    = 7 days

    Arrival Buffer
    = 2 days

    Inventory Coverage
    = 9 days
    """

    return (
        dispatch_cycle_days +
        arrival_buffer_days
    )


def generate_replenishment_calendar(
    dispatch_schedule_df
):
    """
    Simple replenishment calendar.
    Useful for dashboard view.
    """

    calendar_rows = []

    for _, row in (
        dispatch_schedule_df.iterrows()
    ):

        calendar_rows.append({

            "Date":
                row[
                    "Next Dispatch Trigger"
                ],

            "Activity":
                (
                    "Trigger Dispatch "
                    f"#{row['Dispatch No'] + 1}"
                )

        })

    return pd.DataFrame(
        calendar_rows
    )


def generate_dispatch_summary(
    dispatch_schedule_df
):
    """
    Dispatch KPI Summary.
    """

    total_dispatches = len(
        dispatch_schedule_df
    )

    total_media = (
        dispatch_schedule_df[
            "Media Qty (Sq Ft)"
        ]
        .sum()
    )

    total_gum = (
        dispatch_schedule_df[
            "Gum Qty (Kg)"
        ]
        .sum()
    )

    return {

        "Total Dispatches":
            total_dispatches,

        "Total Media":
            round(total_media, 2),

        "Total Gum":
            round(total_gum, 2)

    }
