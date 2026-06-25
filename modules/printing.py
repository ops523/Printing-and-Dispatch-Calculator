# modules/printing.py

import pandas as pd
import math


# --------------------------------------------------
# PRINT DAYS REQUIRED
# --------------------------------------------------

def calculate_print_days(
    media_qty_sqft,
    printer_capacity_per_day=20000
):
    """
    Number of printing days required.
    """

    return math.ceil(
        media_qty_sqft /
        printer_capacity_per_day
    )


# --------------------------------------------------
# PRINT SCHEDULE
# --------------------------------------------------

def generate_print_schedule(
    dispatch_schedule_df,
    printer_capacity_per_day=20000
):
    """
    Generate realistic print schedule.
    """

    rows = []

    for _, row in dispatch_schedule_df.iterrows():

        dispatch_no = row["Dispatch No"]

        dispatch_date = row["Dispatch Date"]

        media_qty = row[
            "Media Qty (Sq Ft)"
        ]

        print_days = calculate_print_days(
            media_qty,
            printer_capacity_per_day
        )

        print_end = (
            dispatch_date -
            pd.Timedelta(days=1)
        )

        print_start = (
            print_end -
            pd.Timedelta(
                days=print_days - 1
            )
        )

        rows.append({

            "Dispatch No":
                dispatch_no,

            "Media Qty (Sq Ft)":
                round(media_qty, 2),

            "Dispatch Date":
                dispatch_date,

            "Print Start":
                print_start,

            "Print End":
                print_end,

            "Print Days":
                print_days,

            "Printer Capacity":
                printer_capacity_per_day

        })

    return pd.DataFrame(rows)


# --------------------------------------------------
# DAILY PRINT PLAN
# --------------------------------------------------

def generate_daily_print_plan(
    print_schedule_df,
    printer_capacity_per_day=20000
):
    """
    Expand schedule into daily printing plan.
    """

    rows = []

    for _, row in print_schedule_df.iterrows():

        dispatch_no = row["Dispatch No"]

        media_qty = row[
            "Media Qty (Sq Ft)"
        ]

        start_date = row[
            "Print Start"
        ]

        end_date = row[
            "Print End"
        ]

        remaining_qty = media_qty

        current_date = start_date

        while current_date <= end_date:

            daily_qty = min(
                printer_capacity_per_day,
                remaining_qty
            )

            rows.append({

                "Print Date":
                    current_date,

                "Dispatch No":
                    dispatch_no,

                "Daily Print Qty":
                    round(
                        daily_qty,
                        2
                    )

            })

            remaining_qty -= daily_qty

            current_date += (
                pd.Timedelta(days=1)
            )

    return pd.DataFrame(rows)


# --------------------------------------------------
# PRINTER LOADING
# --------------------------------------------------

def generate_printer_loading(
    daily_print_df,
    printer_capacity_per_day=20000
):
    """
    Daily printer loading.
    """

    loading = (

        daily_print_df

        .groupby(
            "Print Date",
            as_index=False
        )

        .agg({

            "Daily Print Qty":
                "sum"

        })

    )

    loading["Capacity"] = (
        printer_capacity_per_day
    )

    loading["Utilization %"] = (

        loading[
            "Daily Print Qty"
        ]

        /

        printer_capacity_per_day

        *

        100

    ).round(1)

    loading["Over Capacity"] = (

        loading[
            "Daily Print Qty"
        ]

        >

        printer_capacity_per_day

    )

    return loading


# --------------------------------------------------
# CAPACITY CHECK
# --------------------------------------------------

def identify_capacity_conflicts(
    loading_df
):
    """
    Detect overloaded print days.
    """

    conflicts = loading_df[
        loading_df[
            "Over Capacity"
        ]
    ]

    return conflicts


# --------------------------------------------------
# WEEKLY PRINT FORECAST
# --------------------------------------------------

def generate_weekly_print_forecast(
    daily_print_df
):
    """
    Weekly printing requirement.
    """

    df = daily_print_df.copy()

    df["Week"] = (

        df["Print Date"]

        .dt.isocalendar()

        .week

    )

    weekly = (

        df

        .groupby(
            "Week",
            as_index=False
        )

        .agg({

            "Daily Print Qty":
                "sum"

        })

    )

    weekly.rename(

        columns={

            "Daily Print Qty":
                "Weekly Print Qty"

        },

        inplace=True

    )

    return weekly


# --------------------------------------------------
# PRINTING KPI
# --------------------------------------------------

def build_printing_kpis(
    print_schedule_df,
    loading_df
):
    """
    Printing dashboard metrics.
    """

    total_media = (

        print_schedule_df[
            "Media Qty (Sq Ft)"
        ]

        .sum()

    )

    total_dispatches = len(
        print_schedule_df
    )

    avg_utilization = (

        loading_df[
            "Utilization %"
        ]

        .mean()

    )

    max_utilization = (

        loading_df[
            "Utilization %"
        ]

        .max()

    )

    return {

        "Total Media Printed":
            round(total_media, 2),

        "Total Dispatches":
            total_dispatches,

        "Average Utilization %":
            round(avg_utilization, 1),

        "Peak Utilization %":
            round(max_utilization, 1)

    }


# --------------------------------------------------
# PRINT QUEUE VIEW
# --------------------------------------------------

def build_print_queue(
    print_schedule_df
):
    """
    Operations print queue.
    """

    queue = (

        print_schedule_df

        .sort_values(
            "Print Start"
        )

        .reset_index(
            drop=True
        )

    )

    return queue


# --------------------------------------------------
# ROLL REQUIREMENT
# --------------------------------------------------

def calculate_roll_requirement(
    media_qty_sqft,
    roll_size_sqft=1250
):
    """
    Rolls required.
    """

    return math.ceil(
        media_qty_sqft /
        roll_size_sqft
    )


# --------------------------------------------------
# PRINT MATERIAL PLAN
# --------------------------------------------------

def build_print_material_plan(
    print_schedule_df,
    roll_size_sqft=1250
):
    """
    Roll requirement by dispatch.
    """

    df = print_schedule_df.copy()

    df["Rolls Required"] = (

        df[
            "Media Qty (Sq Ft)"
        ]

        .apply(

            lambda x:
            calculate_roll_requirement(
                x,
                roll_size_sqft
            )

        )

    )

    return df
