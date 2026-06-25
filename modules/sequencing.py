# modules/sequencing.py

import pandas as pd
import math


# --------------------------------------------------
# VALIDATE SEQUENCE FILE
# --------------------------------------------------

def validate_sequence_columns(df):

    required = [

        "Team Name",
        "Team Start Date",
        "Sequence",
        "State",
        "District",
        "Wall Count",
        "Avg Wall Size",
        "Transit Days"

    ]

    missing = [

        col

        for col in required

        if col not in df.columns

    ]

    if missing:

        return False, missing

    return True, []


# --------------------------------------------------
# DISTRICT SQ FT
# --------------------------------------------------

def prepare_sequence_plan(df):

    working = df.copy()

    working["Team Start Date"] = pd.to_datetime(
        working["Team Start Date"]
    )

    working["District Sq Ft"] = (

        working["Wall Count"]

        *

        working["Avg Wall Size"]

    )

    return working


# --------------------------------------------------
# BUILD DISTRICT TIMELINE
# --------------------------------------------------

def build_district_timeline(
    team_plan_df,
    productivity_per_day
):

    rows = []

    teams = team_plan_df["Team Name"].unique()

    for team in teams:

        team_df = (

            team_plan_df[
                team_plan_df["Team Name"] == team
            ]

            .sort_values("Sequence")

            .copy()

        )

        current_start = (
            team_df["Team Start Date"]
            .min()
        )

        for _, row in team_df.iterrows():

            district_sqft = row["District Sq Ft"]

            production_days = math.ceil(

                district_sqft

                /

                productivity_per_day

            )

            district_finish = (

                current_start

                +

                pd.Timedelta(
                    days=production_days
                )

            )

            rows.append({

                "Team Name":
                    team,

                "Sequence":
                    row["Sequence"],

                "State":
                    row["State"],

                "District":
                    row["District"],

                "Wall Count":
                    row["Wall Count"],

                "District Sq Ft":
                    district_sqft,

                "Transit Days":
                    row["Transit Days"],

                "District Start":
                    current_start,

                "District Finish":
                    district_finish,

                "Production Days":
                    production_days

            })

            current_start = (

                district_finish

                +

                pd.Timedelta(
                    days=row["Transit Days"]
                )

            )

    return pd.DataFrame(rows)


# --------------------------------------------------
# TEAM COMPLETION SUMMARY
# --------------------------------------------------

def build_team_completion_summary(
    district_timeline_df
):

    summary = (

        district_timeline_df

        .groupby(
            "Team Name",
            as_index=False
        )

        .agg({

            "District Sq Ft":
                "sum",

            "District Start":
                "min",

            "District Finish":
                "max"

        })

    )

    summary.rename(

        columns={

            "District Sq Ft":
                "Total Sq Ft",

            "District Start":
                "Project Start",

            "District Finish":
                "Project Finish"

        },

        inplace=True

    )

    summary["Duration Days"] = (

        summary["Project Finish"]

        -

        summary["Project Start"]

    ).dt.days

    return summary


# --------------------------------------------------
# DISTRICT COMPLETION CALENDAR
# --------------------------------------------------

def build_district_completion_calendar(
    district_timeline_df
):

    calendar = (

        district_timeline_df[

            [

                "Team Name",
                "District",
                "District Finish"

            ]

        ]

        .sort_values(
            "District Finish"
        )

    )

    return calendar


# --------------------------------------------------
# ACTIVE TEAM LOADING
# --------------------------------------------------

def build_weekly_team_loading(
    district_timeline_df
):

    project_start = (

        district_timeline_df[
            "District Start"
        ]

        .min()

    )

    project_end = (

        district_timeline_df[
            "District Finish"
        ]

        .max()

    )

    rows = []

    current = project_start

    week_no = 1

    while current <= project_end:

        week_end = (

            current +

            pd.Timedelta(days=6)

        )

        active_teams = (

            district_timeline_df[

                (

                    district_timeline_df[
                        "District Start"
                    ]

                    <= week_end

                )

                &

                (

                    district_timeline_df[
                        "District Finish"
                    ]

                    >= current

                )

            ]

            ["Team Name"]

            .nunique()

        )

        rows.append({

            "Week":
                week_no,

            "Week Start":
                current,

            "Week End":
                week_end,

            "Active Teams":
                active_teams

        })

        current += pd.Timedelta(days=7)

        week_no += 1

    return pd.DataFrame(rows)


# --------------------------------------------------
# TEAM MOVEMENT PLAN
# --------------------------------------------------

def build_team_movement_plan(
    district_timeline_df
):

    rows = []

    for team in district_timeline_df[
        "Team Name"
    ].unique():

        team_df = (

            district_timeline_df[
                district_timeline_df[
                    "Team Name"
                ] == team
            ]

            .sort_values("Sequence")

        )

        for i in range(
            len(team_df) - 1
        ):

            current_row = (
                team_df.iloc[i]
            )

            next_row = (
                team_df.iloc[i + 1]
            )

            rows.append({

                "Team Name":
                    team,

                "From District":
                    current_row["District"],

                "To District":
                    next_row["District"],

                "Move Date":
                    current_row[
                        "District Finish"
                    ],

                "Transit Days":
                    current_row[
                        "Transit Days"
                    ]

            })

    return pd.DataFrame(rows)


# --------------------------------------------------
# PROJECT TIMELINE KPI
# --------------------------------------------------

def build_timeline_kpis(
    district_timeline_df
):

    project_start = (

        district_timeline_df[
            "District Start"
        ]

        .min()

    )

    project_end = (

        district_timeline_df[
            "District Finish"
        ]

        .max()

    )

    duration = (
        project_end -
        project_start
    ).days

    teams = (

        district_timeline_df[
            "Team Name"
        ]

        .nunique()

    )

    districts = len(
        district_timeline_df
    )

    sqft = (

        district_timeline_df[
            "District Sq Ft"
        ]

        .sum()

    )

    return {

        "Project Start":
            project_start,

        "Project End":
            project_end,

        "Project Duration":
            duration,

        "Total Teams":
            teams,

        "Total Districts":
            districts,

        "Total Sq Ft":
            round(sqft, 2)

    }
