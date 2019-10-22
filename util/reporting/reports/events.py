import typing

import gridfs
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


def plot_event(event_id: int,
               report_dir: str,
               mongo_client: pymongo.MongoClient):
    fs = gridfs.GridFS(mongo_client.opq)

    box_events_coll = mongo_client.opq.box_events
    box_events = list(box_events_coll.find({"event_id": event_id},
                                           projection={"_id": False,
                                                       "box_id": True,
                                                       "event_id": True,
                                                       "data_fs_filename": True}))

    fig, ax = plt.subplots(len(box_events), 1, sharex=True, figsize=(16,20))

    for i in range(len(box_events)):
        calib_constant = mongo_client.opq.opq_boxes.find_one({"box_id": box_events[i]["box_id"]},
                                                            projection={"_id": False,
                                                                        "box_id": True,
                                                                        "calibration_constant": True})["calibration_constant"]
        data = fs.find_one({"filename": box_events[i]["data_fs_filename"]}).read()
        data = to_s16bit(data).astype(np.int64) / calib_constant
        data = data[300:450]
        ax[i].plot(range(len(data)), data)

    plt.show()

    print(box_events)


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

    for event in events:
        if not reports.any_of_in(box_ids, event["boxes_triggered"]):
            continue

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
    plot_event(172509, ".", pymongo.MongoClient())
