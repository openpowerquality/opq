import datetime
import glob
import os
import subprocess
import sys
import typing

import pymongo
import matplotlib.pyplot as plt
import numpy as np

import reports
import reports.tables
import reports.trends


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


def fmt_ts_by_hour(ts_s: int) -> str:
    dt = datetime.datetime.utcfromtimestamp(ts_s)
    return dt.strftime("%Y-%m-%d")


def plot_events(start_time_s: int,
                end_time_s: int,
                report_dir: str,
                mongo_client: pymongo.MongoClient):
    events_coll = mongo_client.opq.events
    box_ids = [k for k in reports.box_to_location]
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
        if not reports.any_of_in(box_ids, event["boxes_triggered"]):
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


def plot_incidents(start_time_s: int,
                   end_time_s: int,
                   report_dir: str,
                   mongo_client: pymongo.MongoClient):
    box_ids = [k for k in reports.box_to_location]
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


def create_report(start_time_s: int,
                  end_time_s: int):
    mongo_client = pymongo.MongoClient()

    report_id = "report_%d_%d" % (start_time_s, end_time_s)
    report_dir = "./%s" % report_id
    try:
        os.mkdir(report_dir)
    except:
        pass

    start_dt = datetime.datetime.utcfromtimestamp(start_time_s)
    end_dt = datetime.datetime.utcfromtimestamp(end_time_s)
    now_dt = datetime.datetime.now()

    print("Generating trend figures...")
    trend_figures = reports.trends.plot_trends(start_time_s, end_time_s, report_dir, mongo_client)
    # trend_figures = plot_trends(start_time_s, end_time_s, report_dir, mongo_client)

    print("Generating event stats...")
    e_stats = event_stats(start_time_s, end_time_s, mongo_client)

    print("Generating event figures...")
    e_fig = plot_events(start_time_s, end_time_s, report_dir, mongo_client)

    print("Generating incident stats...")
    i_stats = incident_stats(start_time_s, end_time_s, mongo_client)

    print("Generating incident figures...")
    i_fig = plot_incidents(start_time_s, end_time_s, report_dir, mongo_client)

    print("Generating Events table...")
    short_start_dt = start_dt.strftime("%Y-%m-%d")
    short_end_dt = end_dt.strftime("%Y-%m-%d")
    events_table = [["OPQ Box", "Location", "Events Generated"]]
    for box, events in e_stats["events_per_box"].items():
        events_table.append([box, reports.box_to_location[box], events])
    reports.tables.make_table(events_table, "Events %s to %s" % (short_start_dt, short_end_dt), report_dir, sum_cols=[2])

    print("Generating Incidents table...")
    i_table_header = ["OPQ Box", "Location", "Incidents"]
    for incident in i_stats["incidents"]:
        i_table_header.append(reports.incident_map[incident])
    i_table = [i_table_header]
    for box, incidents in i_stats["box_to_total_incidents"].items():
        row = [box, reports.box_to_location[box], incidents]
        for incident in i_stats["incidents"]:
            if incident in i_stats["box_to_incidents"][box]:
                row.append(i_stats["box_to_incidents"][box][incident])
            else:
                row.append(0)
        i_table.append(row)

    sum_cols = list(range(2, len(i_table_header)))
    reports.tables.make_table(i_table, "Incidents %s to %s" % (short_start_dt, short_end_dt), report_dir, sort_by_col=2, sum_cols=sum_cols)

    print("Generating report...")
    with open("%s/%s.txt" % (report_dir, report_id), "w") as fout:
        # ------------------------------------- Title
        fout.write('Micro-report on the UHM micro-grid: %s to %s\n\n' % (start_dt.strftime("%Y-%m-%d %H:%M"),end_dt.strftime("%Y-%m-%d %H:%M")))

        # ------------------------------------- Synopsis
        fout.write('Synopsis\n\n')

        # ------------------------------------- General Summary
        fout.write('General Summary\n\n')

        # ------------------------------------- Trends Summary
        fout.write('Trends Summary\n\n')

        fout.write('Weekly trends measure the minimum, average, and maximum values for Voltage, Frequency, THD, '
                   'and transients for each OPQ Box at a rate of 1 Hz.\n\n')

        fout.write('The following figures show Trends for each Box between %s and %s.\n\n' % (start_dt, end_dt))

        # ------------------------------------- Events Summary
        fout.write('Events Summary\n\n')

        fout.write('Events are ranges of PQ data that may (or may not) have PQ issues within them. Events are generated'
                   ' by two methods. The first method uses Voltage, Frequency, and THD thresholds as defined by IEEE. '
                   'The second method uses the Napali Trigger which was developed by Sergey as part of his dissertation'
                   ' research. The Napali trigger uses statistical methods to determine when Boxes may contain PQ '
                   'issues. This summary of Events examines the number of times that Boxes were triggered due to '
                   'possible PQ issues.\n\n')

        fout.write('There were a total of %d Events processed.\n\n' % e_stats["total_events"])

        fout.write('The following table shows Events generated per Box.\n\n')

        fout.write('The following figure shows Events per Box per day.\n\n')

        # ------------------------------------- Incidents Summary
        fout.write('Incidents Summary\n\n')

        fout.write('Incidents are classified PQ issues that were found in the previously provided Events. Incidents are'
                   ' classified by OPQ Mauka according to various PQ standards. OPQ Mauka provides classifications for'
                   ' Outages, Voltage, Frequency, and THD related issues.\n\n')

        fout.write("A total of %d Incidents were processed.\n\n" % i_stats["total_incidents"])

        fout.write('A breakdown of Incidents by their type is provided in the following table.\n\n')

        fout.write('A breakdown of Incidents per Box is provided in the following table.\n\n')

        fout.write('The following figure shows Incidents per Box per day.\n\n')

        # ------------------------------------- Conclusion
        fout.write('Conclusion\n\n')

        print("Report generated.")


if __name__ == "__main__":
    try:
        start_time_s = int(sys.argv[1])
        end_time_s = int(sys.argv[2])
        create_report(start_time_s, end_time_s)
    except IndexError:
        print("usage: python3 generate_report.py [start time s utc] [end time s utc]")
        sys.exit(1)
    except ValueError:
        print("Error parsing time range.")
        print("usage: python3 generate_report.py [start time s utc] [end time s utc]")
        sys.exit(2)

