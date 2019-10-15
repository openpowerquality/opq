"""
Some docs.
"""

import collections
import datetime
import typing

import matplotlib.dates as md
import matplotlib.pyplot as plt
import pymongo

import numpy as np


def any_of_in(a: typing.List, b: typing.List) -> bool:
    a = set(a)
    b = set(b)
    return len(a.intersection(b)) > 0


box_to_location: typing.Dict[str, str] = {
    "1000": "POST 1",
    "1001": "Hamilton",
    "1002": "POST 2",
    "1003": "LAVA Lab",
    "1005": "Parking Structure Ph II",
    "1006": "Frog 1",
    "1007": "Frog 2",
    "1008": "Mile's Office",
    "1009": "Watanabe",
    "1010": "Holmes",
    "1021": "Marine Science Building",
    "1022": "Ag. Engineering",
    "1023": "Law Library",
    "1024": "IT Building",
    "1025": "Kennedy Theater"
}


def report_stats(start_time_s: int,
                 end_time_s: int,
                 mongo_client: pymongo.MongoClient):
    box_to_total_events: typing.Dict[str, int] = {}
    box_to_total_incidents: typing.Dict[str, int] = {}
    incident_types: typing.Dict[str, int] = {}
    box_to_incidents: typing.Dict[str, typing.Dict[str, int]] = {}

    events_coll = mongo_client.opq.events
    box_ids = [k for k in box_to_location]
    events = events_coll.find({"target_event_start_timestamp_ms": {"$gte": start_time_s * 1000.0,
                                                                   "$lte": end_time_s * 1000.0}})
    for event in events:
        if not any_of_in(box_ids, event["boxes_triggered"]):
            continue

        for box in event["boxes_received"]:
            if box not in box_to_total_events:
                box_to_total_events[box] = 0
            box_to_total_events[box] += 1

    incidents_coll = mongo_client.opq.incidents
    incidents = incidents_coll.find({"start_timestamp_ms": {"$gte": start_time_s * 1000.0,
                                                            "$lte": end_time_s * 1000.0},
                                     "box_id": {"$in": box_ids}})

    for incident in incidents:
        box = incident["box_id"]
        if box not in box_to_total_incidents:
            box_to_total_incidents[box] = 0
        box_to_total_incidents[box] += 1

        for incident_type in incident["classifications"]:
            if incident_type not in incident_types:
                incident_types[incident_type] = 0
            incident_types[incident_type] += 1

            if box not in box_to_incidents:
                box_to_incidents[box] = {}
            if incident_type not in box_to_incidents[box]:
                box_to_incidents[box][incident_type] = 0

            box_to_incidents[box][incident_type] += 1

    print("total events:", sum(box_to_total_events.values()))
    print("total incidents:", sum(box_to_total_incidents.values()))
    for incident, cnt in incident_types.items():
        print("incident type: %s: %d" % (incident, cnt))
    print("box id\tlocation\ttotal events\ttotal incidents\tincident types")
    for box_id, location in box_to_location.items():
        print("%s\t%s\t%d\t%d\t%s" % (box_id,
                                      location,
                                      box_to_total_events[box_id],
                                      box_to_total_incidents[box_id],
                                      box_to_incidents[box_id]))


def fmt_ts_by_hour(ts_s: int) -> str:
    dt = datetime.datetime.utcfromtimestamp(ts_s)
    return dt.strftime("%Y-%m-%d")


