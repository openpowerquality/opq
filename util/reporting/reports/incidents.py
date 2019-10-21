import typing

import matplotlib.pyplot as plt
import numpy as np
import pymongo

import reports


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

    for incident in incidents:
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
