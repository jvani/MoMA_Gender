
import os
import re
import pandas as pd
import datetime as dt
import plotly.tools as tls
import plotly.plotly as py
import plotly.graph_objs as go
import matplotlib.pyplot as plt

tls.set_credentials_file(username="jvani", api_key=os.getenv("PLOTLY_API"))

class MoMA(object):
    def __init__(self, artists_path, artworks_path):
        """Container for MoMA catalogue data.
        Args:
            artists_path (str) - path to artists.csv
            artworks_path (str) - path to artworks.csv
        """

        # -- Read csv files.
        self.artists = pd.read_csv(artists_path, index_col=["Artist ID"])
        self.artworks = pd.read_csv(artworks_path, index_col=["Artwork ID"])

        # -- Standardize Gender case.
        self.artists["Gender"] = self.artists["Gender"].str.title()

        # -- Pull acquisition year.
        self.artworks["Acquisition Year"] = self.artworks["Acquisition Date"] \
            .str[:4].fillna(0).astype(int)

        # -- Pull artwork year.
        self.artworks["Art Year"] = self.artworks["Date"] \
            .apply(lambda x: re.findall("\d+", str(x))) \
            .apply(lambda x: filter(lambda y: len(y) == 4, x))
        self.artworks["Art Year"] = self.artworks["Art Year"].str[0]
        self.artworks["Art Year"] = self.artworks["Art Year"].fillna(0) \
            .astype(int)

        # -- Merge artist and artwork data.
        self.data = pd.merge(self.artworks, self.artists, how="inner",
            left_on="Name", right_on="Name")

        # -- Create acquisition summary data.
        self.acq = self.data.groupby(["Acquisition Year", "Gender"]).size() \
            .unstack(1)
        self.acq["Tot"] = self.acq.sum(axis=1)
        self.acq["FPercent"] = (self.acq["Female"] / self.acq["Tot"]) * 100
        self.acq["MPercent"] = (self.acq["Male"] / self.acq["Tot"]) * 100
        self.acq = self.acq.iloc[1:, :]

        # -- Create artwork year summary data.
        self.artyear = self.data.groupby(["Art Year", "Gender"]).size() \
            .unstack(1)
        self.artyear["Tot"] = self.artyear.sum(axis=1)
        self.artyear["FPercent"] = (self.artyear["Female"] / self.artyear["Tot"]) * 100
        self.artyear["MPercent"] = (self.artyear["Male"] / self.artyear["Tot"]) * 100
        self.artyear = self.artyear.iloc[1:, :]


    def plot_acquisition_year(self, output=None, plotting_lib="matplotlib"):
        """Plot the proportion of artwork by acquisition year.
        Args:
            output (str) - output path to save matplotlib plot.
            plotting_lib (str) - plotting library to use.
        """

        xlabel = "Acquisition Year"
        ylabel = "Percent of MoMA Acquisitions"
        title =  "Percent of MoMA Acquisitions by Year"

        if plotting_lib == "matplotlib":
            # -- Create axes.
            fig, (ax1) = plt.subplots(nrows=1, ncols=1, figsize=(18, 4))

            # -- Format plot.
            ax1.tick_params(top="off", bottom="off", left="off", right="off")
            for spine in fig.gca().spines.values():
                spine.set_visible(False)

            # -- Plot acquisition percentages as stacked bar plot.
            self.acq[["FPercent", "MPercent"]].plot(ax=ax1,
                kind="bar", stacked=True, width=1, alpha=0.8,
                color=["#EF5350", "#2196F3"], linewidth=0.15)

            # -- Add axis labels, title, and legend.
            ax1.set_ylabel(ylabel)
            ax1.set_xlabel(xlabel)
            ax1.set_title(title)
            lines, labels = ax1.get_legend_handles_labels()
            ax1.legend(lines, ["Female", "Male"], loc=2,
                bbox_to_anchor=(0, 0, 1, 0.97))

            # -- Save to output.
            fig.savefig(output, bbox_inches="tight")


        elif plotting_lib == "plotly":
            # -- Create hover labels.
            ftext = ",".join("{}<br>{}".format(*i) for i in zip(
                ["Percent: {:.2f}%".format(i) for i in self.acq.FPercent],
                ["Acquisitions: {}".format(int(i)) for i in self.acq.Female \
                .fillna(0)])).split(",")
            mtext = ",".join("{}<br>{}".format(*i) for i in zip(
                ["Percent: {:.2f}%".format(i) for i in self.acq.MPercent],
                ["Acquisitions: {}".format(int(i)) for i in self.acq.Male \
                .fillna(0)])).split(",")

            # -- Plot.
            f = go.Bar(
                x=self.acq.index,
                y=self.acq.FPercent,
                name="Female Artists",
                marker=dict(color="#EF5350"),
                text=ftext,
                hoverinfo="x+text",
                opacity=0.8
            )
            m = go.Bar(
                x=self.acq.index,
                y=self.acq.MPercent,
                name="Male Artists",
                marker=dict(color="#2196F3"),
                text=mtext,
                hoverinfo="x+text",
                opacity=0.8
            )

            data = [f, m]
            layout = go.Layout(
                barmode="stack",
                title=title,
                xaxis=dict(title=xlabel),
                yaxis=dict(title=ylabel)

            )

            fig = go.Figure(data=data, layout=layout)
            py.iplot(fig, filename="MOMA_Acquisition")


        else:
            raise ValueError("'{}' is not a valid plotting library." \
                .format(plotting_lib))


    def plot_art_year(self, output=None, plotting_lib="matplotlib"):
        """Plot the proportion of artwork by production year.
        Args:
            output (str) - output path to save matplotlib plot.
            plotting_lib (str) - plotting library to use.
        """

        xlabel = "Production Year"
        ylabel = "Percent of MoMA Artwork"
        title =  "Percent of MoMA Artwork by Production Year"
        df = self.artyear[(self.artyear.index > 1899) & (self.artyear.index < 2017)]

        if plotting_lib == "matplotlib":
            # -- Create axes.
            fig, (ax1) = plt.subplots(nrows=1, ncols=1, figsize=(18, 4))

            # -- Format plot.
            ax1.tick_params(top="off", bottom="off", left="off", right="off")
            for spine in fig.gca().spines.values():
                spine.set_visible(False)

            # -- Plot acquisition percentages as stacked bar plot.
            df[["FPercent", "MPercent"]].plot(ax=ax1, kind="bar", stacked=True,
                width=1, alpha=0.8, color=["#EF5350", "#2196F3"],
                linewidth=0.15)

            # -- Add axis labels, title, and legend.
            ax1.set_ylabel(ylabel)
            ax1.set_xlabel(xlabel)
            ax1.set_title(title)
            lines, labels = ax1.get_legend_handles_labels()
            ax1.legend(lines, ["Female", "Male"], loc=2,
                bbox_to_anchor=(0, 0, 1, 0.97))

            # -- Save to output.
            fig.savefig(output, bbox_inches="tight")


        elif plotting_lib == "plotly":
            # -- Create hover labels.
            ftext = ",".join("{}<br>{}".format(*i) for i in zip(
                ["Percent: {:.2f}%".format(i) for i in df.FPercent],
                ["Artworks: {}".format(int(i)) for i in df.Female \
                .fillna(0)])).split(",")
            mtext = ",".join("{}<br>{}".format(*i) for i in zip(
                ["Percent: {:.2f}%".format(i) for i in df.MPercent],
                ["Artworks: {}".format(int(i)) for i in df.Male \
                .fillna(0)])).split(",")

            # -- Plot.
            f = go.Bar(
                x=df.index,
                y=df.FPercent,
                name="Female Artists",
                marker=dict(color="#EF5350"),
                text=ftext,
                hoverinfo="x+text",
                opacity=0.8
            )
            m = go.Bar(
                x=df.index,
                y=df.MPercent,
                name="Male Artists",
                marker=dict(color="#2196F3"),
                text=mtext,
                hoverinfo="x+text",
                opacity=0.8
            )

            data = [f, m]
            layout = go.Layout(
                barmode="stack",
                title=title,
                xaxis=dict(title=xlabel),
                yaxis=dict(title=ylabel)

            )

            fig = go.Figure(data=data, layout=layout)
            py.iplot(fig, filename="MOMA_ArtYear")


        else:
            raise ValueError("'{}' is not a valid plotting library." \
                .format(plotting_lib))


if __name__ == "__main__":
    mm = MoMA("./data/artists.csv", "./data/artworks.csv")
    mm.plot_acquisition_year("./output/MoMAAcquisition.jpeg")
    mm.plot_art_year("./output/MoMAArtYear.jpeg")