def plot_events(start_time_s: int,
                end_time_s: int,
                mongo_client: pymongo.MongoClient):
    events_coll = mongo_client.opq.events
    box_ids = [k for k in box_to_location]
    events = events_coll.find({"target_event_start_timestamp_ms": {"$gte": start_time_s * 1000.0,
                                                                   "$lte": end_time_s * 1000.0}})

    bins = set(map(fmt_ts_by_hour, list(range(start_time_s, end_time_s))))
    bins = list(bins)
    bins.sort()

    box_to_bin_to_events = {}

    for box in box_ids:
        box_to_bin_to_events[box] = {}
        for bin in bins:
            box_to_bin_to_events[box][bin] = 0

    for event in events:
        if not any_of_in(box_ids, event["boxes_triggered"]):
            continue

        dt_bin = fmt_ts_by_hour(int(event["target_event_start_timestamp_ms"] / 1000.0))
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
        labels.append("Box %s (%s)" % (box, box_to_location[box]))
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

    print(bin_to_total)

    plt.xticks(list(range(len(bins))), bins)
    plt.ylabel("# Events")
    plt.xlabel("Day")
    plt.title("Events per Day per Device (%s - %s)" % (bins[0], bins[-1]))
    plt.legend()
    plt.savefig("events-%s-%s.png" % (bins[0], bins[-1]))


def plot_incidents(start_time_s: int,
                   end_time_s: int,
                   mongo_client: pymongo.MongoClient):
    box_ids = [k for k in box_to_location]
    incidents_coll = mongo_client.opq.incidents
    incidents = incidents_coll.find({"start_timestamp_ms": {"$gte": start_time_s * 1000.0,
                                                            "$lte": end_time_s * 1000.0},
                                     "box_id": {"$in": box_ids}})

    bins = set(map(fmt_ts_by_hour, list(range(start_time_s, end_time_s))))
    bins = list(bins)
    bins.sort()

    box_to_bin_to_incidents = {}

    for box in box_ids:
        box_to_bin_to_incidents[box] = {}
        for bin in bins:
            box_to_bin_to_incidents[box][bin] = 0

    for incident in incidents:
        dt_bin = fmt_ts_by_hour(int(incident["start_timestamp_ms"] / 1000.0))
        box = incident["box_id"]
        box_to_bin_to_incidents[box][dt_bin] += 1

    def da_bottom(datasets: typing.List[np.ndarray], i: int) -> np.ndarray:
        d = np.zeros(len(datasets[i]))
        for j in range(i):
            d += datasets[j]
        return d

    plt.figure(figsize=(16, 9))
    labels = []
    datasets = []
    for box in box_to_bin_to_incidents:
        labels.append("Box %s (%s)" % (box, box_to_location[box]))
        datasets.append(np.array(list(box_to_bin_to_incidents[box].values())))

    for i in range(len(datasets)):
        if i == 0:
            plt.bar(list(range(len(bins))), datasets[i], label=labels[i])
        else:
            plt.bar(list(range(len(bins))), datasets[i], bottom=da_bottom(datasets, i), label=labels[i])

    bin_to_total = {}
    for box in box_to_bin_to_incidents:
        for bin in box_to_bin_to_incidents[box]:
            if bin not in bin_to_total:
                bin_to_total[bin] = 0
            bin_to_total[bin] += box_to_bin_to_incidents[box][bin]

    print(bin_to_total)

    plt.xticks(list(range(len(bins))), bins)
    plt.ylabel("# Incidents")
    plt.xlabel("Day")
    plt.title("Incidents per Day per Device (%s - %s)" % (bins[0], bins[-1]))
    plt.legend()
    plt.savefig("incidents-%s-%s.png" % (bins[0], bins[-1]))
    # plt.show()


