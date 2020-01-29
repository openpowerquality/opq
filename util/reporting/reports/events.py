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


def plot_single_event(event_id: int,
                      report_dir: str,
                      mongo_client: pymongo.MongoClient,
                      box_id: str,
                      range_samples: typing.Optional[typing.Tuple[float, float]] = None):
    fs = gridfs.GridFS(mongo_client.opq)
    box_events_coll: pymongo.collection.Collection = mongo_client.opq.box_events
    query = {"event_id": event_id,
             "box_id": box_id}
    projection = {"_id": False,
                  "box_id": True,
                  "event_id": True,
                  "data_fs_filename": True,
                  "event_start_timestamp_ms": True}

    box_event = box_events_coll.find_one(query, projection=projection)

    if box_event is not None:
        fig, ax = plt.subplots(1, 1, figsize=(16, 9))
        event_start_ms = box_event["event_start_timestamp_ms"]
        calib_constant = mongo_client.opq.opq_boxes.find_one({"box_id": box_id},
                                                             projection={"_id": False,
                                                                         "box_id": True,
                                                                         "calibration_constant": True})[
            "calibration_constant"]


        waveform = fs.find_one({"filename": box_event["data_fs_filename"]}).read()
        waveform = to_s16bit(waveform).astype(np.int64) / calib_constant
        x_values = [event_start_ms + reports.sample_to_ms(i) for i in range(0, len(waveform))]
        x_values = list(map(lambda ts: datetime.datetime.utcfromtimestamp(ts / 1000.0), x_values))

        start_idx = 0 if range_samples is None else range_samples[0]
        end_idx = len(waveform) if range_samples is None else range_samples[1]

        waveform = waveform[start_idx:end_idx]
        x_values = x_values[start_idx:end_idx]

        fig.suptitle("OPQ Event #%d OPQ Box %s (%s) @ %s" % (
            event_id,
            box_id,
            reports.box_to_location[box_id],
            x_values[0].strftime("%Y-%m-%d %H:%M")
        ))
        ax.plot(x_values, waveform, color="blue")
        ax.set_xlabel("Date/Time UTC")
        ax.set_ylabel("Voltage")
        ax.tick_params(axis="y", colors="blue")
        ax.yaxis.label.set_color("blue")

        ax2 = ax.twinx()
        vrms_y_values = reports.vrms_waveform(waveform)
        print(event_id, vrms_y_values.min())
        vrms_x_values = x_values[0::200]
        ax2.plot(vrms_x_values, vrms_y_values, color="red")
        ax2.tick_params(axis="y", colors="red")
        ax2.yaxis.label.set_color("red")
        ax2.set_ylabel("$V_{RMS}$")

        plt.savefig("%s/event-single-%d.png" % (report_dir, event_id))


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
    # plot_single_event(262503,
    #                   "/Users/anthony/Development/opq/util/reporting/report_1572343200_1572948000",
    #                   pymongo.MongoClient(),
    #                   "1021",
    #                   (375_000, 425_000))
    mongo_client = pymongo.MongoClient()
    out_dir = "."
    plot_single_event(460032, out_dir, mongo_client, '1021', None)
    plot_single_event(458244, out_dir, mongo_client, '1021', None)
    plot_single_event(458762, out_dir, mongo_client, '1021', None)
    plot_single_event(461586, out_dir, mongo_client, '1021', None)
    plot_single_event(458003, out_dir, mongo_client, '1021', None)
    plot_single_event(458772, out_dir, mongo_client, '1021', None)
    plot_single_event(458773, out_dir, mongo_client, '1021', None)
    plot_single_event(459284, out_dir, mongo_client, '1021', None)
    plot_single_event(459285, out_dir, mongo_client, '1021', None)
    plot_single_event(458515, out_dir, mongo_client, '1021', None)
    plot_single_event(461587, out_dir, mongo_client, '1021', None)
    plot_single_event(458518, out_dir, mongo_client, '1021', None)
    plot_single_event(460827, out_dir, mongo_client, '1021', None)
    plot_single_event(460828, out_dir, mongo_client, '1021', None)
    plot_single_event(460829, out_dir, mongo_client, '1021', None)
    plot_single_event(458786, out_dir, mongo_client, '1021', None)
    plot_single_event(458787, out_dir, mongo_client, '1021', None)
    plot_single_event(461347, out_dir, mongo_client, '1021', None)
    plot_single_event(461348, out_dir, mongo_client, '1021', None)
    plot_single_event(459817, out_dir, mongo_client, '1021', None)
    plot_single_event(460585, out_dir, mongo_client, '1021', None)
    plot_single_event(460586, out_dir, mongo_client, '1021', None)
    plot_single_event(461617, out_dir, mongo_client, '1021', None)
    plot_single_event(461618, out_dir, mongo_client, '1021', None)
    plot_single_event(460598, out_dir, mongo_client, '1021', None)
    plot_single_event(460599, out_dir, mongo_client, '1021', None)
    plot_single_event(457795, out_dir, mongo_client, '1021', None)
    plot_single_event(457796, out_dir, mongo_client, '1021', None)
    plot_single_event(460356, out_dir, mongo_client, '1021', None)
    plot_single_event(460357, out_dir, mongo_client, '1021', None)
    plot_single_event(459076, out_dir, mongo_client, '1021', None)
    plot_single_event(459078, out_dir, mongo_client, '1021', None)
    plot_single_event(459871, out_dir, mongo_client, '1021', None)
    plot_single_event(459617, out_dir, mongo_client, '1021', None)
    plot_single_event(459619, out_dir, mongo_client, '1021', None)
    plot_single_event(460651, out_dir, mongo_client, '1021', None)
    plot_single_event(460652, out_dir, mongo_client, '1021', None)
    plot_single_event(461163, out_dir, mongo_client, '1021', None)
    plot_single_event(461164, out_dir, mongo_client, '1021', None)
    plot_single_event(461165, out_dir, mongo_client, '1021', None)
    plot_single_event(461166, out_dir, mongo_client, '1021', None)
    plot_single_event(459381, out_dir, mongo_client, '1021', None)
    plot_single_event(459382, out_dir, mongo_client, '1021', None)
    plot_single_event(460919, out_dir, mongo_client, '1021', None)
    plot_single_event(460918, out_dir, mongo_client, '1021', None)
    plot_single_event(459128, out_dir, mongo_client, '1021', None)
    plot_single_event(459129, out_dir, mongo_client, '1021', None)
    plot_single_event(461447, out_dir, mongo_client, '1021', None)
    plot_single_event(461448, out_dir, mongo_client, '1021', None)
    plot_single_event(460187, out_dir, mongo_client, '1021', None)
    plot_single_event(460188, out_dir, mongo_client, '1021', None)
    plot_single_event(459174, out_dir, mongo_client, '1021', None)
    plot_single_event(460455, out_dir, mongo_client, '1021', None)
    plot_single_event(458920, out_dir, mongo_client, '1021', None)
    plot_single_event(460456, out_dir, mongo_client, '1021', None)
    plot_single_event(459175, out_dir, mongo_client, '1021', None)
    plot_single_event(459948, out_dir, mongo_client, '1021', None)
    plot_single_event(459949, out_dir, mongo_client, '1021', None)
    plot_single_event(460718, out_dir, mongo_client, '1021', None)
    plot_single_event(460719, out_dir, mongo_client, '1021', None)
    plot_single_event(460464, out_dir, mongo_client, '1021', None)
    plot_single_event(460465, out_dir, mongo_client, '1021', None)
    plot_single_event(460720, out_dir, mongo_client, '1021', None)
    plot_single_event(460721, out_dir, mongo_client, '1021', None)
    plot_single_event(460722, out_dir, mongo_client, '1021', None)
    plot_single_event(460723, out_dir, mongo_client, '1021', None)
    plot_single_event(461588, out_dir, mongo_client, '1021', None)
    plot_single_event(459457, out_dir, mongo_client, '1021', None)
    plot_single_event(459458, out_dir, mongo_client, '1021', None)
    plot_single_event(461251, out_dir, mongo_client, '1021', None)
    plot_single_event(461252, out_dir, mongo_client, '1021', None)
    plot_single_event(459216, out_dir, mongo_client, '1021', None)
    plot_single_event(459217, out_dir, mongo_client, '1021', None)
    plot_single_event(461524, out_dir, mongo_client, '1021', None)
    plot_single_event(459739, out_dir, mongo_client, '1021', None)
    plot_single_event(458724, out_dir, mongo_client, '1021', None)
    plot_single_event(460517, out_dir, mongo_client, '1021', None)
    plot_single_event(460518, out_dir, mongo_client, '1021', None)
    plot_single_event(458725, out_dir, mongo_client, '1021', None)
    plot_single_event(461033, out_dir, mongo_client, '1021', None)
    plot_single_event(461034, out_dir, mongo_client, '1021', None)
    plot_single_event(460030, out_dir, mongo_client, '1021', None)
    plot_single_event(460031, out_dir, mongo_client, '1021', None)
    plot_single_event(460801, out_dir, mongo_client, '1021', None)
    plot_single_event(461638, out_dir, mongo_client, '1021', None)
    plot_single_event(461639, out_dir, mongo_client, '1021', None)
    plot_single_event(458824, out_dir, mongo_client, '1021', None)
    plot_single_event(460795, out_dir, mongo_client, '1021', None)
    plot_single_event(461620, out_dir, mongo_client, '1021', None)
    plot_single_event(461621, out_dir, mongo_client, '1021', None)
    plot_single_event(460789, out_dir, mongo_client, '1021', None)
    plot_single_event(460792, out_dir, mongo_client, '1021', None)
    plot_single_event(459995, out_dir, mongo_client, '1021', None)
    plot_single_event(459998, out_dir, mongo_client, '1021', None)
    plot_single_event(461731, out_dir, mongo_client, '1021', None)
    plot_single_event(461732, out_dir, mongo_client, '1021', None)
    plot_single_event(461733, out_dir, mongo_client, '1021', None)
    plot_single_event(461734, out_dir, mongo_client, '1021', None)
    plot_single_event(461645, out_dir, mongo_client, '1021', None)
    plot_single_event(461646, out_dir, mongo_client, '1021', None)
    plot_single_event(461647, out_dir, mongo_client, '1021', None)
    plot_single_event(461648, out_dir, mongo_client, '1021', None)
    plot_single_event(461773, out_dir, mongo_client, '1021', None)
    plot_single_event(458770, out_dir, mongo_client, '1021', None)
    plot_single_event(461774, out_dir, mongo_client, '1021', None)
    plot_single_event(461775, out_dir, mongo_client, '1021', None)
    plot_single_event(461776, out_dir, mongo_client, '1021', None)
    plot_single_event(461777, out_dir, mongo_client, '1021', None)
    plot_single_event(461778, out_dir, mongo_client, '1021', None)
    plot_single_event(461824, out_dir, mongo_client, '1021', None)
    plot_single_event(461825, out_dir, mongo_client, '1021', None)
    plot_single_event(461730, out_dir, mongo_client, '1021', None)
    plot_single_event(461935, out_dir, mongo_client, '1021', None)
    plot_single_event(461936, out_dir, mongo_client, '1021', None)
    plot_single_event(461909, out_dir, mongo_client, '1021', None)
    plot_single_event(461911, out_dir, mongo_client, '1021', None)
    plot_single_event(461823, out_dir, mongo_client, '1021', None)
    plot_single_event(461727, out_dir, mongo_client, '1021', None)
    plot_single_event(459169, out_dir, mongo_client, '1021', None)
    plot_single_event(462030, out_dir, mongo_client, '1021', None)
    plot_single_event(462031, out_dir, mongo_client, '1021', None)
    plot_single_event(462045, out_dir, mongo_client, '1021', None)
    plot_single_event(462062, out_dir, mongo_client, '1021', None)
    plot_single_event(462063, out_dir, mongo_client, '1021', None)
    plot_single_event(459161, out_dir, mongo_client, '1021', None)
    plot_single_event(462102, out_dir, mongo_client, '1021', None)
    plot_single_event(462103, out_dir, mongo_client, '1021', None)
    plot_single_event(462104, out_dir, mongo_client, '1021', None)
    plot_single_event(462105, out_dir, mongo_client, '1021', None)
    plot_single_event(459162, out_dir, mongo_client, '1021', None)
    plot_single_event(459163, out_dir, mongo_client, '1021', None)
    plot_single_event(459164, out_dir, mongo_client, '1021', None)
    plot_single_event(462118, out_dir, mongo_client, '1021', None)
    plot_single_event(462144, out_dir, mongo_client, '1021', None)
    plot_single_event(462259, out_dir, mongo_client, '1021', None)
    plot_single_event(462260, out_dir, mongo_client, '1021', None)
    plot_single_event(462270, out_dir, mongo_client, '1021', None)
    plot_single_event(462261, out_dir, mongo_client, '1021', None)
    plot_single_event(462262, out_dir, mongo_client, '1021', None)
    plot_single_event(462271, out_dir, mongo_client, '1021', None)
    plot_single_event(462272, out_dir, mongo_client, '1021', None)
    plot_single_event(462273, out_dir, mongo_client, '1021', None)
    plot_single_event(462274, out_dir, mongo_client, '1021', None)
    plot_single_event(462275, out_dir, mongo_client, '1021', None)
    plot_single_event(462328, out_dir, mongo_client, '1021', None)
    plot_single_event(462276, out_dir, mongo_client, '1021', None)
    plot_single_event(462277, out_dir, mongo_client, '1021', None)
    plot_single_event(462327, out_dir, mongo_client, '1021', None)
    plot_single_event(462392, out_dir, mongo_client, '1021', None)
    plot_single_event(462338, out_dir, mongo_client, '1021', None)
    plot_single_event(462287, out_dir, mongo_client, '1021', None)
    plot_single_event(462391, out_dir, mongo_client, '1021', None)
    plot_single_event(462568, out_dir, mongo_client, '1021', None)
    plot_single_event(462467, out_dir, mongo_client, '1021', None)
    plot_single_event(462468, out_dir, mongo_client, '1021', None)
    plot_single_event(462567, out_dir, mongo_client, '1021', None)
    plot_single_event(462596, out_dir, mongo_client, '1021', None)
    plot_single_event(462597, out_dir, mongo_client, '1021', None)
    plot_single_event(462283, out_dir, mongo_client, '1021', None)
    plot_single_event(462714, out_dir, mongo_client, '1021', None)
    plot_single_event(462716, out_dir, mongo_client, '1021', None)
    plot_single_event(462860, out_dir, mongo_client, '1021', None)
    plot_single_event(462862, out_dir, mongo_client, '1021', None)
    plot_single_event(463028, out_dir, mongo_client, '1021', None)
    plot_single_event(462973, out_dir, mongo_client, '1021', None)
    plot_single_event(462974, out_dir, mongo_client, '1021', None)
    plot_single_event(463107, out_dir, mongo_client, '1021', None)
    plot_single_event(463059, out_dir, mongo_client, '1021', None)
    plot_single_event(463060, out_dir, mongo_client, '1021', None)
    plot_single_event(463108, out_dir, mongo_client, '1021', None)
    plot_single_event(463206, out_dir, mongo_client, '1021', None)
    plot_single_event(463207, out_dir, mongo_client, '1021', None)
    plot_single_event(463352, out_dir, mongo_client, '1021', None)
    plot_single_event(463459, out_dir, mongo_client, '1021', None)
    plot_single_event(463460, out_dir, mongo_client, '1021', None)
    plot_single_event(463351, out_dir, mongo_client, '1021', None)
    plot_single_event(463594, out_dir, mongo_client, '1021', None)
    plot_single_event(463595, out_dir, mongo_client, '1021', None)
    plot_single_event(463457, out_dir, mongo_client, '1021', None)
    plot_single_event(463458, out_dir, mongo_client, '1021', None)
    plot_single_event(463666, out_dir, mongo_client, '1021', None)
    plot_single_event(461352, out_dir, mongo_client, '1021', None)
    plot_single_event(463725, out_dir, mongo_client, '1021', None)
    plot_single_event(463726, out_dir, mongo_client, '1021', None)
    plot_single_event(463817, out_dir, mongo_client, '1021', None)
    plot_single_event(463815, out_dir, mongo_client, '1021', None)
    plot_single_event(463942, out_dir, mongo_client, '1021', None)
    plot_single_event(463943, out_dir, mongo_client, '1021', None)
    plot_single_event(461659, out_dir, mongo_client, '1021', None)
    plot_single_event(464042, out_dir, mongo_client, '1021', None)
    plot_single_event(464043, out_dir, mongo_client, '1021', None)
    plot_single_event(464048, out_dir, mongo_client, '1021', None)
    plot_single_event(464047, out_dir, mongo_client, '1021', None)
    plot_single_event(464202, out_dir, mongo_client, '1021', None)
    plot_single_event(464484, out_dir, mongo_client, '1021', None)
    plot_single_event(464485, out_dir, mongo_client, '1021', None)
    plot_single_event(464551, out_dir, mongo_client, '1021', None)
    plot_single_event(464552, out_dir, mongo_client, '1021', None)
    plot_single_event(464071, out_dir, mongo_client, '1021', None)
    plot_single_event(464072, out_dir, mongo_client, '1021', None)
    plot_single_event(464555, out_dir, mongo_client, '1021', None)
    plot_single_event(464556, out_dir, mongo_client, '1021', None)
    plot_single_event(463663, out_dir, mongo_client, '1021', None)
    plot_single_event(463664, out_dir, mongo_client, '1021', None)
    plot_single_event(464056, out_dir, mongo_client, '1021', None)
    plot_single_event(464057, out_dir, mongo_client, '1021', None)
    plot_single_event(464585, out_dir, mongo_client, '1021', None)
    plot_single_event(464668, out_dir, mongo_client, '1021', None)
    plot_single_event(464669, out_dir, mongo_client, '1021', None)
    plot_single_event(464607, out_dir, mongo_client, '1021', None)
    plot_single_event(464724, out_dir, mongo_client, '1021', None)
    plot_single_event(464725, out_dir, mongo_client, '1021', None)
    plot_single_event(464881, out_dir, mongo_client, '1021', None)
    plot_single_event(464882, out_dir, mongo_client, '1021', None)
    plot_single_event(464779, out_dir, mongo_client, '1021', None)
    plot_single_event(464918, out_dir, mongo_client, '1021', None)
    plot_single_event(465208, out_dir, mongo_client, '1021', None)
    plot_single_event(465343, out_dir, mongo_client, '1021', None)
    plot_single_event(465428, out_dir, mongo_client, '1021', None)
    plot_single_event(465429, out_dir, mongo_client, '1021', None)
    plot_single_event(465430, out_dir, mongo_client, '1021', None)
    plot_single_event(465431, out_dir, mongo_client, '1021', None)
    plot_single_event(465457, out_dir, mongo_client, '1021', None)
    plot_single_event(465511, out_dir, mongo_client, '1021', None)
    plot_single_event(465546, out_dir, mongo_client, '1021', None)
    plot_single_event(465563, out_dir, mongo_client, '1021', None)
    plot_single_event(465666, out_dir, mongo_client, '1021', None)
    plot_single_event(465651, out_dir, mongo_client, '1021', None)
    plot_single_event(465773, out_dir, mongo_client, '1021', None)
    plot_single_event(464912, out_dir, mongo_client, '1021', None)
    plot_single_event(465893, out_dir, mongo_client, '1021', None)
    plot_single_event(465829, out_dir, mongo_client, '1021', None)
    plot_single_event(466032, out_dir, mongo_client, '1021', None)
    plot_single_event(466033, out_dir, mongo_client, '1021', None)
    plot_single_event(466149, out_dir, mongo_client, '1021', None)
    plot_single_event(466150, out_dir, mongo_client, '1021', None)
    plot_single_event(464913, out_dir, mongo_client, '1021', None)
    plot_single_event(466458, out_dir, mongo_client, '1021', None)
    plot_single_event(466459, out_dir, mongo_client, '1021', None)
    plot_single_event(466250, out_dir, mongo_client, '1021', None)
    plot_single_event(466251, out_dir, mongo_client, '1021', None)
    plot_single_event(466565, out_dir, mongo_client, '1021', None)
    plot_single_event(466566, out_dir, mongo_client, '1021', None)
    plot_single_event(466720, out_dir, mongo_client, '1021', None)
    plot_single_event(466682, out_dir, mongo_client, '1021', None)
    plot_single_event(466683, out_dir, mongo_client, '1021', None)
    plot_single_event(466719, out_dir, mongo_client, '1021', None)
    plot_single_event(466753, out_dir, mongo_client, '1021', None)
    plot_single_event(466754, out_dir, mongo_client, '1021', None)
    plot_single_event(466756, out_dir, mongo_client, '1021', None)
    plot_single_event(466883, out_dir, mongo_client, '1021', None)
    plot_single_event(466885, out_dir, mongo_client, '1021', None)
    plot_single_event(466082, out_dir, mongo_client, '1021', None)
    plot_single_event(466083, out_dir, mongo_client, '1021', None)
    plot_single_event(467015, out_dir, mongo_client, '1021', None)
    plot_single_event(467016, out_dir, mongo_client, '1021', None)
    plot_single_event(466894, out_dir, mongo_client, '1021', None)
    plot_single_event(466895, out_dir, mongo_client, '1021', None)
    plot_single_event(467090, out_dir, mongo_client, '1021', None)
    plot_single_event(467091, out_dir, mongo_client, '1021', None)
    plot_single_event(466101, out_dir, mongo_client, '1021', None)
    plot_single_event(466236, out_dir, mongo_client, '1021', None)
    plot_single_event(466235, out_dir, mongo_client, '1021', None)
    plot_single_event(465948, out_dir, mongo_client, '1021', None)
    plot_single_event(466237, out_dir, mongo_client, '1021', None)
    plot_single_event(467363, out_dir, mongo_client, '1021', None)
    plot_single_event(467245, out_dir, mongo_client, '1021', None)
    plot_single_event(467398, out_dir, mongo_client, '1021', None)
    plot_single_event(467399, out_dir, mongo_client, '1021', None)
    plot_single_event(467530, out_dir, mongo_client, '1021', None)
    plot_single_event(467531, out_dir, mongo_client, '1021', None)
    plot_single_event(467660, out_dir, mongo_client, '1021', None)
    plot_single_event(467659, out_dir, mongo_client, '1021', None)
    plot_single_event(467605, out_dir, mongo_client, '1021', None)
    plot_single_event(467451, out_dir, mongo_client, '1021', None)
    plot_single_event(467722, out_dir, mongo_client, '1021', None)
    plot_single_event(467723, out_dir, mongo_client, '1021', None)
    plot_single_event(467667, out_dir, mongo_client, '1021', None)
    plot_single_event(467859, out_dir, mongo_client, '1021', None)
    plot_single_event(468008, out_dir, mongo_client, '1021', None)
    plot_single_event(468009, out_dir, mongo_client, '1021', None)
    plot_single_event(467904, out_dir, mongo_client, '1021', None)
    plot_single_event(468185, out_dir, mongo_client, '1021', None)
    plot_single_event(468078, out_dir, mongo_client, '1021', None)
    plot_single_event(468254, out_dir, mongo_client, '1021', None)
    plot_single_event(468457, out_dir, mongo_client, '1021', None)
    plot_single_event(468419, out_dir, mongo_client, '1021', None)
    plot_single_event(468544, out_dir, mongo_client, '1021', None)
    plot_single_event(468521, out_dir, mongo_client, '1021', None)
    plot_single_event(468642, out_dir, mongo_client, '1021', None)
    plot_single_event(468722, out_dir, mongo_client, '1021', None)
    plot_single_event(469028, out_dir, mongo_client, '1021', None)
    plot_single_event(468901, out_dir, mongo_client, '1021', None)
    plot_single_event(469069, out_dir, mongo_client, '1021', None)
    plot_single_event(469306, out_dir, mongo_client, '1021', None)
    plot_single_event(466441, out_dir, mongo_client, '1021', None)
    plot_single_event(469307, out_dir, mongo_client, '1021', None)
    plot_single_event(469509, out_dir, mongo_client, '1021', None)
    plot_single_event(469604, out_dir, mongo_client, '1021', None)
    plot_single_event(470131, out_dir, mongo_client, '1021', None)
    plot_single_event(469775, out_dir, mongo_client, '1021', None)
    plot_single_event(470380, out_dir, mongo_client, '1021', None)
    plot_single_event(470603, out_dir, mongo_client, '1021', None)
    plot_single_event(470604, out_dir, mongo_client, '1021', None)
    plot_single_event(470605, out_dir, mongo_client, '1021', None)
    plot_single_event(470606, out_dir, mongo_client, '1021', None)
    plot_single_event(470472, out_dir, mongo_client, '1021', None)
    plot_single_event(470465, out_dir, mongo_client, '1021', None)
    plot_single_event(471068, out_dir, mongo_client, '1021', None)
    plot_single_event(471169, out_dir, mongo_client, '1021', None)
    plot_single_event(470249, out_dir, mongo_client, '1021', None)
    plot_single_event(470251, out_dir, mongo_client, '1021', None)
    plot_single_event(469553, out_dir, mongo_client, '1021', None)
    plot_single_event(469714, out_dir, mongo_client, '1021', None)
    plot_single_event(471253, out_dir, mongo_client, '1021', None)
    plot_single_event(469241, out_dir, mongo_client, '1021', None)
    plot_single_event(471302, out_dir, mongo_client, '1021', None)
    plot_single_event(471483, out_dir, mongo_client, '1021', None)
    plot_single_event(471598, out_dir, mongo_client, '1021', None)
    plot_single_event(471735, out_dir, mongo_client, '1021', None)
    plot_single_event(472160, out_dir, mongo_client, '1021', None)
    plot_single_event(472036, out_dir, mongo_client, '1021', None)
    plot_single_event(471854, out_dir, mongo_client, '1021', None)
    plot_single_event(471895, out_dir, mongo_client, '1021', None)
    plot_single_event(472255, out_dir, mongo_client, '1021', None)
    plot_single_event(472424, out_dir, mongo_client, '1021', None)
    plot_single_event(472609, out_dir, mongo_client, '1021', None)
    plot_single_event(473028, out_dir, mongo_client, '1021', None)
    plot_single_event(472829, out_dir, mongo_client, '1021', None)
    plot_single_event(473309, out_dir, mongo_client, '1021', None)
    plot_single_event(473622, out_dir, mongo_client, '1021', None)
    plot_single_event(473623, out_dir, mongo_client, '1021', None)
    plot_single_event(474473, out_dir, mongo_client, '1021', None)
    plot_single_event(474734, out_dir, mongo_client, '1021', None)
    plot_single_event(473967, out_dir, mongo_client, '1021', None)
    plot_single_event(474255, out_dir, mongo_client, '1021', None)
    plot_single_event(474975, out_dir, mongo_client, '1021', None)
    plot_single_event(475560, out_dir, mongo_client, '1021', None)
    plot_single_event(475305, out_dir, mongo_client, '1021', None)
