import datetime
import typing

import gridfs
import matplotlib.pyplot as plt
import numpy as np
import pymongo

import reports



def plot_incident(incident_id: int,
                  report_dir: str,
                  mongo_client: pymongo.MongoClient):
    grid_fs = gridfs.GridFS(mongo_client.opq)
    incidents_coll = mongo_client.opq.incidents

    incident = incidents_coll.find_one({"incident_id": incident_id})
    print(incident)
    start_ms = incident["start_timestamp_ms"]
    start_dt = datetime.datetime.utcfromtimestamp(start_ms / 1000.0)
    wf_y_values = reports.calib_waveform(incident["gridfs_filename"], incident["box_id"], mongo_client)
    wf_x_values = [datetime.datetime.utcfromtimestamp((start_ms + reports.sample_to_ms(t)) / 1000.0) for t in
                range(len(wf_y_values))]

    fig, ax = plt.subplots(4, 1, figsize=(16, 9), sharex="all")
    fig.suptitle("Incident: %d (%s) OPQ Box: %s @ %s UTC" % (
        incident["incident_id"],
        incident["classifications"][0],
        incident["box_id"],
        start_dt.strftime("%Y-%m-%d %H:%M:%S")
    ))
    ax[0].plot(wf_x_values, wf_y_values)
    ax[0].set_title("Waveform")
    ax[0].set_ylabel("Voltage")

    vrms_y_values = reports.vrms_waveform(wf_y_values)
    vrms_x_values = wf_x_values[0::12000]
    print(vrms_y_values)
    ax[1].plot(vrms_x_values, vrms_y_values)

    plt.show()


def plot_incidents(start_time_s: int,
                   end_time_s: int,
                   report_dir: str,
                   mongo_client: pymongo.MongoClient):
    box_ids = [k for k in reports.box_to_location]
    incidents_coll = mongo_client.opq.incidents
    incidents = incidents_coll.find({"start_timestamp_ms": {"$gte": start_time_s * 1000.0,
                                                            "$lte": end_time_s * 1000.0},
                                     "box_id": {"$in": box_ids}})

    bins = set(map(reports.fmt_ts_by_hour, list(range(start_time_s, end_time_s))))
    bins = list(bins)
    bins.sort()

    box_to_bin_to_incidents = {}

    for box in box_ids:
        box_to_bin_to_incidents[box] = {}
        for bin in bins:
            box_to_bin_to_incidents[box][bin] = 0

    with open("%s/incidents.txt" % report_dir, "a") as fout:
        for incident in incidents:
            fout.write("%d %s\n" % (incident["incident_id"], incident["classifications"][0]))
            dt_bin = reports.fmt_ts_by_hour(int(incident["start_timestamp_ms"] / 1000.0))
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
        labels.append("Box %s (%s)" % (box, reports.box_to_location[box]))
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

    plt.xticks(list(range(len(bins))), bins)
    plt.ylabel("# Incidents")
    plt.xlabel("Day")
    plt.title("Incidents per Day per Device (%s - %s)" % (bins[0], bins[-1]))
    plt.legend()
    fig_name = "incidents-%s-%s.png" % (bins[0], bins[-1])
    print("Produced %s" % fig_name)
    plt.savefig("%s/%s" % (report_dir, fig_name))
    return fig_name


def incident_stats(start_time_s: int,
                   end_time_s: int,
                   mongo_client: pymongo.MongoClient):
    box_to_total_incidents: typing.Dict[str, int] = {}
    incident_types: typing.Dict[str, int] = {}
    box_to_incidents: typing.Dict[str, typing.Dict[str, int]] = {}

    box_ids = [k for k in reports.box_to_location]

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

    return {"total_incidents": sum(box_to_total_incidents.values()),
            "box_to_total_incidents": box_to_total_incidents,
            "incident_types": incident_types,
            "incidents": [k for k in incident_types],
            "box_to_incidents": box_to_incidents}

def plot_outage(incident_id: int,
                report_dir: str,
                mongo_client: pymongo.MongoClient):
    measurements_coll = mongo_client.opq.measurements
    trends_coll = mongo_client.opq.trends
    incidents_coll = mongo_client.opq.incidents

    incident = incidents_coll.find_one({"incident_id": incident_id})
    i_start = incident["start_timestamp_ms"]
    i_end = incident["end_timestamp_ms"]
    box_id = incident["box_id"]
    print(datetime.datetime.utcfromtimestamp(i_start / 1000.0))
    print("outage %d OPQ Box %s (%s) range=%f (%d - %d)" % (
        incident_id,
        box_id,
        reports.box_to_location[box_id],
        (i_end - i_start),
        i_start,
        i_end
    ))

    h_start = datetime.datetime.utcfromtimestamp(i_start / 1000.0)
    h_end = datetime.datetime.utcfromtimestamp(i_end / 1000.0)


    measurements = list(measurements_coll.find({"box_id": box_id,
                                           "timestamp_ms": {"$gte": i_start,
                                                            "$lte": i_end}}))
    print("%d measurements" % len(list(measurements)))

    trends = trends_coll.find({"box_id": box_id,
                               "timestamp_ms": {"$gte": i_start,
                                                "$lte": i_end}})

    print("%d trends" % len(list(trends)))

    fig, ax = plt.subplots(1, 1, figsize=(16, 9))
    m_x = list(map(lambda m: datetime.datetime.utcfromtimestamp(m["timestamp_ms"] / 1000.0), measurements))
    m_y = list(map(lambda m: m["voltage"], measurements))
    print(m_x)
    print(m_y)
    ax.plot(m_x, m_y)

    plt.show()

def plot_outages(start_ms: int,
                 end_ms: int,
                 report_dir: str,
                 mongo_client: pymongo.MongoClient):
    incidents_coll = mongo_client.opq.incidents
    outages = incidents_coll.find({"box_id": {"$in": reports.boxes},
                                   "start_timestamp_ms": {"$gte": start_ms,
                                                          "$lte": end_ms},
                                   "classifications": "OUTAGE"})
    outages = list(outages)
    print(outages)

    fig, ax = plt.subplots(1, 1, figsize=(16, 9))
    fig.suptitle("Outages")
    for outage in outages:
        o_start = datetime.datetime.utcfromtimestamp(outage["start_timestamp_ms"] / 1000.0)
        o_end = datetime.datetime.utcfromtimestamp(outage["end_timestamp_ms"] / 1000.0)
        box_id = outage["box_id"]
        ax.plot([o_start, o_end], [int(box_id), int(box_id)],
                linewidth=15)
        ax.set_ylabel("OPQ Box")
        ax.set_xlabel("Time (UTC)")

    plt.savefig("%s/outages-%d-%d.png" % (report_dir, start_ms, end_ms))
    plt.show()


if __name__ == "__main__":
    # plot_incident(56040, ".", pymongo.MongoClient())
    # plot_outage(62868, ".", pymongo.MongoClient())
    plot_outage(73319, ".", pymongo.MongoClient())
    # with open("/Users/anthony/Development/opq/util/reporting/report_1571133600_1571738400/incidents.txt", "r") as fin:
    #     for line in fin.readlines():
    #         s = line.strip().split(" ")
    #         # print(s)
    #         if s[1] == "OUTAGE":
    #             plot_outage(int(s[0]), ".", pymongo.MongoClient())
    # plot_outages(1571133600000, 1571738400000, ".", pymongo.MongoClient())
