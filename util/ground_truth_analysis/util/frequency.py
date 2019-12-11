import datetime
from typing import *

import matplotlib.pyplot as plt
import numpy as np
import pymongo
import pymongo.database

import util.align_data as align
import util.io as io
import util


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
    opq_trends: List[Dict] = list(cursor)

    ground_truth_path: str = f"{ground_truth_root}/{uhm_sensor}/Frequency"
    uhm_data_points: List[io.DataPoint] = io.parse_file(ground_truth_path)

    aligned_opq_dts, aligned_opq_vs, aligned_uhm_dts, aligned_uhm_vs = align.align_data_by_min(
        opq_trends,
        uhm_data_points,
        lambda trend: datetime.datetime.utcfromtimestamp(trend["timestamp_ms"] / 1000.0),
        lambda data_point: datetime.datetime.utcfromtimestamp(data_point.ts_s),
        lambda trend: trend["frequency"]["average"],
        lambda data_point: data_point.avg_v
    )

    aligned_opq_freqs = np.array(aligned_opq_vs)
    aligned_uhm_freqs = np.array(aligned_uhm_vs)

    min_y = min(aligned_opq_freqs.min(), aligned_uhm_freqs.min())
    max_y = max(aligned_opq_freqs.max(), aligned_uhm_freqs.max())

    fig, ax = plt.subplots(3, 1, figsize=(16, 9), sharex="all")
    # noinspection Mypy
    fig: plt.Figure = fig
    # noinspection Mypy
    ax: List[plt.Axes] = ax

    # OPQ
    ax_opq = ax[0]
    ax_opq.plot(aligned_opq_dts, aligned_opq_freqs, label=f"Trends (OPQ Box {opq_box_id})")
    ax_opq.set_ylim(ymin=min_y, ymax=max_y)
    ax_opq.set_ylabel("Frequency (Hz)")
    ax_opq.set_title(f"OPQ Box {opq_box_id} Mean={aligned_opq_freqs.mean()} Std={aligned_opq_freqs.std()}")
    ax_opq.legend()

    # UHM
    ax_uhm = ax[1]
    ax_uhm.plot(aligned_uhm_dts, aligned_uhm_freqs, label=f"Ground Truth ({uhm_sensor})")
    ax_uhm.set_ylim(ymin=min_y, ymax=max_y)
    ax_uhm.set_ylabel("Frequency (Hz)")
    ax_uhm.set_title(f"UHM Meter {uhm_sensor} Mean={aligned_uhm_freqs.mean()} Std={aligned_uhm_freqs.std()}")
    ax_uhm.legend()

    # Diff
    ax_diff = ax[2]
    diff: np.ndarray = aligned_opq_freqs - aligned_uhm_freqs
    ax_diff.plot(aligned_opq_dts, diff, label=f"Diff")
    ax_diff.legend()
    ax_diff.set_ylabel("Difference")
    ax_diff.set_title(f"Difference ({opq_box_id} - {uhm_sensor})  Mean={diff.mean()} Std={diff.std()}")

    ax_diff.set_ylabel("Frequency Diff (Hz)")
    ax_diff.set_xlabel("Time (UTC)")

    fig.suptitle(
        f"Frequency Ground Truth Comparison: {opq_box_id} vs {uhm_sensor} {aligned_opq_dts[0].strftime('%Y-%m-%d')} to "
        f"{aligned_opq_dts[-1].strftime('%Y-%m-%d')}")

    fig.savefig(f"{out_dir}/f_{opq_box_id}_{uhm_sensor}.png")


def compare_frequencies(opq_start_ts_s: int,
                        opq_end_ts_s: int,
                        ground_truth_root: str,
                        mongo_client: pymongo.MongoClient,
                        out_dir: str) -> None:
    for opq_box, uhm_meters in util.opq_box_to_uhm_meters.items():
        for uhm_meter in uhm_meters:
            try:
                print(f"plot_frequency {opq_box} {uhm_meter}")
                plot_frequency(opq_start_ts_s, opq_end_ts_s, opq_box, ground_truth_root, uhm_meter, mongo_client,
                               out_dir)
            except Exception as e:
                print(e, "...ignoring...")
