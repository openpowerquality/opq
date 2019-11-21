import datetime
from typing import Dict, List, Union

import reports

import matplotlib.pyplot as plt
import numpy as np
import pymongo
import pymongo.database
import scipy.signal as signal


class Trend:
    def __init__(self,
                 timestamp_ms: int,
                 box_id: str,
                 minv: float,
                 meanv: float,
                 maxv: float):
        self.timestamp_ms = timestamp_ms
        self.dt = datetime.datetime.utcfromtimestamp(timestamp_ms / 1000.0)
        self.box_id = box_id
        self.minv = minv
        self.meanv = meanv
        self.maxv = maxv

    @staticmethod
    def from_trend_doc(doc: Dict) -> 'Trend':
        return Trend(doc["timestamp_ms"], doc["box_id"], doc["voltage"]["min"], doc["voltage"]["average"], doc["voltage"]["max"])

    def __str__(self):
        return "(%s %d (%s) %f %f %f)" % (self.box_id, self.timestamp_ms, self.dt, self.minv, self.meanv, self.maxv)


# noinspection PyTypeChecker
def analyze_trends(trends: List[Trend],
                   report_dir: str):
    fig, axes = plt.subplots(3, 2, figsize=(18, 12))
    fig: plt.Figure = fig
    axes: List[List[plt.Axes]] = axes

    # Organize the trend data
    dts = np.array(list(map(lambda trend: trend.dt, trends)))
    mins = np.array(list(map(lambda trend: trend.minv, trends)))
    means = np.array(list(map(lambda trend: trend.meanv, trends)))
    maxes = np.array(list(map(lambda trend: trend.maxv, trends)))

    # Plot the trends
    ax_trend = axes[0][0]
    ax_trend.plot(dts, mins, label="Min $V_{RMS}$")
    ax_trend.plot(dts, means, label="Mean $V_{RMS}$")
    ax_trend.plot(dts, maxes, label="Max $V_{RMS}$")
    ax_trend.set_xlim(xmin=dts[0], xmax=dts[-1])

    ax_trend.set_title("$V_{RMS}$ Trends with Peaks")
    ax_trend.set_ylabel("$V_{RMS}$")

    # Trent hist
    ax_trend_hist = axes[0][1]
    ax_trend_hist.hist([mins, means, maxes], bins=100, stacked=True, density=True, label=["Min $V_{RMS}$",
                                                                                          "Mean $V_{RMS}$",
                                                                                          "Max $V_{RMS}$"])
    ax_trend_hist.set_title("Histogram of Trend Values")
    ax_trend_hist.set_ylabel("Percent Density")
    ax_trend_hist.set_xlabel("$V_{RMS}$")
    ax_trend_hist.set_ylim(ymax=0.2)
    ax_trend_hist.legend()

    # Find those peaks
    max_peaks, _ = signal.find_peaks(maxes, threshold=.5, distance=30)
    ax_trend.plot(dts[max_peaks], maxes[max_peaks], "X", label="Swell Peaks")

    min_peaks, _ = signal.find_peaks(-mins, threshold=2)
    ax_trend.plot(dts[min_peaks], mins[min_peaks], "X", label="Sag Peaks")

    ax_trend.legend()

    # Determine periodicity
    ax_periodic = axes[1][0]
    mins_diff = np.array(list(map(lambda td: td.seconds / 60.0, np.diff(dts[min_peaks]))))
    ax_periodic.plot(dts[min_peaks[1:]], mins_diff, label="Delta Min Peaks")

    maxes_diff = np.array(list(map(lambda td: td.seconds / 60.0, np.diff(dts[max_peaks]))))
    ax_periodic.plot(dts[max_peaks[1:]], maxes_diff, label="Delta Max Peaks", color="green")
    max_mean = maxes_diff.mean()
    ax_periodic.plot(dts, [max_mean for _ in dts], color="green", linestyle="--", label="Mean(Delta Max Peaks)")
    min_mean = mins_diff.mean()
    ax_periodic.plot(dts, [min_mean for _ in dts], color="blue", linestyle="--", label="Mean(Delta Min Peaks)")

    ax_periodic.set_ylabel("Minutes")
    ax_periodic.set_title("Peak Periodicity (Minutes)")
    ax_periodic.set_xlim(xmin=dts[0], xmax=dts[-1])
    ax_periodic.legend()

    # Periodicity Hist
    ax_periodic_hist = axes[1][1]
    ax_periodic_hist.hist([mins_diff, maxes_diff], bins=50, stacked=True, density=True, label=["Delta Min Peaks",
                                                                                               "Delta Max Peaks"],
                          color=["blue", "green"])
    ax_periodic_hist.set_title("Histogram of Peak Periodicity")
    ax_periodic_hist.set_ylabel("Percent Density")
    ax_periodic_hist.set_xlabel("Minutes")
    ax_periodic_hist.legend()

    # Determine on cycle
    ax_on_cycle = axes[2][0]
    on_cycle_dts = []
    on_cycle = []

    def first_swell_idx_after_sag(sag_idx: int) -> int:
        if sag_idx >= max_peaks[-1]:
            return -1

        return list(filter(lambda i: i >= sag_idx, max_peaks))[0]

    for idx in min_peaks:
        sag_dt = dts[idx]
        swell_idx = first_swell_idx_after_sag(idx)
        if swell_idx >= 0:
            swell_dt = dts[swell_idx]
            diff = (swell_dt - sag_dt).seconds / 60.0
            on_cycle.append(diff)
            on_cycle_dts.append(swell_dt)

    on_cycle = np.array(on_cycle)
    ax_on_cycle.plot(on_cycle_dts, on_cycle, label="On-Cycle")

    on_mean = on_cycle.mean()
    ax_on_cycle.plot(dts, [on_mean for _ in dts], color="blue", linestyle="--", label="Mean(On-Cycle)")

    ax_on_cycle.set_ylabel("Minutes")
    ax_on_cycle.set_xlabel("Time (UTC)")
    ax_on_cycle.set_title("Estimated On-cycle (Sag to next Swell) Minutes")
    ax_on_cycle.set_xlim(xmin=dts[0], xmax=dts[-1])
    ax_on_cycle.legend()

    # On cycle hist
    # Periodicity Hist
    ax_on_hist = axes[2][1]
    ax_on_hist.hist(on_cycle, bins=50, density=True, label="On-Cycle")
    ax_on_hist.set_title("Histogram of On-Cycle")
    ax_on_hist.set_ylabel("Percent Density")
    ax_on_hist.set_xlabel("Minutes")
    ax_on_hist.legend()

    # Finalize the plot
    fig.suptitle("Voltage Trends OPQ Box %s (%s) from %s UTC to %s UTC" % (
        trends[0].box_id,
        reports.box_to_location[trends[0].box_id],
        dts[0].strftime("%Y-%m-%d %H:%M"),
        dts[-1].strftime("%Y-%m-%d %H:%M")
    ))

    plt.subplots_adjust(hspace=.5)
    plt.savefig("%s/periodic_voltage_trends.png" % report_dir)
    plt.show()

def get_voltage_trends(start_ts_s: int,
                       end_ts_s: int,
                       box_id: str) -> List[Trend]:
    mongo_client: pymongo.MongoClient = pymongo.MongoClient()
    db: pymongo.database.Database = mongo_client["opq"]
    coll: pymongo.collection.Collection = db["trends"]

    query = {"timestamp_ms": {"$gte": start_ts_s * 1000.0,
                              "$lte": end_ts_s * 1000.0},
             "box_id": box_id}
    projection = {"_id": False,
                  "voltage": True,
                  "box_id": True,
                  "timestamp_ms": True}

    trends = list(coll.find(query, projection=projection))
    trends = list(map(Trend.from_trend_doc, trends))

    return trends


if __name__ == "__main__":
    trends = get_voltage_trends(1573605390, 1574199881, "1021")
    analyze_trends(trends, ".")
