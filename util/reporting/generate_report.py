import datetime
import os
import sys

import pymongo

import reports
import reports.events
import reports.incidents
import reports.tables
import reports.trends


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

    print("Generating event stats...")
    e_stats = reports.events.event_stats(start_time_s, end_time_s, mongo_client)

    print("Generating event figures...")
    e_fig = reports.events.plot_events(start_time_s, end_time_s, report_dir, mongo_client)

    print("Generating incident stats...")
    i_stats = reports.incidents.incident_stats(start_time_s, end_time_s, mongo_client)

    print("Generating incident figures...")
    i_fig = reports.incidents.plot_incidents(start_time_s, end_time_s, report_dir, mongo_client)

    print("Generating outage figures...")
    reports.incidents.plot_outages(start_time_s * 1000.0, end_time_s * 1000.0, report_dir, mongo_client)

    print("Generating Events table...")
    short_start_dt = start_dt.strftime("%Y-%m-%d")
    short_end_dt = end_dt.strftime("%Y-%m-%d")
    events_table = [["OPQ Box", "Location", "Events Generated"]]
    for box, events in e_stats["events_per_box"].items():
        events_table.append([box, reports.box_to_location[box], events])
    reports.tables.make_table(events_table, "Events %s to %s" % (short_start_dt, short_end_dt), report_dir,
                              sum_cols=[2])

    print("Generating Incidents table...")
    i_table_header = ["Box", "Cnt"]
    for incident in i_stats["incidents"]:
        i_table_header.append(reports.incident_map[incident])
    i_table = [i_table_header]
    for box, incidents in i_stats["box_to_total_incidents"].items():
        row = [box, incidents]
        for incident in i_stats["incidents"]:
            if incident in i_stats["box_to_incidents"][box]:
                row.append(i_stats["box_to_incidents"][box][incident])
            else:
                row.append(0)
        i_table.append(row)

    sum_cols = list(range(1, len(i_table_header)))
    reports.tables.make_table(i_table, "Incidents %s to %s" % (short_start_dt, short_end_dt), report_dir, sort_by_col=1,
                              sum_cols=sum_cols)

    print("Generating report...")
    with open("%s/%s.txt" % (report_dir, report_id), "w") as fout:
        # ------------------------------------- Title
        fout.write('Micro-report on the UHM micro-grid: %s to %s\n\n' % (start_dt.strftime("%m/%d"),
                                                                         end_dt.strftime("%m/%d")))

        # ------------------------------------- General Summary
        fout.write('General Summary\n\n')
        fout.write('University of Hawaii at Manoa micro-grid report on data from %s to %s UTC.\n\n' % (
            start_dt.strftime("%m-%d-%Y %H:%M"),
            end_dt.strftime("%m-%d-%Y  %H:%M")))

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
