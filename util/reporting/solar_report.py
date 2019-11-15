import argparse
import collections
import datetime
from typing import List, Dict, Tuple, Optional

import matplotlib.dates as md
import matplotlib.pyplot as plt
import numpy as np
import pymongo

import reports


def local_dt_to_ts_ms(local_dt: datetime.datetime) -> int:
    return int(round(local_dt.timestamp() * 1000.0))


def get_trends(start_ts_ms_utc: int,
               end_ts_ms_utc: int,
               mongo_client: pymongo.MongoClient) -> Dict[str, List[Tuple[datetime.datetime, float]]]:
    trends_coll: pymongo.collection.Collection = mongo_client["opq"]["trends"]
    query = {"timestamp_ms": {"$gte": start_ts_ms_utc,
                              "$lte": end_ts_ms_utc},
             "box_id": {"$in": reports.boxes}}
    projection = {"_id": False,
                  "timestamp_ms": True,
                  "box_id": True,
                  "thd": True}

    res: Dict[str, List[Tuple[datetime.datetime, float]]] = collections.defaultdict(list)
    trends = trends_coll.find(query, projection=projection).sort("timestamp_ms")
    for trend in trends:
        dt = datetime.datetime.fromtimestamp(trend["timestamp_ms"] / 1000.0)
        thd = trend["thd"]["max"] * 100.0
        res[trend["box_id"]].append((dt, thd))

    return res


def first_not_none_idx(vals: List[Optional[float]]) -> int:
    for (i, v) in enumerate(vals):
        if v is not None:
            return i

    return -1


def last_not_none_idx(vals: List[Optional[float]]) -> int:
    i = len(vals) - 1
    while i > 0:
        if vals[i] is not None:
            return i
        i -= 1
    return -1


def analyze_solar_data(solar_data_csv_path: str):
    mongo_client = pymongo.MongoClient()
    with open(solar_data_csv_path, "r") as fin:
        lines = list(map(lambda line: line.strip().replace('"', ""), fin.readlines()[1:]))
        timestamps = []
        elkor_prod_meter_kw = []
        inverters_kw = []

        for line in lines:
            split_line = line.split(",")
            timestamps.append(split_line[0])
            elkor_value = float(split_line[1]) if len(split_line[1]) > 0 else None
            elkor_prod_meter_kw.append(elkor_value)
            inverter_value = float(split_line[2]) if len(split_line[2]) > 0 else None
            inverters_kw.append(inverter_value)

        dts = list(map(lambda ts: datetime.datetime.strptime(ts, "%Y-%m-%d %H:%M:%S"), timestamps))

        start_ts_ms_utc = local_dt_to_ts_ms(dts[first_not_none_idx(inverters_kw)])
        end_ts_ms_utc = local_dt_to_ts_ms(dts[last_not_none_idx(inverters_kw)])
        start_dt = datetime.datetime.fromtimestamp(start_ts_ms_utc / 1000.0)
        end_dt = datetime.datetime.fromtimestamp(end_ts_ms_utc / 1000.0)

        fig, axes = plt.subplots(2, 1, figsize=(16, 9), sharex="all")
        fig: plt.Figure = fig
        axes: List[plt.Axes] = axes

        fig.suptitle("UHM Solar Production vs. THD (%s to %s HST)" % (
            start_dt.strftime("%Y-%m-%d %H:%M"),
            end_dt.strftime("%Y-%m-%d %H:%M"),
        ))

        # Solar ax
        ax_solar = axes[0]
        ax_solar.plot(dts, inverters_kw, label="Inverters Kilowatts")
        ax_solar.plot(dts, elkor_prod_meter_kw, label="Elkor Production Meter Kilowatts")

        ax_solar.set_title("Solar Production Parking Structure Ph II")
        ax_solar.set_ylabel("Kilowatts")
        ax_solar.legend()

        # THD ax
        ax_thd = axes[1]
        trend_data = get_trends(start_ts_ms_utc, end_ts_ms_utc, mongo_client)
        for box_id, data in trend_data.items():
            dts = list(map(lambda t: t[0], data))
            thds = list(map(lambda t: t[1], data))
            ax_thd.plot(dts, thds, label="%s %s" % (box_id, reports.box_to_location[box_id]))

        ax_thd.set_title("Percent THD OPQ Boxes")
        ax_thd.set_ylabel("Percent THD")
        ax_thd.set_xlabel("Time (dd HH:MM HST)")
        ax_thd.set_ylim(ymax=7)
        fmt = md.DateFormatter("%d %H:%M")
        ax_thd.xaxis.set_major_formatter(fmt)
        ax_thd.legend(bbox_to_anchor=(0, 1), loc='upper left', ncol=5)

        plt.savefig("solar_report_%d_%d.png" % (start_ts_ms_utc, end_ts_ms_utc))


if __name__ == "__main__":
    PARSER = argparse.ArgumentParser()
    PARSER.add_argument("solar_data_csv_path")
    ARGS = PARSER.parse_args()
    analyze_solar_data(ARGS.solar_data_csv_path)