def plot_trends(start_time_s: int,
                end_time_s: int,
                mongo_client: pymongo.MongoClient):
    trends_coll: pymongo.collection.Collection = mongo_client.opq.trends

    for box_id, location in box_to_location.items():
        timestamps = []
        f_min = []
        f_avg = []
        f_max = []
        v_min = []
        v_avg = []
        v_max = []
        thd_min = []
        thd_avg = []
        thd_max = []
        transient_min = []
        transient_avg = []
        transient_max = []
        trends = trends_coll.find({"timestamp_ms": {"$gte": start_time_s * 1000.0,
                                                    "$lte": end_time_s * 1000.0},
                                   "box_id": box_id}).sort("timestamp_ms")
        for trend in trends:
            timestamps.append(trend["timestamp_ms"])
            if "frequency" in trend:
                f_min.append(trend["frequency"]["min"])
                f_avg.append(trend["frequency"]["average"])
                f_max.append(trend["frequency"]["max"])
            else:
                f_min.append(0)
                f_avg.append(0)
                f_max.append(0)

            if "voltage" in trend:
                v_min.append(trend["voltage"]["min"])
                v_avg.append(trend["voltage"]["average"])
                v_max.append(trend["voltage"]["max"])
            else:
                v_min.append(0)
                v_avg.append(0)
                v_max.append(0)

            if "thd" in trend:
                thd_min.append(trend["thd"]["min"])
                thd_avg.append(trend["thd"]["average"])
                thd_max.append(trend["thd"]["max"])
            else:
                thd_min.append(0)
                thd_avg.append(0)
                thd_max.append(0)

            if "transient" in trend:
                transient_min.append(trend["transient"]["min"])
                transient_avg.append(trend["transient"]["average"])
                transient_max.append(trend["transient"]["max"])
            else:
                transient_min.append(0)
                transient_avg.append(0)
                transient_max.append(0)

        timestamps = list(map(lambda ts: datetime.datetime.utcfromtimestamp(ts / 1000.0), timestamps))
        xfmt = md.DateFormatter('%d %H:%M:%S')
        fig, (fax, vax, thdax, transientax) = plt.subplots(4, 1, sharex=True, figsize=(16, 9))

        start_dt = timestamps[0].strftime("%Y-%m-%d %H:%M")
        end_dt = timestamps[-1].strftime("%Y-%m-%d %H:%M")
        fig.suptitle("OPQ Box %s (%s): Trends %s - %s UTC" % (box_id, location, start_dt, end_dt), y=1.0, size="large",
                     weight="bold")

        fax.plot(timestamps, f_min, label="min(F)")
        fax.plot(timestamps, f_avg, label="avg(F)")
        fax.plot(timestamps, f_max, label="max(F)")
        fax.set_title("F")
        fax.set_ylabel("Hz")
        fax.legend(loc="upper right")

        vax.plot(timestamps, v_min, label="min(V)")
        vax.plot(timestamps, v_avg, label="avg(V)")
        vax.plot(timestamps, v_max, label="max(V)")
        vax.set_title("V")
        vax.set_ylabel("$V_{RMS}$")
        vax.legend(loc="upper right")

        thdax.plot(timestamps, thd_min, label="min(THD)")
        thdax.plot(timestamps, thd_avg, label="avg(THD)")
        thdax.plot(timestamps, thd_max, label="max(THD)")
        thdax.set_title("% THD")
        thdax.set_ylabel("% THD")
        thdax.legend(loc="upper right")

        transientax.plot(timestamps, transient_min, label="min(Transient)")
        transientax.plot(timestamps, transient_avg, label="avg(Transient)")
        transientax.plot(timestamps, transient_max, label="max(Transient)")
        transientax.set_title("Transient")
        transientax.set_ylabel("$P_{V}$")
        transientax.legend(loc="upper right")
        transientax.xaxis.set_major_formatter(xfmt)

        fig_title = "trends-%s-%s-%s.png" % (box_id, start_dt, end_dt)
        fig.savefig(fig_title)
        fig.show()
        print("Produced %s" % fig_title)


if __name__ == "__main__":
    mongo_client = pymongo.MongoClient()
    # plot_trends(1570798800, 1570813200, mongo_client)
    # plot_trends(1570406400, 1571054400, mongo_client)
    # report_stats(1570406400, 1571054400, mongo_client)
    # plot_events(1570406400, 1571054400, mongo_client)
    plot_incidents(1570406400, 1571054400, mongo_client)
