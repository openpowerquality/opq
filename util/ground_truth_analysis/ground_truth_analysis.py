import datetime
from typing import *

import matplotlib.pyplot as plt
import numpy as np
import pymongo
import pymongo.database


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

    # Align the samples
    opq_dts: Set[datetime.datetime] = set(
        map(lambda dt: datetime.datetime(dt.year, dt.month, dt.day, dt.hour, dt.minute), dts))
    uhm_dts: Set[datetime.datetime] = set(
        map(lambda dt: datetime.datetime(dt.year, dt.month, dt.day, dt.hour, dt.minute), gt_dts))
    intersecting_dts: Set[datetime.datetime] = opq_dts.intersection(uhm_dts)

    aligned_opq_dts = []
    aligned_uhm_dts = []
    aligned_opq_freqs = []
    aligned_uhm_freqs = []

    for i, dt in enumerate(dts):
        new_dt = datetime.datetime(dt.year, dt.month, dt.day, dt.hour, dt.minute)
        if new_dt in intersecting_dts:
            aligned_opq_dts.append(dt)
            aligned_opq_freqs.append(frequencies[i])

    for i, dt in enumerate(gt_dts):
        new_dt = datetime.datetime(dt.year, dt.month, dt.day, dt.hour, dt.minute)
        if new_dt in intersecting_dts:
            aligned_uhm_dts.append(dt)
            aligned_uhm_freqs.append(gt_f[i])

    aligned_opq_freqs = np.array(aligned_opq_freqs)
    aligned_uhm_freqs = np.array(aligned_uhm_freqs)

    fig, ax = plt.subplots(3, 1, figsize=(16, 9), sharex="all")
    fig: plt.Figure = fig
    ax: List[plt.Axes] = ax

    # OPQ
    ax_opq = ax[0]
    ax_opq.plot(aligned_opq_dts, aligned_opq_freqs, label=f"Trends (OPQ Box {opq_box_id})")
    ax_opq.set_ylabel("Frequency (Hz)")
    ax_opq.set_title(f"OPQ Box {opq_box_id} Mean={aligned_opq_freqs.mean()} Std={aligned_opq_freqs.std()}")
    ax_opq.legend()

    # UHM
    ax_uhm = ax[1]
    ax_uhm.plot(aligned_uhm_dts, aligned_uhm_freqs, label=f"Ground Truth ({uhm_sensor})")
    ax_uhm.set_ylabel("Frequency (Hz)")
    ax_uhm.set_title(f"UHM Meter {uhm_sensor} Mean={aligned_uhm_freqs.mean()} Std={aligned_uhm_freqs.std()}")
    ax_uhm.legend()

    # Diff
    ax_diff = ax[2]
    if len(aligned_uhm_freqs) == len(aligned_opq_freqs):
        diff: np.ndarray = aligned_opq_freqs - aligned_uhm_freqs
        ax_diff.plot(aligned_opq_dts, diff, label=f"Diff")
        ax_diff.legend()
        ax_diff.set_ylabel("Difference")
        ax_diff.set_title(f"Difference ({opq_box_id} - {uhm_sensor})  Mean={diff.mean()} Std={diff.std()}")
    else:
        diff: np.ndarray = aligned_opq_freqs[1:] - aligned_uhm_freqs
        ax_diff.plot(aligned_opq_dts[1:], diff, label=f"Diff")
        ax_diff.legend()
        ax_diff.set_ylabel("Difference")
        ax_diff.set_title(f"Difference ({opq_box_id} - {uhm_sensor})  Mean={diff.mean()} Std={diff.std()}")

    ax_diff.set_ylabel("Frequency Diff (Hz)")
    ax_diff.set_xlabel("Time (UTC)")

    fig.suptitle(
        f"Frequency Ground Truth Comparison: {opq_box_id} vs {uhm_sensor} {dts[0].strftime('%Y-%m-%d')} to {dts[-1].strftime('%Y-%m-%d')}")

    fig.savefig(f"{out_dir}/f_{opq_box_id}_{uhm_sensor}.png")


