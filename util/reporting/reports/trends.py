import datetime
import sys
import typing

import matplotlib.ticker
import matplotlib.dates as md
import matplotlib.pyplot as plt
import pymongo

import reports


def plot_trends(start_time_s: int,
                end_time_s: int,
                report_dir: str,
                mongo_client: pymongo.MongoClient):
    trends_coll: pymongo.collection.Collection = mongo_client.opq.trends

    fig_titles: typing.List[str] = []

    box_to_trends: typing.Dict[str, typing.Dict[str, typing.List]] = {}

    min_x = 99999999999999999999999999999
    max_x = -1 * min_x
    min_v = min_x
    max_v = max_x
    min_f = min_x
    max_f = max_x
    min_thd = min_x
    max_thd = max_x
    min_transient = min_x
    max_transient = max_x

    voltage_high = 120.0 + (120.0 * .06)
    voltage_low = 120.0 - (120.0 * .06)
    frequency_high = 60.0 + (60.0 * .01)
    frequency_low = 60.0 - (60.0 * .01)
    thd_high = 5
    transient_high = 7

    for box_id, location in reports.box_to_location.items():
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
                thd_min.append(trend["thd"]["min"] * 100.0)
                thd_avg.append(trend["thd"]["average"] * 100.0)
                thd_max.append(trend["thd"]["max"] * 100.0)
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


        min_x = min(min_x, min(timestamps))
        max_x = max(max_x, max(timestamps))
        min_v = min(min_v, min(v_min))
        max_v = max(max_v, max(v_max))
        min_f = min(min_f, min(f_min))
        max_f = max(max_f, max(f_max))
        min_thd = min(min_thd, min(thd_min))
        max_thd = max(max_thd, max(thd_max))
        min_transient = min(min_transient, min(transient_min))
        max_transient = max(max_transient, max(transient_max))

        if box_id not in box_to_trends:
            box_to_trends[box_id] = {}

        box_to_trends[box_id]["timestamps"] = timestamps
        box_to_trends[box_id]["f_min"] = f_min
        box_to_trends[box_id]["f_avg"] = f_avg
        box_to_trends[box_id]["f_max"] = f_max
        box_to_trends[box_id]["v_min"] = v_min
        box_to_trends[box_id]["v_avg"] = v_avg
        box_to_trends[box_id]["v_max"] = v_max
        box_to_trends[box_id]["thd_min"] = thd_min
        box_to_trends[box_id]["thd_avg"] = thd_avg
        box_to_trends[box_id]["thd_max"] = thd_max
        box_to_trends[box_id]["transient_min"] = transient_min
        box_to_trends[box_id]["transient_avg"] = transient_avg
        box_to_trends[box_id]["transient_max"] = transient_max

    min_v = min(min_v, voltage_low)
    max_v = max(max_v, voltage_high)
    min_f = min(min_f, frequency_low)
    max_f = max(max_f, frequency_high)
    min_thd = min(min_thd, 0)
    max_thd = max(max_thd, thd_high)
    min_transient = min(min_transient, 0)
    max_transient = max(max_transient, transient_high)
    min_x = datetime.datetime.utcfromtimestamp(min_x / 1000.0)
    max_x = datetime.datetime.utcfromtimestamp(max_x / 1000.0)
    for box_id, trends in box_to_trends.items():
        timestamps = list(map(lambda ts: datetime.datetime.utcfromtimestamp(ts / 1000.0), trends["timestamps"]))
        xfmt = md.DateFormatter('%d %H:%M:%S')
        fig, (fax, vax, thdax, transientax) = plt.subplots(4, 1, sharex=True, figsize=(16, 9))

        start_dt = timestamps[0].strftime("%Y-%m-%d %H:%M")
        end_dt = timestamps[-1].strftime("%Y-%m-%d %H:%M")
        fig.suptitle("OPQ Box %s (%s): Trends %s - %s UTC" % (box_id, reports.box_to_location[box_id], start_dt, end_dt), y=1.0, size="large",
                     weight="bold")

        fax.scatter(timestamps, trends["f_min"], label="min(F)", s=1)
        fax.scatter(timestamps, trends["f_avg"], label="avg(F)", s=1)
        fax.scatter(timestamps, trends["f_max"], label="max(F)", s=1)

        fax2 = fax.twinx()
        fax2.plot(timestamps, [frequency_high for i in range(len(timestamps))], linestyle="--", color="red", linewidth=1)
        fax2.plot(timestamps, [frequency_low for i in range(len(timestamps))], linestyle="--", color="red", linewidth=1)
        fax2.get_yaxis().set_major_formatter(matplotlib.ticker.FuncFormatter(lambda x, p: "%.2f" % ((x / 60.0 * 100.0) - 100.0)))
        fax2.set_ylim(ymin=min_f-.5, ymax=max_f+.5)
        fax2.set_ylabel("% Nominal")

        fax.set_title("F")
        fax.set_ylabel("Hz")
        fax.set_xlim(xmin=min_x, xmax=max_x)
        fax.set_ylim(ymin=min_f-.5, ymax=max_f+.5)
        fax.legend(loc="upper right")

        vax.scatter(timestamps, trends["v_min"], label="min(V)", s=1)
        vax.scatter(timestamps, trends["v_avg"], label="avg(V)", s=1)
        vax.scatter(timestamps, trends["v_max"], label="max(V)", s=1)

        vax2 = vax.twinx()
        vax2.plot(timestamps, [voltage_high for i in range(len(timestamps))], linestyle="--", color="red", linewidth=1)
        vax2.plot(timestamps, [voltage_low for i in range(len(timestamps))], linestyle="--", color="red", linewidth=1)
        vax2.get_yaxis().set_major_formatter(matplotlib.ticker.FuncFormatter(lambda x, p: "%.2f" % ((x / 120.0 * 100.0) - 100.0)))
        vax2.set_ylim(ymin=min_v-5, ymax=max_v+5)
        vax2.set_ylabel("% Nominal")

        vax.set_title("V")
        vax.set_ylabel("$V_{RMS}$")
        vax.set_xlim(xmin=min_x, xmax=max_x)
        vax.set_ylim(ymin=min_v-5, ymax=max_v+5)
        vax.legend(loc="upper right")

        thdax.scatter(timestamps, trends["thd_min"], label="min(THD)", s=1)
        thdax.scatter(timestamps, trends["thd_avg"], label="avg(THD)", s=1)
        thdax.scatter(timestamps, trends["thd_max"], label="max(THD)", s=1)
        thdax.plot(timestamps, [thd_high for i in range(len(timestamps))], linestyle="--", color="red", linewidth=1)
        thdax.set_title("% THD")
        thdax.set_ylabel("% THD")
        thdax.set_xlim(xmin=min_x, xmax=max_x)
        thdax.set_ylim(ymin=min_thd, ymax=max_thd + 1)
        thdax.legend(loc="upper right")

        transientax.scatter(timestamps, trends["transient_min"], label="min(Transient)", s=1)
        transientax.scatter(timestamps, trends["transient_avg"], label="avg(Transient)", s=1)
        transientax.scatter(timestamps, trends["transient_max"], label="max(Transient)", s=1)

        transientax2 = transientax.twinx()
        transientax2.plot(timestamps, [transient_high for i in range(len(timestamps))], linestyle="--", color="red", linewidth=1)
        transientax2.get_yaxis().set_major_formatter(matplotlib.ticker.FuncFormatter(lambda x, p: "%.2f" % ((x / 7.0 * 100.0) - 100.0)))
        transientax2.set_ylim(ymin=min_transient - 5, ymax=max_transient + 5)
        transientax2.set_ylabel("% Nominal")

        transientax.set_title("Transient")
        transientax.set_ylabel("$P_{V}$")
        transientax.legend(loc="upper right")
        transientax.set_xlim(xmin=min_x, xmax=max_x)
        transientax.set_ylim(ymin=min_transient - 5, ymax=max_transient + 5)
        transientax.xaxis.set_major_formatter(xfmt)

        fig_title = "trends-%s-%d-%d.png" % (box_id, start_time_s, end_time_s)
        fig_titles.append(fig_title)
        fig.savefig("%s/%s" % (report_dir, fig_title))
        print("Produced %s" % fig_title)

    return fig_titles
