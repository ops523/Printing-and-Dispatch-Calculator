# modules/exports.py

import io
import pandas as pd


# --------------------------------------------------
# SAFE SHEET WRITER
# --------------------------------------------------

def write_sheet(
    writer,
    df,
    sheet_name
):
    """
    Write dataframe safely.
    """

    if df is None:
        return

    if len(df) == 0:
        return

    df.to_excel(
        writer,
        sheet_name=sheet_name[:31],
        index=False
    )


# --------------------------------------------------
# DASHBOARD SHEET
# --------------------------------------------------

def build_dashboard_sheet(
    dashboard_dict
):
    """
    Convert dashboard dictionary
    into dataframe.
    """

    rows = []

    for key, value in dashboard_dict.items():

        rows.append({

            "Metric": key,

            "Value": value

        })

    return pd.DataFrame(rows)


# --------------------------------------------------
# MAIN EXPORT FUNCTION
# --------------------------------------------------

def create_excel_export(
    team_plan_df=None,
    team_summary_df=None,
    district_summary_df=None,
    state_summary_df=None,
    team_loading_df=None,
    production_df=None,
    weekly_production_df=None,
    campaign_forecast_df=None,
    media_forecast_df=None,
    gum_forecast_df=None,
    dispatch_df=None,
    dispatch_calendar_df=None,
    arrival_calendar_df=None,
    print_schedule_df=None,
    daily_print_df=None,
    printer_loading_df=None,
    roll_procurement_df=None,
    gum_procurement_df=None,
    purchase_plan_df=None,
    roll_inventory_df=None,
    gum_inventory_df=None,
    po_tracker_df=None,
    stockout_df=None,
    reforecast_df=None,
    dashboard_dict=None
):
    """
    Create complete workbook.
    """

    output = io.BytesIO()

    with pd.ExcelWriter(
        output,
        engine="openpyxl"
    ) as writer:

        # ---------------------------------
        # MASTER DATA
        # ---------------------------------

        write_sheet(
            writer,
            team_plan_df,
            "Team Plan"
        )

        write_sheet(
            writer,
            team_summary_df,
            "Team Summary"
        )

        write_sheet(
            writer,
            district_summary_df,
            "District Summary"
        )

        write_sheet(
            writer,
            state_summary_df,
            "State Summary"
        )

        write_sheet(
            writer,
            team_loading_df,
            "Team Loading"
        )

        # ---------------------------------
        # PRODUCTION
        # ---------------------------------

        write_sheet(
            writer,
            production_df,
            "Production Plan"
        )

        write_sheet(
            writer,
            weekly_production_df,
            "Weekly Production"
        )

        write_sheet(
            writer,
            campaign_forecast_df,
            "Campaign Forecast"
        )

        write_sheet(
            writer,
            media_forecast_df,
            "Media Forecast"
        )

        write_sheet(
            writer,
            gum_forecast_df,
            "Gum Forecast"
        )

        # ---------------------------------
        # DISPATCH
        # ---------------------------------

        write_sheet(
            writer,
            dispatch_df,
            "Dispatch Plan"
        )

        write_sheet(
            writer,
            dispatch_calendar_df,
            "Dispatch Calendar"
        )

        write_sheet(
            writer,
            arrival_calendar_df,
            "Arrival Calendar"
        )

        # ---------------------------------
        # PRINTING
        # ---------------------------------

        write_sheet(
            writer,
            print_schedule_df,
            "Print Schedule"
        )

        write_sheet(
            writer,
            daily_print_df,
            "Daily Print Plan"
        )

        write_sheet(
            writer,
            printer_loading_df,
            "Printer Loading"
        )

        # ---------------------------------
        # PROCUREMENT
        # ---------------------------------

        write_sheet(
            writer,
            roll_procurement_df,
            "Roll Procurement"
        )

        write_sheet(
            writer,
            gum_procurement_df,
            "Gum Procurement"
        )

        write_sheet(
            writer,
            purchase_plan_df,
            "Purchase Plan"
        )

        # ---------------------------------
        # INVENTORY
        # ---------------------------------

        write_sheet(
            writer,
            roll_inventory_df,
            "Roll Inventory"
        )

        write_sheet(
            writer,
            gum_inventory_df,
            "Gum Inventory"
        )

        write_sheet(
            writer,
            po_tracker_df,
            "PO Tracker"
        )

        write_sheet(
            writer,
            stockout_df,
            "Stockout Forecast"
        )

        # ---------------------------------
        # REFORECAST
        # ---------------------------------

        write_sheet(
            writer,
            reforecast_df,
            "Reforecast"
        )

        # ---------------------------------
        # DASHBOARD
        # ---------------------------------

        if dashboard_dict:

            dashboard_df = (
                build_dashboard_sheet(
                    dashboard_dict
                )
            )

            write_sheet(
                writer,
                dashboard_df,
                "Dashboard"
            )

    output.seek(0)

    return output


# --------------------------------------------------
# DOWNLOAD BUTTON HELPER
# --------------------------------------------------

def get_excel_download_data(
    excel_buffer
):
    """
    Returns binary data
    for st.download_button()
    """

    return excel_buffer.getvalue()


# --------------------------------------------------
# CONSOLIDATED KPI BUILDER
# --------------------------------------------------

def build_master_dashboard(
    project_summary=None,
    production_kpis=None,
    procurement_kpis=None,
    printing_kpis=None,
    inventory_kpis=None,
    reforecast_kpis=None
):
    """
    Consolidate all KPIs.
    """

    dashboard = {}

    for source in [

        project_summary,
        production_kpis,
        procurement_kpis,
        printing_kpis,
        inventory_kpis,
        reforecast_kpis

    ]:

        if source:

            dashboard.update(source)

    return dashboard