def plot_avg_voltage_thd(opq_start_ts_s: int,
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
        "thd": {"$exists": True}
    }

    projection: Dict[str, bool] = {
        "_id": False,
        "box_id": True,
        "timestamp_ms": True,
        "thd": True,
    }

    cursor: pymongo.cursor.Cursor = coll.find(query, projection=projection)
    trends: List[Dict] = list(cursor)
    timestamps_ms: np.ndarray = np.array(list(map(lambda trend: trend["timestamp_ms"], trends)))
    timestamps_s: np.ndarray = timestamps_ms / 1000.0
    dts: List[datetime.datetime] = list(map(datetime.datetime.utcfromtimestamp, list(timestamps_s)))
    thds: np.ndarray = np.array(list(map(lambda trend: trend["thd"]["average"], trends)))
    thds = thds * 100.0

    gt_path: str = f"{ground_truth_root}/{uhm_sensor}/AVG_VOLTAGE_THD"
    data_points: List[DataPoint] = parse_file(gt_path)
    gt_ts: List[int] = list(map(lambda data_point: data_point.ts_s, data_points))
    gt_dts: List[datetime.datetime] = list(map(datetime.datetime.utcfromtimestamp, gt_ts))
    gt_thd: List[float] = list(map(lambda data_point: data_point.avg_v, data_points))

    # Align the samples
    opq_dts: Set[datetime.datetime] = set(
        map(lambda dt: datetime.datetime(dt.year, dt.month, dt.day, dt.hour, dt.minute), dts))
    uhm_dts: Set[datetime.datetime] = set(
        map(lambda dt: datetime.datetime(dt.year, dt.month, dt.day, dt.hour, dt.minute), gt_dts))
    intersecting_dts: Set[datetime.datetime] = opq_dts.intersection(uhm_dts)

    aligned_opq_dts = []
    aligned_uhm_dts = []
    aligned_opq_thds = []
    aligned_uhm_thds = []

    for i, dt in enumerate(dts):
        new_dt = datetime.datetime(dt.year, dt.month, dt.day, dt.hour, dt.minute)
        if new_dt in intersecting_dts:
            aligned_opq_dts.append(dt)
            aligned_opq_thds.append(thds[i])

    for i, dt in enumerate(gt_dts):
        new_dt = datetime.datetime(dt.year, dt.month, dt.day, dt.hour, dt.minute)
        if new_dt in intersecting_dts:
            aligned_uhm_dts.append(dt)
            aligned_uhm_thds.append(gt_thd[i])

    aligned_opq_thds = np.array(aligned_opq_thds)
    aligned_uhm_thds = np.array(aligned_uhm_thds)

    fig, ax = plt.subplots(3, 1, figsize=(16, 9), sharex="all")
    fig: plt.Figure = fig
    ax: List[plt.Axes] = ax

    # OPQ
    ax_opq = ax[0]
    ax_opq.plot(aligned_opq_dts, aligned_opq_thds, label=f"Trends (OPQ Box {opq_box_id})")
    ax_opq.set_ylabel("% THD")
    ax_opq.set_title(f"OPQ Box {opq_box_id} Mean={aligned_opq_thds.mean()} Std={aligned_opq_thds.std()}")
    ax_opq.legend()

    # UHM
    ax_uhm = ax[1]
    ax_uhm.plot(aligned_uhm_dts, aligned_uhm_thds, label=f"Ground Truth ({uhm_sensor})")
    ax_uhm.set_ylabel("% THD")
    ax_uhm.set_title(f"UHM Meter {uhm_sensor} Mean={aligned_uhm_thds.mean()} Std={aligned_uhm_thds.std()}")
    ax_uhm.legend()

    # Diff
    ax_diff = ax[2]
    if len(aligned_uhm_thds) == len(aligned_opq_thds):
        diff: np.ndarray = aligned_opq_thds - aligned_uhm_thds
        ax_diff.plot(aligned_opq_dts, diff, label=f"Diff")
        ax_diff.legend()
        ax_diff.set_ylabel("Difference")
        ax_diff.set_title(f"Difference ({opq_box_id} - {uhm_sensor})  Mean={diff.mean()} Std={diff.std()}")
    else:
        diff: np.ndarray = aligned_opq_thds[1:] - aligned_uhm_thds
        ax_diff.plot(aligned_opq_dts[1:], diff, label=f"Diff")
        ax_diff.legend()
        ax_diff.set_ylabel("Difference")
        ax_diff.set_title(f"Difference ({opq_box_id} - {uhm_sensor})  Mean={diff.mean()} Std={diff.std()}")

    ax_diff.set_ylabel("% THD Diff)")
    ax_diff.set_xlabel("Time (UTC)")

    fig.suptitle(
        f"THD Ground Truth Comparison: {opq_box_id} vs {uhm_sensor} {dts[0].strftime('%Y-%m-%d')} to {dts[-1].strftime('%Y-%m-%d')}")

    fig.savefig(f"{out_dir}/avg_voltage_thd_{opq_box_id}_{uhm_sensor}.png")


