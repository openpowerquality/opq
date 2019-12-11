import datetime
from typing import *

import matplotlib.pyplot as plt
import numpy as np
import pymongo
import pymongo.database

import util.io as io
import util.frequency as frequency
import util.thd as thd



def plot_avg_voltage_thd_incident(opq_start_ts_s: int,
                                  opq_end_ts_s: int,
                                  opq_box_id: str,
                                  ground_truth_root: str,
                                  uhm_sensor: str,
                                  mongo_client: pymongo.MongoClient,
                                  out_dir: str) -> None:
    db: pymongo.database.Database = mongo_client["opq"]
    trends_coll: pymongo.collection.Collection = db["trends"]
    incidents_coll: pymongo.collection.Collection = db["incidents"]

    incidents_query: Dict = {
        "start_timestamp_ms": {"$gte": start_ts_s * 1000,
                               "$lte": end_ts_s * 1000},
        "box_id": opq_box_id,
        "classifications": "EXCESSIVE_THD"
    }

    incidents_projection: Dict[str, bool] = {
        "_id": False,
        "start_timestamp_ms": True,
        "end_timestamp_ms": True,
        "classifications": True,
    }

    incidents: List[Dict] = list(incidents_coll.find(incidents_query, projection=incidents_projection))

    if len(incidents) == 0:
        return

    trends_query: Dict = {
        "box_id": opq_box_id,
        "timestamp_ms": {"$gte": opq_start_ts_s * 1000,
                         "$lte": opq_end_ts_s * 1000},
        "thd": {"$exists": True}
    }

    trends_projection: Dict[str, bool] = {
        "_id": False,
        "box_id": True,
        "timestamp_ms": True,
        "thd": True,
    }

    cursor: pymongo.cursor.Cursor = trends_coll.find(trends_query, projection=trends_projection)
    trends: List[Dict] = list(cursor)
    timestamps_ms: np.ndarray = np.array(list(map(lambda trend: trend["timestamp_ms"], trends)))
    timestamps_s: np.ndarray = timestamps_ms / 1000.0
    dts: List[datetime.datetime] = list(map(datetime.datetime.utcfromtimestamp, list(timestamps_s)))
    thds: np.ndarray = np.array(list(map(lambda trend: trend["thd"]["average"], trends)))
    thds = thds * 100.0

    gt_path: str = f"{ground_truth_root}/{uhm_sensor}/AVG_VOLTAGE_THD"
    data_points: List[io.DataPoint] = io.parse_file(gt_path)
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
    for incident in incidents:
        ax_opq.axvline(datetime.datetime.utcfromtimestamp(incident["start_timestamp_ms"] / 1000.0), 0, 100)
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
        f"THD Ground Truth Comparison: {opq_box_id} vs {uhm_sensor} {dts[0].strftime('%Y-%m-%d')} to "
        f"{dts[-1].strftime('%Y-%m-%d')}")

    fig.savefig(f"{out_dir}/avg_voltage_thd_incidents_{opq_box_id}_{uhm_sensor}.png")


