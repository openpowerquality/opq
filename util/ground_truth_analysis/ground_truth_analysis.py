import datetime
from typing import *

import matplotlib.pyplot as plt
import numpy as np
import pymongo
import pymongo.database
import scipy.stats


class DataPoint:
    def __init__(self,
                 ts_s: int,
                 actual_v: float,
                 min_v: float,
                 max_v: float,
                 avg_v: float,
                 stddev_v: float) -> None:
        self.ts_s: int = ts_s
        self.actual_v: float = actual_v
        self.min_v: float = min_v
        self.max_v: float = max_v
        self.avg_v: float = avg_v
        self.stddev_v: float = stddev_v

    @staticmethod
    def from_line(line: str) -> 'DataPoint':
        split_line = line.split(" ")
        ts_s = int(split_line[0])
        actual_v = float(split_line[1])
        min_v = float(split_line[2])
        max_v = float(split_line[3])
        avg_v = float(split_line[4])
        stddev_v = float(split_line[5])

        return DataPoint(ts_s, actual_v, min_v, max_v, avg_v, stddev_v)

    def __str__(self) -> str:
        return f"{self.ts_s} {self.actual_v} {self.min_v} {self.max_v} {self.avg_v} {self.stddev_v}"


def parse_file(path: str) -> List[DataPoint]:
    with open(path, "r") as fin:
        lines: List[str] = list(map(lambda line: line.strip(), fin.readlines()))
        return list(map(DataPoint.from_line, lines))


def plot_path(path: str) -> None:
    fig, ax = plt.subplots(1, 1, figsize=(16, 9))
    fig: plt.Figure = fig
    ax: plt.Axes = ax

    split_path = path.split("/")
    feature = split_path[-1]
    meter = split_path[-2]

    data_points: List[DataPoint] = parse_file(path)
    dts: List[datetime.datetime] = list(
        map(lambda data_point: datetime.datetime.utcfromtimestamp(data_point.ts_s), data_points))
    # actuals: List[float] = list(map(lambda data_point: data_point.actual_v, data_points))
    mins: List[float] = list(map(lambda data_point: data_point.min_v, data_points))
    maxes: List[float] = list(map(lambda data_point: data_point.max_v, data_points))
    averages: List[float] = list(map(lambda data_point: data_point.avg_v, data_points))

    # ax.plot(dts, actuals)
    ax.plot(dts, mins, label="Min")
    ax.plot(dts, maxes, label="Max")
    ax.plot(dts, averages, label="Average")

    ax.set_xlabel("Time (UTC)")
    ax.set_ylabel(f"{feature}")
    ax.set_title(f"{meter} {feature} {dts[0].strftime('%Y-%m-%d')} to {dts[-1].strftime('%Y-%m-%d')}")

    ax.legend()
    fig.show()


def plot_dir(path: str) -> None:
    pass


def plot_frequency(opq_start_ts_s: int,
                   opq_end_ts_s: int,
                   opq_box_id: str,
                   ground_truth_root: str,
                   uhm_sensor: str,
                   mongo_client: pymongo.MongoClient,
                   out_dir: str) -> None:
    db: pymongo.database.Database = mongo_client["opq"]
    coll: pymongo.collection.Collection = db["trends"]
    query: Dict = {
        "box_id": opq_box_id,
        "timestamp_ms": {"$gte": opq_start_ts_s * 1000,
                         "$lte": opq_end_ts_s * 1000},
        "frequency": {"$exists": True}
    }

    projection: Dict[str, bool] = {
        "_id": False,
        "box_id": True,
        "timestamp_ms": True,
        "frequency": True,
    }

    cursor: pymongo.cursor.Cursor = coll.find(query, projection=projection)
    trends: List[Dict] = list(cursor)
    timestamps_ms: np.ndarray = np.array(list(map(lambda trend: trend["timestamp_ms"], trends)))
    timestamps_s: np.ndarray = timestamps_ms / 1000.0
    dts: List[datetime.datetime] = list(map(datetime.datetime.utcfromtimestamp, list(timestamps_s)))
    frequencies: np.ndarray = np.array(list(map(lambda trend: trend["frequency"]["average"], trends)))

    gt_path: str = f"{ground_truth_root}/{uhm_sensor}/Frequency"
    data_points: List[DataPoint] = parse_file(gt_path)
    gt_ts: List[int] = list(map(lambda data_point: data_point.ts_s, data_points))
    gt_dts: List[datetime.datetime] = list(map(datetime.datetime.utcfromtimestamp, gt_ts))
    gt_f: List[float] = list(map(lambda data_point: data_point.avg_v, data_points))

    fig, ax = plt.subplots(1, 1, figsize=(16, 9))
    fig: plt.Figure = fig
    ax: plt.Axes = ax

    ax.plot(dts, frequencies, label=f"Trends (OPQ Box {opq_box_id})")
    ax.plot(gt_dts, gt_f, label=f"Ground Truth ({uhm_sensor})")

    ax.set_title(f"Frequency Ground Truth Comparison: {opq_box_id} vs {uhm_sensor} {dts[0].strftime('%Y-%m-%d')} to {dts[-1].strftime('%Y-%m-%d')}")

    ax.legend()
    fig.savefig(f"{out_dir}/f_{opq_box_id}_{uhm_sensor}.png")


