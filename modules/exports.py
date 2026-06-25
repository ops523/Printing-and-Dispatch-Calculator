# modules/exports.py

import io
import pandas as pd


def create_excel_export(
    summary_df,
    district_df,
    state_allocation_df,
    dispatch_schedule_df,
    dispatch_manifest_df,
    printing_plan_df,
    roll_summary_df,
    kpi_dashboard
):
    """
    Create Excel workbook and return bytes.
    """

    output = io.BytesIO()

    with pd.ExcelWriter(
        output,
        engine="xlsxwriter"
    ) as writer:

        # ---------------------------------
        # Campaign Summary
        # ---------------------------------

        summary_df.to_excel(
            writer,
            sheet_name="Campaign Summary",
            index=False
        )

        # ---------------------------------
        # District Allocation
        # ---------------------------------

        district_df.to_excel(
            writer,
            sheet_name="District Allocation",
            index=False
        )

        # ---------------------------------
        # State Allocation
        # ---------------------------------

        state_allocation_df.to_excel(
            writer,
            sheet_name="State Allocation",
            index=False
        )

        # ---------------------------------
        # Dispatch Schedule
        # ---------------------------------

        dispatch_schedule_df.to_excel(
            writer,
            sheet_name="Dispatch Schedule",
            index=False
        )

        # ---------------------------------
        # Dispatch Manifest
        # ---------------------------------

        dispatch_manifest_df.to_excel(
            writer,
            sheet_name="Dispatch Manifest",
            index=False
        )

        # ---------------------------------
        # Printing Plan
        # ---------------------------------

        printing_plan_df.to_excel(
            writer,
            sheet_name="Printing Plan",
            index=False
        )

        # ---------------------------------
        # Roll Summary
        # ---------------------------------

        roll_summary_df.to_excel(
            writer,
            sheet_name="Roll Summary",
            index=False
        )

        # ---------------------------------
        # KPI Dashboard
        # ---------------------------------

        kpi_df = pd.DataFrame(
            list(kpi_dashboard.items()),
            columns=["Metric", "Value"]
        )

        kpi_df.to_excel(
            writer,
            sheet_name="KPI Dashboard",
            index=False
        )

        # ---------------------------------
        # Formatting
        # ---------------------------------

        workbook = writer.book

        header_format = workbook.add_format({
            "bold": True,
            "border": 1
        })

        for sheet_name, df in {

            "Campaign Summary":
                summary_df,

            "District Allocation":
                district_df,

            "State Allocation":
                state_allocation_df,

            "Dispatch Schedule":
                dispatch_schedule_df,

            "Dispatch Manifest":
                dispatch_manifest_df,

            "Printing Plan":
                printing_plan_df,

            "Roll Summary":
                roll_summary_df,

            "KPI Dashboard":
                kpi_df

        }.items():

            worksheet = writer.sheets[
                sheet_name
            ]

            for col_num, value in enumerate(
                df.columns.values
            ):

                worksheet.write(
                    0,
                    col_num,
                    value,
                    header_format
                )

                worksheet.set_column(
                    col_num,
                    col_num,
                    max(
                        18,
                        len(str(value)) + 5
                    )
                )

    output.seek(0)

    return output.getvalue()


def build_kpi_dashboard(
    total_campaign_sqft,
    total_teams,
    daily_campaign_production,
    dispatch_media_qty,
    dispatch_gum_qty,
    total_dispatches,
    total_media_weight,
    total_running_feet,
    avg_printer_utilization
):
    """
    KPI dashboard dictionary.
    """

    return {

        "Total Campaign Sq Ft":
            round(total_campaign_sqft, 2),

        "Total Teams":
            total_teams,

        "Daily Production":
            round(
                daily_campaign_production,
                2
            ),

        "Media Per Dispatch":
            round(
                dispatch_media_qty,
                2
            ),

        "Gum Per Dispatch (Kg)":
            round(
                dispatch_gum_qty,
                2
            ),

        "Total Dispatches":
            total_dispatches,

        "Total Running Feet":
            round(
                total_running_feet,
                2
            ),

        "Total Media Weight (Kg)":
            round(
                total_media_weight,
                2
            ),

        "Average Printer Utilization %":
            round(
                avg_printer_utilization,
                2
            )

    }


def create_sample_upload_template():
    """
    Create sample deployment file
    for users to download.
    """

    sample_df = pd.DataFrame({

        "State": [

            "Maharashtra",
            "Karnataka",
            "Gujarat"

        ],

        "District": [

            "Pune",
            "Bengaluru",
            "Ahmedabad"

        ],

        "Teams": [

            5,
            4,
            6

        ]

    })

    output = io.BytesIO()

    with pd.ExcelWriter(
        output,
        engine="xlsxwriter"
    ) as writer:

        sample_df.to_excel(
            writer,
            sheet_name="Deployment",
            index=False
        )

    output.seek(0)

    return output.getvalue()
