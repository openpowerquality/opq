"""
Some docs.
"""

import datetime
import typing

import matplotlib.dates as md
import matplotlib.pyplot as plt
import pymongo

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

    box_to_mauka_events: typing.Dict[str, int] = {}
    box_to_napali_events: typing.Dict[str, int] = {}
    box_to_boxes_triggered: typing.Dict[str, int] = {}
    box_to_boxes_received: typing.Dict[str, int] = {}


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
        fig.suptitle("OPQ Box %s (%s): Trends %s - %s UTC" % (box_id, location, start_dt, end_dt), y=1.0, size="large", weight="bold")

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
    plot_trends(1570565400, 1570566300, mongo_client)