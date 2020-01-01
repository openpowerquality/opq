"""
This module contains the plugin for Periodic Phenomena.
"""
import collections
import functools
from typing import DefaultDict, Dict, List, Optional, Set, TypeVar
import threading

import config
import numpy as np
import scipy.signal
from log import maybe_debug
import mongo
import plugins.base_plugin
import protobuf.mauka_pb2
import protobuf.pb_util
import pymongo
import pymongo.database

from plugins.routes import Routes

THD: str = "thd"
VOLTAGE: str = "voltage"
FREQUENCY: str = "frequency"
MINV: str = "min"
MEANV: str = "average"
MAXV: str = "max"


class Measurement:
    """
    Measurement
    """

    def __init__(self,
                 box_id: str,
                 timestamp_ms: int,
                 voltage: float,
                 thd: float,
                 frequency: float):
        self.box_id = box_id
        self.timestamp_ms = timestamp_ms
        self.voltage = voltage
        self.thd = thd
        self.frequency = frequency

    def __str__(self):
        return f"{self.box_id} {self.timestamp_ms} {self.voltage} {self.frequency} {self.thd}"


class TrendValue:
    """
    TrendValue
    """

    def __init__(self,
                 name: str,
                 minv: float,
                 meanv: float,
                 maxv: float):
        self.name = name
        self.minv = minv
        self.meanv = meanv
        self.maxv = maxv

    def __str__(self):
        return f"{self.name} {self.minv} {self.meanv} {self.maxv}"


class Trend:
    """
    Trend
    """

    def __init__(self,
                 box_id: str,
                 timestamp_ms: int,
                 trend_values: Dict[str, TrendValue]):
        self.box_id = box_id
        self.timestamp_ms = timestamp_ms
        self.trend_values = trend_values

    def __str__(self):
        return f"{self.box_id} {self.timestamp_ms} {list(map(str, self.trend_values.values()))}"


T = TypeVar("T")
S = TypeVar("S")


class CycleResult:
    """
    CycleResult
    """

    def __init__(self,
                 peaks: int,
                 mean_diff: float,
                 std_diff: float):
        self.peaks = peaks
        self.mean_diff = mean_diff
        self.std_diff = std_diff

    def __str__(self):
        return f"{self.peaks} {self.mean_diff} {self.std_diff}"


def search_for_sub_daily_voltage_cycles(measurements: List[Measurement]) -> Optional[CycleResult]:
    """

    :param measurements:
    :return:
    """
    vs_raw = np.array(list(map(lambda measurement: measurement.voltage, measurements)))
    (b, a) = scipy.signal.butter(4, 1 / 3600, btype="highpass", fs=1.0)
    values = scipy.signal.filtfilt(b, a, vs_raw)
    values_minus_dc = values - values.mean()
    corr = np.correlate(values_minus_dc, values_minus_dc, mode="same")
    peaks = scipy.signal.find_peaks(corr, prominence=1000)[0]

    if peaks.size >= 3:
        peak_diffs = np.diff(peaks)
        diff_mean = peak_diffs.mean()
        diff_std = peak_diffs.std()
        return CycleResult(peaks.size, diff_mean, diff_std)
    else:
        return None


def append_dict(other_dict: DefaultDict[S, List[T]],
                key: S,
                value: T) -> DefaultDict[S, List[T]]:
    """

    :param other_dict:
    :param key:
    :param value:
    :return:
    """
    other_dict[key].append(value)
    return other_dict


def get_measurements_map(start_time_s: int,
                         end_time_s: int,
                         mongo_client: pymongo.MongoClient) -> DefaultDict[str, List[Measurement]]:
    """

    :param start_time_s:
    :param end_time_s:
    :param mongo_client:
    :return:
    """
    database: pymongo.database.Database = mongo_client["opq"]
    coll: pymongo.collection.Collection = database["measurements"]

    query = {"timestamp_ms": {"$gte": start_time_s * 1_000.0,
                              "$lte": end_time_s * 1_000.0},
             "box_id": {"$in": ["1021", "1023"]}}

    projection = {"_id": False,
                  "thd": True,
                  "voltage": True,
                  "frequency": True,
                  "timestamp_ms": True,
                  "box_id": True}

    cursor: pymongo.cursor.Cursor = coll.find(query, projection=projection).sort("timestamp_ms")
    measurements = list(
            map(lambda doc: Measurement(doc["box_id"], doc["timestamp_ms"], doc["voltage"], doc["thd"],
                                        doc["frequency"]),
                list(cursor)))

    return functools.reduce(
            lambda measurement_dict, measurement: append_dict(measurement_dict, measurement.box_id, measurement),
            measurements,
            collections.defaultdict(list))


def handle_cycle_result(cycle_result: CycleResult,
                        opq_mongo_client: mongo.OpqMongoClient) -> None:
    """

    :param cycle_result:
    :return:
    """
    if cycle_result.peaks > 3 and cycle_result.std_diff < 600:
        # Check to see if a periodic incident already exists

        # If it does, update it if this one has better metrics

        # If it doesn't create a new periodic phenomena
        mongo.store_periodic_phenomena(opq_mongo_client, -1, -1, [], [], [], cycle_result.mean_diff, cycle_result.std_diff)

        # Find Events and Incidents for this box that match this period
        pass


def check_for_periodic_phenomena(interval_s: float,
                                 mongo_client: pymongo.MongoClient):
    """

    :param interval_s:
    :param mongo_client:
    :return:
    """
    now = int(round(time.time()))
    all_measurements = get_measurements_map(now - 86400, now, mongo_client)
    for box_id, measurements in all_measurements.items():
        cycle_result: CycleResult = search_for_sub_daily_voltage_cycles(measurements)
        if cycle_result is not None:
            handle_cycle_result(cycle_result)

    timer: threading.Timer = threading.Timer(interval_s, check_for_periodic_phenomena, (interval_s,))
    timer.start()


class PeriodicityPlugin(plugins.base_plugin.MaukaPlugin):
    """
    This plugin subscribes to annotation request messages.
    """
    NAME: str = "PeriodicityPlugin"

    def __init__(self, conf: config.MaukaConfig, exit_event):
        super().__init__(conf, [Routes.makai_event], PeriodicityPlugin.NAME, exit_event)
        check_for_periodic_phenomena(3600,
                                     self.mongo_client.client)

    def on_message(self, topic: str, mauka_message: protobuf.mauka_pb2.MaukaMessage):
        """

        :param topic:
        :param mauka_message:
        :return:
        """

        if protobuf.pb_util.is_makai_event_message(mauka_message):
            pass
        else:
            pass

        # if protobuf.pb_util.is_annotation_request(mauka_message):
        #     self.debug("Recv annotation request")
        # phenomena_id: int = perform_annotation(self.mongo_client,
        #                                        mauka_message.annotation_request.incidents_ids[:],
        #                                        mauka_message.annotation_request.event_ids[:],
        #                                        mauka_message.annotation_request.annotation,
        #                                        mauka_message.annotation_request.start_timestamp_ms,
        #                                        mauka_message.annotation_request.end_timestamp_ms)
        #
        # self.debug(f"Made phenomena with id={phenomena_id}")
        #
        # gc_update = protobuf.pb_util.build_gc_update(self.name,
        #                                              protobuf.mauka_pb2.PHENOMENA,
        #                                              phenomena_id)
        # self.debug(f"Preparing to send gc_update={str(gc_update)}")
        #
        # self.produce(Routes.laha_gc, gc_update)
        # else:
        #     self.logger.error("Received incorrect message type for AnnotationPlugin: %s", str(mauka_message))
