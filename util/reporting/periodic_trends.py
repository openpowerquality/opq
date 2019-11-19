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

def analyze_trends(trends: List[Trend],
                   report_dir: str):
    fig, axes = plt.subplots(3, 1, figsize=(16, 9), sharex="all")
    fig: plt.Figure = fig
    axes: List[plt.Axes] = axes

    # Organize the trend data
    dts = np.array(list(map(lambda trend: trend.dt, trends)))
    mins = np.array(list(map(lambda trend: trend.minv, trends)))
    means = np.array(list(map(lambda trend: trend.meanv, trends)))
    maxes = np.array(list(map(lambda trend: trend.maxv, trends)))

    # Plot the trends
    ax_trend = axes[0]
    ax_trend.plot(dts, mins, label="Min $V_{RMS}$")
    ax_trend.plot(dts, means, label="Mean $V_{RMS}$")
    ax_trend.plot(dts, maxes, label="Max $V_{RMS}$")

    ax_trend.set_title("$V_{RMS}$ Trends with Peaks")
    ax_trend.set_ylabel("$V_{RMS}$")

    # Find those peaks
    max_peaks, _ = signal.find_peaks(maxes, threshold=.5)
    ax_trend.plot(dts[max_peaks], maxes[max_peaks], "X", label="Swell Peaks")

    min_peaks, _ = signal.find_peaks(-mins, threshold=2)
    ax_trend.plot(dts[min_peaks], mins[min_peaks], "X", label="Sag Peaks")

    ax_trend.legend()

    # Determine periodicity
    ax_periodic = axes[1]
    mins_diff = list(map(lambda td: td.seconds / 60.0, np.diff(dts[min_peaks])))
    ax_periodic.plot(dts[min_peaks[1:]], mins_diff, label="Delta Min Peaks")

    maxes_diff = list(map(lambda td: td.seconds / 60.0, np.diff(dts[max_peaks])))
    ax_periodic.plot(dts[max_peaks[1:]], maxes_diff, label="Delta Max Peaks", color="green")

    ax_periodic.set_ylabel("Minutes")
    ax_periodic.set_title("Peak Periodicity (Minutes)")
    ax_periodic.legend()

    # Determine on cycle
    ax_on_cycle = axes[2]
    on_cycles = []
    for idx in min_peaks:
        sag_dt = dts[idx]
        swell_dt = dts[max_peaks[max_peaks > idx][0]]
        diff = (swell_dt - sag_dt).seconds
        on_cycles.append(diff)
    print(on_cycles)

    # Finalize the plot
    fig.suptitle("Voltage Trends OPQ Box %s (%s) from %s UTC to %s UTC" % (
        trends[0].box_id,
        reports.box_to_location[trends[0].box_id],
        dts[0].strftime("%Y-%m-%d %H:%M"),
        dts[-1].strftime("%Y-%m-%d %H:%M")
    ))


    plt.savefig("%s/periodic_voltage_trends.png" % report_dir)

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
    trends = get_voltage_trends(1574113481, 1574199881, "1021")
    analyze_trends(trends, ".")
