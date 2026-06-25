# modules/inventory.py

import pandas as pd


# --------------------------------------------------
# MEDIA ROLL INVENTORY
# --------------------------------------------------

def build_roll_inventory_plan(
    roll_procurement_df,
    opening_roll_stock,
    safety_roll_stock=25,
    roll_lead_time_days=3
):
    """
    Weekly roll inventory tracking.
    """

    rows = []

    stock = opening_roll_stock

    for _, row in roll_procurement_df.iterrows():

        week = row["Week"]

        opening = stock

        consumption = row["Rolls Required"]

        receipt = row["Rolls Required"]

        closing = (
            opening +
            receipt -
            consumption
        )

        alert = ""

        if closing < safety_roll_stock:

            alert = "REORDER ALERT"

        if closing <= 0:

            alert = "STOCKOUT RISK"

        rows.append({

            "Week":
                week,

            "Opening Stock":
                opening,

            "Receipt":
                receipt,

            "Consumption":
                consumption,

            "Closing Stock":
                closing,

            "Safety Stock":
                safety_roll_stock,

            "Alert":
                alert

        })

        stock = closing

    return pd.DataFrame(rows)


# --------------------------------------------------
# GUM INVENTORY
# --------------------------------------------------

def build_gum_inventory_plan(
    gum_procurement_df,
    opening_gum_stock,
    safety_gum_stock=200
):
    """
    Weekly gum inventory tracking.
    """

    rows = []

    stock = opening_gum_stock

    for _, row in gum_procurement_df.iterrows():

        week = row["Week"]

        opening = stock

        consumption = row[
            "Gum Required (Kg)"
        ]

        receipt = row[
            "Gum Required (Kg)"
        ]

        closing = (
            opening +
            receipt -
            consumption
        )

        alert = ""

        if closing < safety_gum_stock:

            alert = "REORDER ALERT"

        if closing <= 0:

            alert = "STOCKOUT RISK"

        rows.append({

            "Week":
                week,

            "Opening Stock":
                round(opening, 2),

            "Receipt":
                round(receipt, 2),

            "Consumption":
                round(consumption, 2),

            "Closing Stock":
                round(closing, 2),

            "Safety Stock":
                safety_gum_stock,

            "Alert":
                alert

        })

        stock = closing

    return pd.DataFrame(rows)


# --------------------------------------------------
# PURCHASE ORDER TRACKER
# --------------------------------------------------

def build_purchase_order_tracker(
    purchase_plan_df,
    roll_lead_time_days=3,
    gum_lead_time_days=7
):
    """
    Track PO creation and arrival.
    """

    rows = []

    for _, row in purchase_plan_df.iterrows():

        item = row["Order Type"]

        order_date = row["Order Date"]

        qty = row["Quantity"]

        if item == "Media Roll":

            arrival_date = (

                order_date +

                pd.Timedelta(
                    days=roll_lead_time_days
                )

            )

        else:

            arrival_date = (

                order_date +

                pd.Timedelta(
                    days=gum_lead_time_days
                )

            )

        rows.append({

            "Item":
                item,

            "Quantity":
                qty,

            "Order Date":
                order_date,

            "Expected Arrival":
                arrival_date

        })

    return pd.DataFrame(rows)


# --------------------------------------------------
# INVENTORY DASHBOARD
# --------------------------------------------------

def build_inventory_dashboard(
    roll_inventory_df,
    gum_inventory_df
):
    """
    Dashboard KPIs.
    """

    current_roll_stock = (

        roll_inventory_df[
            "Closing Stock"
        ]

        .iloc[-1]

        if len(roll_inventory_df) > 0
        else 0

    )

    current_gum_stock = (

        gum_inventory_df[
            "Closing Stock"
        ]

        .iloc[-1]

        if len(gum_inventory_df) > 0
        else 0

    )

    roll_alerts = (

        roll_inventory_df[
            "Alert"
        ]

        != ""

    ).sum()

    gum_alerts = (

        gum_inventory_df[
            "Alert"
        ]

        != ""

    ).sum()

    return {

        "Closing Roll Stock":
            current_roll_stock,

        "Closing Gum Stock":
            current_gum_stock,

        "Roll Alerts":
            int(roll_alerts),

        "Gum Alerts":
            int(gum_alerts)

    }


# --------------------------------------------------
# STOCKOUT FORECAST
# --------------------------------------------------

def build_stockout_forecast(
    roll_inventory_df,
    gum_inventory_df
):
    """
    Predict stockout weeks.
    """

    stockout_rows = []

    roll_stockouts = roll_inventory_df[
        roll_inventory_df[
            "Closing Stock"
        ] <= 0
    ]

    gum_stockouts = gum_inventory_df[
        gum_inventory_df[
            "Closing Stock"
        ] <= 0
    ]

    for _, row in roll_stockouts.iterrows():

        stockout_rows.append({

            "Item":
                "Media Roll",

            "Week":
                row["Week"],

            "Issue":
                "Stockout"

        })

    for _, row in gum_stockouts.iterrows():

        stockout_rows.append({

            "Item":
                "Gum",

            "Week":
                row["Week"],

            "Issue":
                "Stockout"

        })

    return pd.DataFrame(stockout_rows)


# --------------------------------------------------
# RECEIPT CALENDAR
# --------------------------------------------------

def build_receipt_calendar(
    po_tracker_df
):
    """
    Incoming material calendar.
    """

    calendar = (

        po_tracker_df

        .groupby(
            "Expected Arrival",
            as_index=False
        )

        .agg({

            "Quantity":
                "sum"

        })

    )

    return calendar


# --------------------------------------------------
# INVENTORY MOVEMENT
# --------------------------------------------------

def build_inventory_movement(
    roll_inventory_df,
    gum_inventory_df
):
    """
    Combined inventory report.
    """

    roll_df = roll_inventory_df.copy()

    roll_df["Item"] = "Media Roll"

    gum_df = gum_inventory_df.copy()

    gum_df["Item"] = "Gum"

    movement = pd.concat(

        [

            roll_df,

            gum_df

        ],

        ignore_index=True

    )

    return movement