if __name__ == "__main__":
    mongo_client: pymongo.MongoClient = pymongo.MongoClient()
    start_ts_s: int = 1575367200
    end_ts_s: int = 1575972000
    gt_root: str = "/home/opq/temp/Nov10/ground_truth_data"
    out_dir: str = "/home/opq/temp/Nov10"

    frequency.compare_frequencies(start_ts_s, end_ts_s, gt_root, mongo_client, out_dir)
    thd.compare_thds(start_ts_s, end_ts_s, gt_root, mongo_client, out_dir)

    # # Frequency
    # # 1000
    # frequency.plot_frequency(start_ts_s, end_ts_s, "1000", gt_root, "POST_MAIN_1",
    #                mongo_client, out_dir)
    # frequency.plot_frequency(start_ts_s, end_ts_s, "1000", gt_root, "POST_MAIN_2",
    #                mongo_client, out_dir)
    #
    # # 1001
    # # plot_frequency(start_ts_s, end_ts_s, "1001", gt_root, "HAMILTON_LIB_PH_III_CH_1_MTR", mongo_client, out_dir)
    # frequency.plot_frequency(start_ts_s, end_ts_s, "1001", gt_root,
    #                "HAMILTON_LIB_PH_III_CH_2_MTR", mongo_client, out_dir)
    # frequency.plot_frequency(start_ts_s, end_ts_s, "1001", gt_root,
    #                "HAMILTON_LIB_PH_III_CH_3_MTR", mongo_client, out_dir)
    # frequency.plot_frequency(start_ts_s, end_ts_s, "1001", gt_root,
    #                "HAMILTON_LIB_PH_III_MAIN_1_MTR", mongo_client, out_dir)
    # frequency.plot_frequency(start_ts_s, end_ts_s, "1001", gt_root,
    #                "HAMILTON_LIB_PH_III_MAIN_2_MTR", mongo_client, out_dir)
    # frequency.plot_frequency(start_ts_s, end_ts_s, "1001", gt_root,
    #                "HAMILTON_LIB_PH_III_MCC_AC1_MTR", mongo_client, out_dir)
    # frequency.plot_frequency(start_ts_s, end_ts_s, "1001", gt_root,
    #                "HAMILTON_LIB_PH_III_MCC_AC2_MTR", mongo_client, out_dir)
    #
    # # 1002
    # frequency.plot_frequency(start_ts_s, end_ts_s, "1002", gt_root, "POST_MAIN_1",
    #                mongo_client, out_dir)
    # frequency.plot_frequency(start_ts_s, end_ts_s, "1002", gt_root, "POST_MAIN_2",
    #                mongo_client, out_dir)
    #
    # # 1003
    # frequency.plot_frequency(start_ts_s, end_ts_s, "1003", gt_root, "KELLER_HALL_MAIN_MTR",
    #                mongo_client, out_dir)
    #
    # # 1021
    # frequency.plot_frequency(start_ts_s, end_ts_s, "1021", gt_root,
    #                "MARINE_SCIENCE_MAIN_A_MTR", mongo_client, out_dir)
    # frequency.plot_frequency(start_ts_s, end_ts_s, "1021", gt_root,
    #                "MARINE_SCIENCE_MAIN_B_MTR", mongo_client, out_dir)
    # # plot_frequency(start_ts_s, end_ts_s, "1021", gt_root, "MARINE_SCIENCE_MCC_MTR", mongo_client, out_dir)
    #
    # # 1022
    # frequency.plot_frequency(start_ts_s, end_ts_s, "1022", gt_root, "AG_ENGINEERING_MAIN_MTR",
    #                mongo_client, out_dir)
    # frequency.plot_frequency(start_ts_s, end_ts_s, "1022", gt_root, "AG_ENGINEERING_MCC_MTR",
    #                mongo_client, out_dir)
    #
    # # 1023
    # frequency.plot_frequency(start_ts_s, end_ts_s, "1023", gt_root, "LAW_LIB_MAIN_MTR",
    #                mongo_client, out_dir)
    #
    # # 1025
    # frequency.plot_frequency(start_ts_s, end_ts_s, "1025", gt_root, "KENNEDY_THEATRE_MAIN_MTR",
    #                mongo_client, out_dir)
    #
    # # Thd
    # # 1000
    # plot_avg_voltage_thd(start_ts_s, end_ts_s, "1000", gt_root, "POST_MAIN_1",
    #                      mongo_client, out_dir)
    # plot_avg_voltage_thd(start_ts_s, end_ts_s, "1000", gt_root, "POST_MAIN_2",
    #                      mongo_client, out_dir)
    #
    # # 1001
    # # plot_frequency(start_ts_s, end_ts_s, "1001", gt_root, "HAMILTON_LIB_PH_III_CH_1_MTR", mongo_client, out_dir)
    # plot_avg_voltage_thd(start_ts_s, end_ts_s, "1001", gt_root,
    #                      "HAMILTON_LIB_PH_III_CH_2_MTR", mongo_client, out_dir)
    # plot_avg_voltage_thd(start_ts_s, end_ts_s, "1001", gt_root,
    #                      "HAMILTON_LIB_PH_III_CH_3_MTR", mongo_client, out_dir)
    # plot_avg_voltage_thd(start_ts_s, end_ts_s, "1001", gt_root,
    #                      "HAMILTON_LIB_PH_III_MAIN_1_MTR", mongo_client, out_dir)
    # plot_avg_voltage_thd(start_ts_s, end_ts_s, "1001", gt_root,
    #                      "HAMILTON_LIB_PH_III_MAIN_2_MTR", mongo_client, out_dir)
    # plot_avg_voltage_thd(start_ts_s, end_ts_s, "1001", gt_root,
    #                      "HAMILTON_LIB_PH_III_MCC_AC1_MTR", mongo_client, out_dir)
    # plot_avg_voltage_thd(start_ts_s, end_ts_s, "1001", gt_root,
    #                      "HAMILTON_LIB_PH_III_MCC_AC2_MTR", mongo_client, out_dir)
    #
    # # 1002
    # plot_avg_voltage_thd(start_ts_s, end_ts_s, "1002", gt_root, "POST_MAIN_1",
    #                      mongo_client, out_dir)
    # plot_avg_voltage_thd(start_ts_s, end_ts_s, "1002", gt_root, "POST_MAIN_2",
    #                      mongo_client, out_dir)
    #
    # # 1003
    # # plot_avg_voltage_thd(start_ts_s, end_ts_s, "1003", gt_root, "KELLER_HALL_MAIN_MTR",
    # #                mongo_client, out_dir)
    #
    # # 1021
    # plot_avg_voltage_thd(start_ts_s, end_ts_s, "1021", gt_root,
    #                      "MARINE_SCIENCE_MAIN_A_MTR", mongo_client, out_dir)
    # plot_avg_voltage_thd(start_ts_s, end_ts_s, "1021", gt_root,
    #                      "MARINE_SCIENCE_MAIN_B_MTR", mongo_client, out_dir)
    # # plot_frequency(start_ts_s, end_ts_s, "1021", gt_root, "MARINE_SCIENCE_MCC_MTR", mongo_client, out_dir)
    #
    # # 1022
    # plot_avg_voltage_thd(start_ts_s, end_ts_s, "1022", gt_root, "AG_ENGINEERING_MAIN_MTR",
    #                      mongo_client, out_dir)
    # plot_avg_voltage_thd(start_ts_s, end_ts_s, "1022", gt_root, "AG_ENGINEERING_MCC_MTR",
    #                      mongo_client, out_dir)
    #
    # # 1023
    # # plot_avg_voltage_thd(start_ts_s, end_ts_s, "1023", gt_root, "LAW_LIB_MAIN_MTR",
    # #                mongo_client, out_dir)
    #
    # # 1025
    # # plot_avg_voltage_thd(start_ts_s, end_ts_s, "1025", gt_root, "KENNEDY_THEATRE_MAIN_MTR",
    # #                mongo_client, out_dir)

