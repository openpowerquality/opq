import datetime
import math
import typing

import gridfs
import matplotlib.dates as md
import matplotlib.pyplot as plt
import numpy as np
import pymongo

import reports


def to_s16bit(data: bytes) -> np.ndarray:
    """
    Converts raw bytes into an array of 16 bit integers.
    :param data:
    :return:
    """
    return np.frombuffer(data, np.int16)


def ms_to_sample(ms: float) -> float:
    return ms * 12


def sample_to_ms(sample: int) -> float:
    return sample / 12.0

def sample_to_us(sample: int) -> float:
    return sample / 12_000.0

def ms_to_us(ms: float) -> float:
    return ms * 1000.0


def plot_event_stacked(event_id: int,
                       report_dir: str,
                       mongo_client: pymongo.MongoClient,
                       include_only_boxes: typing.List[str] = [],
                       range_ms: typing.Optional[typing.Tuple[float, float]] = None):
    fs = gridfs.GridFS(mongo_client.opq)

    box_events_coll = mongo_client.opq.box_events
    box_events = list(box_events_coll.find({"event_id": event_id},
                                           projection={"_id": False,
                                                       "box_id": True,
                                                       "event_id": True,
                                                       "data_fs_filename": True,
                                                       "event_start_timestamp_ms": True}))

    if len(include_only_boxes) > 0:
        box_events = list(filter(lambda box_event: box_event["box_id"] in include_only_boxes, box_events))

    box_events = sorted(box_events, key=lambda box_event: box_event["box_id"])
    start_ms = box_events[0]["event_start_timestamp_ms"]
    start_dt = datetime.datetime.utcfromtimestamp(start_ms / 1000.0)

    # fig, ax = plt.subplots(len(box_events), 1, sharex=True, figsize=(16, 20))
    fig, ax = plt.subplots(len(box_events), 1, sharex=True, figsize=(14, 21))
    fig.suptitle("Event #%d @ %s UTC" % (event_id, start_dt.strftime("%Y-%m-%d %H:%M:%S")))

    min_y = 9999999999999999
    max_y = -min_y
    min_x = datetime.datetime.utcnow()
    max_x = datetime.datetime(1970, 1, 1)
    for i in range(len(box_events)):
        calib_constant = mongo_client.opq.opq_boxes.find_one({"box_id": box_events[i]["box_id"]},
                                                             projection={"_id": False,
                                                                         "box_id": True,
                                                                         "calibration_constant": True})[
            "calibration_constant"]

        y_values = fs.find_one({"filename": box_events[i]["data_fs_filename"]}).read()
        y_values = to_s16bit(y_values).astype(np.int64) / calib_constant
        event_start_ms = box_events[i]["event_start_timestamp_ms"]
        x_values = list(map(lambda sample: sample_to_ms(sample) + event_start_ms, range(len(y_values))))
        x_values = list(map(lambda x: datetime.datetime.utcfromtimestamp(x / 1000.0), x_values))


        if range_ms is not None:
            start_sample = ms_to_sample(range_ms[0])
            end_sample = ms_to_sample(range_ms[1])
            x_values = x_values[start_sample:end_sample]
            y_values = y_values[start_sample:end_sample]

        min_y = min(min_y, min(y_values))
        max_y = max(max_y, max(y_values))
        min_x = min(min_x, min(x_values))
        max_x = max(max_x, max(x_values))

        ax[i].plot(x_values, y_values)
        ax[i].set_title("OPQ Box %s (%s)" % (box_events[i]["box_id"], reports.box_to_location[box_events[i]["box_id"]]))
        ax[i].set_ylabel("Voltage")

    for a in ax:
        a.set_ylim(ymin=min_y - 5, ymax=max_y + 5)
        a.set_xlim(xmin=min_x, xmax=max_x)

    ax[-1].set_xlabel("Time UTC (MM:SS.$\mu$S)")
    ax[-1].xaxis.set_major_formatter(md.DateFormatter('%M:%S.%f'))

    plt.savefig("%s/event_%d.png" % (report_dir, event_id))


def plot_events(start_time_s: int,
                end_time_s: int,
                report_dir: str,
                mongo_client: pymongo.MongoClient):
    events_coll = mongo_client.opq.events
    box_ids = [k for k in reports.box_to_location]
    events = events_coll.find({"target_event_start_timestamp_ms": {"$gte": start_time_s * 1000.0,
                                                                   "$lte": end_time_s * 1000.0}})

    bins = set(map(reports.fmt_ts_by_hour, list(range(start_time_s, end_time_s))))
    bins = list(bins)
    bins.sort()

    box_to_bin_to_events = {}

    for box in box_ids:
        box_to_bin_to_events[box] = {}
        for bin in bins:
            box_to_bin_to_events[box][bin] = 0

    with open("%s/events.txt" % report_dir, "a") as fout:
        for event in events:
            if not reports.any_of_in(box_ids, event["boxes_triggered"]):
                continue
            fout.write("%d\n" % event["event_id"])
            dt_bin = reports.fmt_ts_by_hour(int(event["target_event_start_timestamp_ms"] / 1000.0))
            for box in event["boxes_received"]:
                if box in box_ids:
                    box_to_bin_to_events[box][dt_bin] += 1

    def da_bottom(datasets: typing.List[np.ndarray], i: int) -> np.ndarray:
        d = np.zeros(len(datasets[i]))
        for j in range(i):
            d += datasets[j]
        return d

    plt.figure(figsize=(16, 9))
    labels = []
    datasets = []
    for box in box_to_bin_to_events:
        labels.append("Box %s (%s)" % (box, reports.box_to_location[box]))
        datasets.append(np.array(list(box_to_bin_to_events[box].values())))

    for i in range(len(datasets)):
        if i == 0:
            plt.bar(list(range(len(bins))), datasets[i], label=labels[i])
        else:
            plt.bar(list(range(len(bins))), datasets[i], bottom=da_bottom(datasets, i), label=labels[i])

    bin_to_total = {}
    for box in box_to_bin_to_events:
        for bin in box_to_bin_to_events[box]:
            if bin not in bin_to_total:
                bin_to_total[bin] = 0
            bin_to_total[bin] += box_to_bin_to_events[box][bin]

    plt.xticks(list(range(len(bins))), bins)
    plt.ylabel("# Events")
    plt.xlabel("Day")
    plt.title("Events per Day per Device (%s - %s)" % (bins[0], bins[-1]))
    plt.legend()
    fig_title = "events-%s-%s.png" % (bins[0], bins[-1])
    plt.savefig("%s/%s" % (report_dir, fig_title))
    print("Produced %s" % fig_title)
    return fig_title


def event_stats(start_time_s: int,
                end_time_s: int,
                mongo_client: pymongo.MongoClient):
    box_to_total_events: typing.Dict[str, int] = {}

    events_coll = mongo_client.opq.events
    box_ids = [k for k in reports.box_to_location]
    events = events_coll.find({"target_event_start_timestamp_ms": {"$gte": start_time_s * 1000.0,
                                                                   "$lte": end_time_s * 1000.0}})
    for event in events:
        if not reports.any_of_in(box_ids, event["boxes_triggered"]):
            continue

        for box in event["boxes_received"]:
            if box not in box_ids:
                continue
            if box not in box_to_total_events:
                box_to_total_events[box] = 0
            box_to_total_events[box] += 1

    return {"total_events": sum(box_to_total_events.values()),
            "events_per_box": box_to_total_events}


if __name__ == "__main__":
    plot_event_stacked(171418, ".", pymongo.MongoClient(),
                        range_ms=(200,700)
                       )
