# modules/teams.py

import pandas as pd
import math


# --------------------------------------------------
# VALIDATION
# --------------------------------------------------

def validate_team_plan(df):
    """
    Validate uploaded team planning file.
    """

    required_columns = [

        "Team Name",
        "Team Start Date",
        "State",
        "District",
        "Wall Count",
        "Avg Wall Size"

    ]

    missing = [

        col

        for col in required_columns

        if col not in df.columns

    ]

    if missing:

        return False, missing

    return True, []


# --------------------------------------------------
# PREPARE DATA
# --------------------------------------------------

def prepare_team_plan(df):
    """
    Standardize uploaded data.
    """

    working_df = df.copy()

    working_df["Team Start Date"] = pd.to_datetime(
        working_df["Team Start Date"]
    )

    working_df["District Sq Ft"] = (

        working_df["Wall Count"]

        *

        working_df["Avg Wall Size"]

    )

    return working_df


# --------------------------------------------------
# TEAM SUMMARY
# --------------------------------------------------

def build_team_summary(
    team_plan_df,
    target_sqft_per_day,
    efficiency_pct
):
    """
    Team level summary.
    """

    effective_productivity = (

        target_sqft_per_day

        *

        efficiency_pct

        / 100

    )

    grouped = (

        team_plan_df

        .groupby(
            "Team Name",
            as_index=False
        )

        .agg({

            "District Sq Ft": "sum",

            "Team Start Date": "min"

        })

    )

    grouped.rename(

        columns={

            "District Sq Ft":
                "Total Sq Ft"

        },

        inplace=True

    )

    grouped["Effective Productivity"] = (
        effective_productivity
    )

    grouped["Completion Days"] = (

        grouped["Total Sq Ft"]

        /

        effective_productivity

    )

    grouped["Completion Days"] = (

        grouped["Completion Days"]

        .apply(math.ceil)

    )

    grouped["Completion Date"] = (

        grouped["Team Start Date"]

        +

        pd.to_timedelta(

            grouped["Completion Days"],

            unit="D"

        )

    )

    return grouped


# --------------------------------------------------
# DISTRICT SUMMARY
# --------------------------------------------------

def build_district_summary(
    team_plan_df
):
    """
    District level summary.
    """

    district_df = (

        team_plan_df

        .groupby(

            [

                "State",
                "District"

            ],

            as_index=False

        )

        .agg({

            "Wall Count": "sum",

            "District Sq Ft": "sum"

        })

    )

    return district_df


# --------------------------------------------------
# PROJECT SUMMARY
# --------------------------------------------------

def build_project_summary(
    team_plan_df
):
    """
    Overall project summary.
    """

    total_walls = (

        team_plan_df["Wall Count"]

        .sum()

    )

    total_sqft = (

        team_plan_df["District Sq Ft"]

        .sum()

    )

    total_teams = (

        team_plan_df["Team Name"]

        .nunique()

    )

    summary = {

        "Total Teams":
            total_teams,

        "Total Walls":
            int(total_walls),

        "Total Sq Ft":
            round(total_sqft, 2)

    }

    return summary


# --------------------------------------------------
# ACTIVE TEAM LOADING
# --------------------------------------------------

def generate_team_loading(
    team_summary_df
):
    """
    Weekly active team loading.
    Useful for manpower planning.
    """

    rows = []

    project_start = (

        team_summary_df[
            "Team Start Date"
        ]

        .min()

    )

    project_end = (

        team_summary_df[
            "Completion Date"
        ]

        .max()

    )

    current_date = project_start

    week_no = 1

    while current_date <= project_end:

        week_end = (

            current_date +

            pd.Timedelta(days=6)

        )

        active_teams = (

            (

                team_summary_df[
                    "Team Start Date"
                ]

                <= week_end

            )

            &

            (

                team_summary_df[
                    "Completion Date"
                ]

                >= current_date

            )

        ).sum()

        rows.append({

            "Week":
                week_no,

            "Week Start":
                current_date,

            "Week End":
                week_end,

            "Active Teams":
                int(active_teams)

        })

        current_date = (

            current_date +

            pd.Timedelta(days=7)

        )

        week_no += 1

    return pd.DataFrame(rows)


# --------------------------------------------------
# STATE SUMMARY
# --------------------------------------------------

def build_state_summary(
    team_plan_df
):
    """
    State wise summary.
    """

    state_df = (

        team_plan_df

        .groupby(
            "State",
            as_index=False
        )

        .agg({

            "Wall Count": "sum",

            "District Sq Ft": "sum"

        })

    )

    state_df.rename(

        columns={

            "District Sq Ft":
                "Total Sq Ft"

        },

        inplace=True

    )

    return state_df


# --------------------------------------------------
# TEAM DISTRICT MATRIX
# --------------------------------------------------

def build_team_district_matrix(
    team_plan_df
):
    """
    Useful for operations visibility.
    """

    matrix = (

        team_plan_df

        .pivot_table(

            index="Team Name",

            columns="District",

            values="Wall Count",

            aggfunc="sum",

            fill_value=0

        )

    )

    return matrix.reset_index()