if __name__ == "__main__":
    mongo_client: pymongo.MongoClient = pymongo.MongoClient()

    # Frequency
    # 1000
    plot_frequency(1575367200, 1575972000, "1000", "/home/opq/temp/Nov10/ground_truth_data", "POST_MAIN_1",
                   mongo_client, ".")
    plot_frequency(1575367200, 1575972000, "1000", "/home/opq/temp/Nov10/ground_truth_data", "POST_MAIN_2",
                   mongo_client, ".")

    # 1001
    # # plot_frequency(1575367200, 1575972000, "1001", "/home/opq/temp/Nov10/ground_truth_data", "HAMILTON_LIB_PH_III_CH_1_MTR", mongo_client, ".")
    # plot_frequency(1575367200, 1575972000, "1001", "/home/opq/temp/Nov10/ground_truth_data",
    #                "HAMILTON_LIB_PH_III_CH_2_MTR", mongo_client, ".")
    # plot_frequency(1575367200, 1575972000, "1001", "/home/opq/temp/Nov10/ground_truth_data",
    #                "HAMILTON_LIB_PH_III_CH_3_MTR", mongo_client, ".")
    # plot_frequency(1575367200, 1575972000, "1001", "/home/opq/temp/Nov10/ground_truth_data",
    #                "HAMILTON_LIB_PH_III_MAIN_1_MTR", mongo_client, ".")
    # plot_frequency(1575367200, 1575972000, "1001", "/home/opq/temp/Nov10/ground_truth_data",
    #                "HAMILTON_LIB_PH_III_MAIN_2_MTR", mongo_client, ".")
    # plot_frequency(1575367200, 1575972000, "1001", "/home/opq/temp/Nov10/ground_truth_data",
    #                "HAMILTON_LIB_PH_III_MCC_AC1_MTR", mongo_client, ".")
    # plot_frequency(1575367200, 1575972000, "1001", "/home/opq/temp/Nov10/ground_truth_data",
    #                "HAMILTON_LIB_PH_III_MCC_AC2_MTR", mongo_client, ".")
    #
    # # 1002
    # plot_frequency(1575367200, 1575972000, "1002", "/home/opq/temp/Nov10/ground_truth_data", "POST_MAIN_1",
    #                mongo_client, ".")
    # plot_frequency(1575367200, 1575972000, "1002", "/home/opq/temp/Nov10/ground_truth_data", "POST_MAIN_2",
    #                mongo_client, ".")
    #
    # # 1003
    # plot_frequency(1575367200, 1575972000, "1003", "/home/opq/temp/Nov10/ground_truth_data", "KELLER_HALL_MAIN_MTR",
    #                mongo_client, ".")
    #
    # # 1021
    # plot_frequency(1575367200, 1575972000, "1021", "/home/opq/temp/Nov10/ground_truth_data",
    #                "MARINE_SCIENCE_MAIN_A_MTR", mongo_client, ".")
    # plot_frequency(1575367200, 1575972000, "1021", "/home/opq/temp/Nov10/ground_truth_data",
    #                "MARINE_SCIENCE_MAIN_B_MTR", mongo_client, ".")
    # # plot_frequency(1575367200, 1575972000, "1021", "/home/opq/temp/Nov10/ground_truth_data", "MARINE_SCIENCE_MCC_MTR", mongo_client, ".")
    #
    # # 1022
    # plot_frequency(1575367200, 1575972000, "1022", "/home/opq/temp/Nov10/ground_truth_data", "AG_ENGINEERING_MAIN_MTR",
    #                mongo_client, ".")
    # plot_frequency(1575367200, 1575972000, "1022", "/home/opq/temp/Nov10/ground_truth_data", "AG_ENGINEERING_MCC_MTR",
    #                mongo_client, ".")
    #
    # # 1023
    # plot_frequency(1575367200, 1575972000, "1023", "/home/opq/temp/Nov10/ground_truth_data", "LAW_LIB_MAIN_MTR",
    #                mongo_client, ".")
    #
    # # 1025
    # plot_frequency(1575367200, 1575972000, "1025", "/home/opq/temp/Nov10/ground_truth_data", "KENNEDY_THEATRE_MAIN_MTR",
    #                mongo_client, ".")

    # Thd
    # 1000
    plot_avg_voltage_thd(1575367200, 1575972000, "1000", "/home/opq/temp/Nov10/ground_truth_data", "POST_MAIN_1",
                   mongo_client, ".")
    plot_avg_voltage_thd(1575367200, 1575972000, "1000", "/home/opq/temp/Nov10/ground_truth_data", "POST_MAIN_2",
                   mongo_client, ".")

    # 1001
    # plot_frequency(1575367200, 1575972000, "1001", "/home/opq/temp/Nov10/ground_truth_data", "HAMILTON_LIB_PH_III_CH_1_MTR", mongo_client, ".")
    plot_avg_voltage_thd(1575367200, 1575972000, "1001", "/home/opq/temp/Nov10/ground_truth_data",
                   "HAMILTON_LIB_PH_III_CH_2_MTR", mongo_client, ".")
    plot_avg_voltage_thd(1575367200, 1575972000, "1001", "/home/opq/temp/Nov10/ground_truth_data",
                   "HAMILTON_LIB_PH_III_CH_3_MTR", mongo_client, ".")
    plot_avg_voltage_thd(1575367200, 1575972000, "1001", "/home/opq/temp/Nov10/ground_truth_data",
                   "HAMILTON_LIB_PH_III_MAIN_1_MTR", mongo_client, ".")
    plot_avg_voltage_thd(1575367200, 1575972000, "1001", "/home/opq/temp/Nov10/ground_truth_data",
                   "HAMILTON_LIB_PH_III_MAIN_2_MTR", mongo_client, ".")
    plot_avg_voltage_thd(1575367200, 1575972000, "1001", "/home/opq/temp/Nov10/ground_truth_data",
                   "HAMILTON_LIB_PH_III_MCC_AC1_MTR", mongo_client, ".")
    plot_avg_voltage_thd(1575367200, 1575972000, "1001", "/home/opq/temp/Nov10/ground_truth_data",
                   "HAMILTON_LIB_PH_III_MCC_AC2_MTR", mongo_client, ".")

    # 1002
    plot_avg_voltage_thd(1575367200, 1575972000, "1002", "/home/opq/temp/Nov10/ground_truth_data", "POST_MAIN_1",
                   mongo_client, ".")
    plot_avg_voltage_thd(1575367200, 1575972000, "1002", "/home/opq/temp/Nov10/ground_truth_data", "POST_MAIN_2",
                   mongo_client, ".")

    # 1003
    # plot_avg_voltage_thd(1575367200, 1575972000, "1003", "/home/opq/temp/Nov10/ground_truth_data", "KELLER_HALL_MAIN_MTR",
    #                mongo_client, ".")

    # 1021
    plot_avg_voltage_thd(1575367200, 1575972000, "1021", "/home/opq/temp/Nov10/ground_truth_data",
                   "MARINE_SCIENCE_MAIN_A_MTR", mongo_client, ".")
    plot_avg_voltage_thd(1575367200, 1575972000, "1021", "/home/opq/temp/Nov10/ground_truth_data",
                   "MARINE_SCIENCE_MAIN_B_MTR", mongo_client, ".")
    # plot_frequency(1575367200, 1575972000, "1021", "/home/opq/temp/Nov10/ground_truth_data", "MARINE_SCIENCE_MCC_MTR", mongo_client, ".")

    # 1022
    plot_avg_voltage_thd(1575367200, 1575972000, "1022", "/home/opq/temp/Nov10/ground_truth_data", "AG_ENGINEERING_MAIN_MTR",
                   mongo_client, ".")
    plot_avg_voltage_thd(1575367200, 1575972000, "1022", "/home/opq/temp/Nov10/ground_truth_data", "AG_ENGINEERING_MCC_MTR",
                   mongo_client, ".")

    # 1023
    # plot_avg_voltage_thd(1575367200, 1575972000, "1023", "/home/opq/temp/Nov10/ground_truth_data", "LAW_LIB_MAIN_MTR",
    #                mongo_client, ".")

    # 1025
    # plot_avg_voltage_thd(1575367200, 1575972000, "1025", "/home/opq/temp/Nov10/ground_truth_data", "KENNEDY_THEATRE_MAIN_MTR",
    #                mongo_client, ".")