if __name__ == "__main__":
    mongo_client: pymongo.MongoClient = pymongo.MongoClient()
    # 1000
    plot_frequency(1575367200, 1575972000, "1000", "/home/opq/temp/Nov10/ground_truth_data", "POST_MAIN_1", mongo_client, ".")
    plot_frequency(1575367200, 1575972000, "1000", "/home/opq/temp/Nov10/ground_truth_data", "POST_MAIN_2", mongo_client, ".")

    # 1001
    # plot_frequency(1575367200, 1575972000, "1001", "/home/opq/temp/Nov10/ground_truth_data", "HAMILTON_LIB_PH_III_CH_1_MTR", mongo_client, ".")
    plot_frequency(1575367200, 1575972000, "1001", "/home/opq/temp/Nov10/ground_truth_data", "HAMILTON_LIB_PH_III_CH_2_MTR", mongo_client, ".")
    plot_frequency(1575367200, 1575972000, "1001", "/home/opq/temp/Nov10/ground_truth_data", "HAMILTON_LIB_PH_III_CH_3_MTR", mongo_client, ".")
    plot_frequency(1575367200, 1575972000, "1001", "/home/opq/temp/Nov10/ground_truth_data", "HAMILTON_LIB_PH_III_MAIN_1_MTR", mongo_client, ".")
    plot_frequency(1575367200, 1575972000, "1001", "/home/opq/temp/Nov10/ground_truth_data", "HAMILTON_LIB_PH_III_MAIN_2_MTR", mongo_client, ".")
    plot_frequency(1575367200, 1575972000, "1001", "/home/opq/temp/Nov10/ground_truth_data", "HAMILTON_LIB_PH_III_MCC_AC1_MTR", mongo_client, ".")
    plot_frequency(1575367200, 1575972000, "1001", "/home/opq/temp/Nov10/ground_truth_data", "HAMILTON_LIB_PH_III_MCC_AC2_MTR", mongo_client, ".")

    # 1002
    plot_frequency(1575367200, 1575972000, "1002", "/home/opq/temp/Nov10/ground_truth_data", "POST_MAIN_1", mongo_client, ".")
    plot_frequency(1575367200, 1575972000, "1002", "/home/opq/temp/Nov10/ground_truth_data", "POST_MAIN_2", mongo_client, ".")

    # 1003
    plot_frequency(1575367200, 1575972000, "1003", "/home/opq/temp/Nov10/ground_truth_data", "KELLER_HALL_MAIN_MTR", mongo_client, ".")

    # 1021
    plot_frequency(1575367200, 1575972000, "1021", "/home/opq/temp/Nov10/ground_truth_data", "MARINE_SCIENCE_MAIN_A_MTR", mongo_client, ".")
    plot_frequency(1575367200, 1575972000, "1021", "/home/opq/temp/Nov10/ground_truth_data", "MARINE_SCIENCE_MAIN_B_MTR", mongo_client, ".")
    # plot_frequency(1575367200, 1575972000, "1021", "/home/opq/temp/Nov10/ground_truth_data", "MARINE_SCIENCE_MCC_MTR", mongo_client, ".")

    # 1022
    plot_frequency(1575367200, 1575972000, "1022", "/home/opq/temp/Nov10/ground_truth_data", "AG_ENGINEERING_MAIN_MTR", mongo_client, ".")
    plot_frequency(1575367200, 1575972000, "1022", "/home/opq/temp/Nov10/ground_truth_data", "AG_ENGINEERING_MCC_MTR", mongo_client, ".")

    # 1023
    plot_frequency(1575367200, 1575972000, "1023", "/home/opq/temp/Nov10/ground_truth_data", "LAW_LIB_MAIN_MTR", mongo_client, ".")

    # 1025
    plot_frequency(1575367200, 1575972000, "1025", "/home/opq/temp/Nov10/ground_truth_data", "KENNEDY_THEATRE_MAIN_MTR", mongo_client, ".")

