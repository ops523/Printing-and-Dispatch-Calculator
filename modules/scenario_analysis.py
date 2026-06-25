import pandas as pd


def dispatch_cycle_comparison(
    daily_campaign_production,
    total_campaign_sqft,
    gum_per_1000_sqft
):

    rows = []

    for cycle in [7, 8, 9, 10]:

        media_qty = (
            daily_campaign_production *
            cycle
        )

        gum_qty = (
            media_qty /
            1000
        ) * gum_per_1000_sqft

        dispatches = round(
            total_campaign_sqft /
            media_qty
        )

        rows.append({

            "Dispatch Cycle":
                cycle,

            "Dispatches":
                dispatches,

            "Media/Dispatch":
                round(media_qty, 2),

            "Gum/Dispatch":
                round(gum_qty, 2)

        })

    return pd.DataFrame(rows)
