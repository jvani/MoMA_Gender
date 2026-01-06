import pandas as pd
import datetime as dt

import matplotlib.pyplot as plt

output = "./output/moma-{}-summary.csv"

if __name__ == "__main__":
    # Read CSV files
    artists = pd.read_csv("./data/artists.csv", index_col=["Artist ID"])
    artworks = pd.read_csv("./data/artworks.csv", index_col=["Artwork ID"]).dropna(
        subset=["Date"]
    )

    # Extract and transform relevant data
    artists["gender"] = artists.Gender.str.lower()
    artworks["year"] = artworks["Date"].str.extract(r"(\d{4})").fillna(0).astype(int)
    artworks["acquired"] = (
        artworks["Acquisition Date"].str.extract(r"(\d{4})").fillna(0).astype(int)
    )

    # Merge datasets
    df = pd.merge(artworks, artists, on="Name")

    # Aggregate data and write to CSV
    (
        df[(2016 >= df.acquired) & (df.acquired >= 1900)]
        .groupby(["acquired", "gender"])
        .size()
        .unstack(1)
        .fillna(0)
        .to_csv(output.format("acquisition"))
    )

    (
        df[(2016 >= df.year) & (df.year >= 1900)]
        .groupby(["year", "gender"])
        .size()
        .unstack(1)
        .fillna(0)
        .to_csv(output.format("artwork"))
    )

    # Plot data with Matplotlib
    for dataset in ("acquisition", "artwork"):
        fig, (ax1) = plt.subplots(nrows=1, ncols=1, figsize=(18, 4))

        # Format plot: hide tick marks and keep axes on bottom/left only.
        ax1.tick_params(top=False, bottom=False, left=False, right=False)
        ax1.xaxis.set_ticks_position("bottom")
        ax1.yaxis.set_ticks_position("left")

        for spine in fig.gca().spines.values():
            spine.set_visible(False)

        ax1.set_ylabel(
            "Percent of MoMA Acquisitions"
            if dataset == "acquisition"
            else "Percent of MoMA Artwork"
        )
        ax1.set_xlabel(
            "Acquisition Year" if dataset == "acquisition" else "Production Year"
        )
        ax1.set_title(
            "Percent of MoMA Acquisitions by Year"
            if dataset == "acquisition"
            else "Percent of MoMA Artwork by Production Year"
        )

        # Plot acquisition percentages as stacked bar plot.
        df = pd.read_csv(output.format(dataset), index_col=0)
        df["total"] = df.sum(axis=1)
        df["f_percent"] = (df["female"] / df["total"]) * 100
        df["m_percent"] = (df["male"] / df["total"]) * 100
        df[["f_percent", "m_percent"]].plot(
            ax=ax1,
            kind="bar",
            stacked=True,
            width=1,
            alpha=0.8,
            color=["#EF5350", "#2196F3"],
            linewidth=0.15,
        )

        lines, labels = ax1.get_legend_handles_labels()
        ax1.legend(lines, ["Female", "Male"], loc=2, bbox_to_anchor=(0, 0, 1, 0.97))

        # Save JPG.
        fig.savefig(f"./output/moma-{dataset}.jpg", bbox_inches="tight")
