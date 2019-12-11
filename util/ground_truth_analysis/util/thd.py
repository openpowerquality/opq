import datetime
from typing import *

import matplotlib.pyplot as plt
import numpy as np
import pymongo
import pymongo.database

import util
import util.align_data as align
import util.io as io

AVG_VOLTAGE_THD: str = "AVG_VOLTAGE_THD"
VOLAGE_CN_THD: str = "VOLAGE_CN_THD" # NOT A TYPO!!! THIS IS WHAT THEIR API EXPOSES FOR SOME METERS!
VOLTAGE_AN_THD: str = "VOLTAGE_AN_THD"
VOLTAGE_BN_THD: str = "VOLTAGE_BN_THD"
VOLTAGE_CN_THD: str = "VOLTAGE_CN_THD"

THD_FEATURES: List[str] = [AVG_VOLTAGE_THD, VOLAGE_CN_THD, VOLTAGE_AN_THD, VOLTAGE_BN_THD, VOLTAGE_CN_THD]


def plot_thd(opq_start_ts_s: int,
             opq_end_ts_s: int,
             opq_box_id: str,
             ground_truth_root: str,
             uhm_sensor: str,
             uhm_feature: str,
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
    opq_trends: List[Dict] = list(cursor)

    ground_truth_path: str = f"{ground_truth_root}/{uhm_sensor}/{uhm_feature}"
    uhm_data_points: List[io.DataPoint] = io.parse_file(ground_truth_path)

    aligned_opq_dts, aligned_opq_vs, aligned_uhm_dts, aligned_uhm_vs = align.align_data_by_min(
        opq_trends,
        uhm_data_points,
        lambda trend: datetime.datetime.utcfromtimestamp(trend["timestamp_ms"] / 1000.0),
        lambda data_point: datetime.datetime.utcfromtimestamp(data_point.ts_s),
        lambda trend: trend["thd"]["average"] * 100.0,
        lambda data_point: data_point.avg_v
    )

    aligned_opq_thds = np.array(aligned_opq_vs)
    aligned_uhm_thds = np.array(aligned_uhm_vs)

    min_y = min(aligned_opq_thds.min(), aligned_uhm_thds.min())
    max_y = max(aligned_opq_thds.max(), aligned_uhm_thds.max())

    fig, ax = plt.subplots(3, 1, figsize=(16, 9), sharex="all")
    fig: plt.Figure = fig
    ax: List[plt.Axes] = ax

    # OPQ
    ax_opq = ax[0]
    ax_opq.plot(aligned_opq_dts, aligned_opq_thds, label=f"Trends (OPQ Box {opq_box_id})")
    ax_opq.set_ylim(ymin=min_y, ymax=max_y)
    ax_opq.set_ylabel("% THD")
    ax_opq.set_title(f"OPQ Box {opq_box_id} Mean={aligned_opq_thds.mean()} Std={aligned_opq_thds.std()}")
    ax_opq.legend()

    # UHM
    ax_uhm = ax[1]
    ax_uhm.plot(aligned_uhm_dts, aligned_uhm_thds, label=f"Ground Truth ({uhm_sensor})")
    ax_uhm.set_ylim(ymin=min_y, ymax=max_y)
    ax_uhm.set_ylabel("% THD")
    ax_uhm.set_title(f"UHM Meter {uhm_sensor} Mean={aligned_uhm_thds.mean()} Std={aligned_uhm_thds.std()}")
    ax_uhm.legend()

    # Diff
    ax_diff = ax[2]
    diff: np.ndarray = aligned_opq_thds - aligned_uhm_thds
    ax_diff.plot(aligned_opq_dts, diff, label=f"Diff")
    ax_diff.legend()
    ax_diff.set_ylabel("Difference")
    ax_diff.set_title(f"Difference ({opq_box_id} - {uhm_sensor})  Mean={diff.mean()} Std={diff.std()}")

    ax_diff.set_ylabel("% THD Diff)")
    ax_diff.set_xlabel("Time (UTC)")

    fig.suptitle(
        f"THD Ground Truth Comparison ({uhm_feature}): {opq_box_id} vs {uhm_sensor} {aligned_opq_dts[0].strftime('%Y-%m-%d')} to "
        f"{aligned_opq_dts[-1].strftime('%Y-%m-%d')}")

    fig.savefig(f"{out_dir}/thd_{uhm_feature}_{opq_box_id}_{uhm_sensor}.png")


def compare_thds(opq_start_ts_s: int,
                 opq_end_ts_s: int,
                 ground_truth_root: str,
                 mongo_client: pymongo.MongoClient,
                 out_dir: str) -> None:
    for opq_box, uhm_meters in util.opq_box_to_uhm_meters.items():
        for uhm_meter in uhm_meters:
            for uhm_feature in THD_FEATURES:
                try:
                    print(f"plot_thd {opq_box} {uhm_meter} {uhm_feature}")
                    plot_thd(opq_start_ts_s, opq_end_ts_s, opq_box, ground_truth_root, uhm_meter, uhm_feature, mongo_client,
                             out_dir)
                except Exception as e:
                    print(e, "...ignoring...")
