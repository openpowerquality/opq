"""
This plugin calculates and stores statistics about mauka and the system,
"""
import collections
import json
import multiprocessing.queues
import threading
import time
import typing

import numpy
import psutil

import config
import mongo
import plugins.base_plugin
import protobuf.mauka_pb2
import protobuf.pb_util

TriggeringOverrideType = typing.Dict[str, typing.Union[str, float]]
TriggeringType = typing.Dict[str, typing.Union[float, typing.List[TriggeringOverrideType]]]


def timestamp() -> int:
    """
    Returns the current timestamp in seconds since the epoch.
    :return: The current timestamp in seconds since the epoch.
    """
    return int(round(time.time()))


def box_triggering_thresholds(box_ids: typing.Set[str],
                              opq_mongo_client: typing.Optional[mongo.OpqMongoClient] = None) -> typing.List[
    typing.Dict[str, float]]:
    mongo_client = mongo.get_default_client(opq_mongo_client)
    triggering_thresholds: TriggeringType = mongo_client.makai_config_collection.find_one()["triggering"]
    triggering_overrides: typing.Dict[str, TriggeringOverrideType] = {}

    for override in triggering_thresholds["triggering_overrides"]:
        triggering_overrides[override["box_id"]] = override

    thresholds = []

    for box_id in box_ids:
        if box_id not in triggering_overrides:
            thresholds.append({
                "box_id": box_id,
                "ref_f": triggering_thresholds["default_ref_f"],
                "ref_v": triggering_thresholds["default_ref_v"],
                "threshold_percent_f_low": triggering_thresholds["default_threshold_percent_f_low"],
                "threshold_percent_f_high": triggering_thresholds["default_threshold_percent_f_high"],
                "threshold_percent_v_low": triggering_thresholds["default_threshold_percent_v_low"],
                "threshold_percent_v_high": triggering_thresholds["default_threshold_percent_v_high"],
                "threshold_percent_thd_high": triggering_thresholds["default_threshold_percent_thd_high"],
            })
        else:
            triggering_override = triggering_overrides[box_id]
            thresholds.append({
                "box_id": box_id,
                "ref_f": triggering_override["ref_f"],
                "ref_v": triggering_override["ref_v"],
                "threshold_percent_f_low": triggering_override["threshold_percent_f_low"],
                "threshold_percent_f_high": triggering_override["threshold_percent_f_high"],
                "threshold_percent_v_low": triggering_override["threshold_percent_v_low"],
                "threshold_percent_v_high": triggering_override["threshold_percent_v_high"],
                "threshold_percent_thd_high": triggering_override["threshold_percent_thd_high"],
            })
    return thresholds


class DescriptiveStatistic:
    """
    This class encapsulates a descriptive statistic which contains the min, max, mean, variance, and count of values
    """

    def __init__(self):
        self.values = []
        self.start_timestamp_s = 0
        self.end_timestamp_s = 0

    def update(self, value: typing.Union[int, float], timestamp_s: typing.Optional[int] = None):
        """
        Updates this statistic with the latest value.
        :param value: Value to update this statistic with.
        :param timestamp_s: An optional timestamp of when this value was added (will use current time if not supplied).
        """
        ts_s = timestamp_s if timestamp_s is not None else timestamp()

        if len(self.values) == 0:
            self.start_timestamp_s = ts_s

        self.values.append(value)
        self.end_timestamp_s = ts_s

    def get(self) -> typing.Dict:
        """
        Returns the contents of this class as a dictionary for easy storage in MongoDB.
        :return: The contents of this class as a dictionary for easy storage in MongoDB.
        """
        as_np = numpy.array(self.values)
        return {
            "min": float(as_np.min()),
            "max": float(as_np.max()),
            "mean": float(as_np.mean()),
            "var": float(as_np.var()),
            "cnt": len(as_np),
            "start_timestamp_s": self.start_timestamp_s,
            "end_timestamp_s": self.end_timestamp_s
        }

    def clear(self):
        """
        Clears this descriptive statistic.
        """
        self.values = []
        self.start_timestamp_s = 0
        self.end_timestamp_s = 0


class SystemStatsPlugin(plugins.base_plugin.MaukaPlugin):
    """
    Mauka plugin that retrieves and stores system and plugin stats
    """
    NAME = "SystemStatsPlugin"

    def __init__(self, conf: config.MaukaConfig, exit_event: multiprocessing.Event):
        """
        Initializes this plugin
        :param conf: Configuration dictionary
        :param exit_event: Exit event
        """
        super().__init__(conf,
                         [super().routes.heartbeat,
                          super().routes.gc_stat,
                          super().routes.box_measurement_rate_response],
                         SystemStatsPlugin.NAME, exit_event)
        self.interval_s = conf.get("plugins.SystemStatsPlugin.intervalS")
        self.system_stats_interval_s = conf.get("plugins.SystemStatsPlugin.systemStatsIntervalS")
        self.plugin_stats: typing.Dict[str, typing.Dict[str, int]] = {}
        self.gc_stats: typing.Dict[protobuf.mauka_pb2.GcDomain, int] = {
            protobuf.mauka_pb2.SAMPLES: 0,
            protobuf.mauka_pb2.MEASUREMENTS: 0,
            protobuf.mauka_pb2.TRENDS: 0,
            protobuf.mauka_pb2.EVENTS: 0,
            protobuf.mauka_pb2.INCIDENTS: 0,
            protobuf.mauka_pb2.PHENOMENA: 0
        }
        self.system_stats = collections.defaultdict(DescriptiveStatistic)
        self.system_stats["cpu_load_percent"].update(self.cpu_load_percent())
        self.system_stats["memory_use_bytes"].update(self.memory_use_bytes())
        self.system_stats["disk_use_bytes"].update(self.disk_use_bytes())

        self.box_measurement_rates: typing.Dict[str, int] = {}

        # Start stats collection
        system_stats_timer = threading.Timer(self.system_stats_interval_s, self.update_system_stats,
                                             args=[self.system_stats_interval_s])
        system_stats_timer.start()
        timer = threading.Timer(self.interval_s, self.collect_stats, args=[self.interval_s])
        timer.start()

    def events_size_bytes(self) -> int:
        """
        Returns the size of the events collection, box_events collection, associated indexes, and associated gridfs
        content.
        :return: The size of the events collection, box_events collection, associated indexes, and associated gridfs
        content.
        """
        self.debug("Collecting event stats...")
        events_collection_size_bytes = self.mongo_client.get_collection_size_bytes(mongo.Collection.EVENTS)
        # pylint: disable=C0103
        box_events_collection_size_bytes = self.mongo_client.get_collection_size_bytes(mongo.Collection.BOX_EVENTS)
        self.debug("Got collection sizes...")
        cursor = self.mongo_client.fs_files_collection.find({},
                                                            projection={
                                                                '_id': False,
                                                                'filename': True,
                                                                'length': True})
        self.debug("Got events cursor")

        only_events = filter(lambda fs_file: fs_file["filename"].startswith("event"), cursor)
        self.debug("Got only_events")
        fs_files_size_bytes = sum(map(lambda fs_file: fs_file["length"], only_events))
        self.debug("Done collecting event stats.")
        return (
                events_collection_size_bytes +
                box_events_collection_size_bytes +
                fs_files_size_bytes
        )

    def incidents_size_bytes(self) -> int:
        """
        Returns the size of the incidents collection, associated indexes, and associated gridfs
        content.
        :return: The size of the incidents collection, associated indexes, and associated gridfs
        content.
        """
        self.debug("Collecting incident stats...")
        incidents_collection_size_bytes = self.mongo_client.get_collection_size_bytes(mongo.Collection.INCIDENTS)

        cursor = self.mongo_client.fs_files_collection.find({},
                                                            projection={
                                                                '_id': False,
                                                                'filename': True,
                                                                'length': True})
        only_incidents = filter(lambda fs_file: fs_file["filename"].startswith("incident"), cursor)
        fs_files_size_bytes = sum(map(lambda fs_file: fs_file["length"], only_incidents))
        self.debug("Done collecting incident stats.")

        return (
                incidents_collection_size_bytes +
                fs_files_size_bytes
        )

    def active_devices(self) -> typing.Set[str]:
        measurements_last_minute = self.mongo_client.measurements_collection.find(
                {"timestamp_ms": {"$gt": (timestamp() - 5) * 1000}},
                projection={"_id": False,
                            "timestamp_ms": True,
                            "box_id": True})
        return set(map(lambda measurement: measurement["box_id"], measurements_last_minute))

    def num_active_devices(self) -> int:
        """
        Returns the number of active devices.

        Devices are considered active if they've send a measurement in the past 5 minutes.
        :return: The number of active OPQBoxes.
        """
        return len(self.active_devices())

    def phenomena_size_bytes(self) -> int:
        """
        Returns the size of phenomena content.
        :return: The size of phenomena content.
        """
        return 0

    def handle_gc_stat_message(self, mauka_message: protobuf.mauka_pb2.MaukaMessage):
        """
        Handles a GcStatMessage and updates the number of gc counts for the provided domain.
        :param mauka_message: A MaukaMessage contains a laha.gc_stat message.
        """
        self.debug("handle_gc_stat_message")
        gc_domain = mauka_message.laha.gc_stat.gc_domain
        gc_cnt = mauka_message.laha.gc_stat.gc_cnt
        if gc_domain == protobuf.mauka_pb2.SAMPLES:
            self.gc_stats[protobuf.mauka_pb2.SAMPLES] += gc_cnt
        elif gc_domain == protobuf.mauka_pb2.MEASUREMENTS:
            self.gc_stats[protobuf.mauka_pb2.MEASUREMENTS] += gc_cnt
        elif gc_domain == protobuf.mauka_pb2.TRENDS:
            self.gc_stats[protobuf.mauka_pb2.TRENDS] += gc_cnt
        elif gc_domain == protobuf.mauka_pb2.EVENTS:
            self.gc_stats[protobuf.mauka_pb2.EVENTS] += gc_cnt
        elif gc_domain == protobuf.mauka_pb2.INCIDENTS:
            self.gc_stats[protobuf.mauka_pb2.INCIDENTS] += gc_cnt
        elif gc_domain == protobuf.mauka_pb2.PHENOMENA:
            self.gc_stats[protobuf.mauka_pb2.PHENOMENA] += gc_cnt
        else:
            self.logger.warning("Unknown domain %s", gc_domain)

    def handle_box_measurement_rate_response(self, mauka_message: protobuf.mauka_pb2.MaukaMessage):
        box_measurement_rate_response = mauka_message.box_measurement_rate_response
        self.box_measurement_rates[box_measurement_rate_response.box_id] = box_measurement_rate_response.measurement_rate

    def update_system_stats(self, interval_s: int):
        """
        Update the system statistics.
        :param interval_s: How often the statistics should be updated.
        """
        self.debug("Updating system stats")
        self.system_stats["cpu_load_percent"].update(self.cpu_load_percent())
        self.system_stats["memory_use_bytes"].update(self.memory_use_bytes())
        self.system_stats["disk_use_bytes"].update(self.disk_use_bytes())
        timer = threading.Timer(interval_s, self.update_system_stats, args=[interval_s])
        timer.start()

    def cpu_load_percent(self) -> float:
        """
        Gets the CPU load as a percentage.
        :return: The CPU load as a percentage.
        """
        return psutil.cpu_percent()

    def memory_use_bytes(self) -> int:
        """
        Returns the memory usage in bytes.
        :return: The memory usage in bytes.
        """
        mem_stats = psutil.virtual_memory()
        return mem_stats.total - mem_stats.available

    def disk_use_bytes(self) -> int:
        """
        Return the disk usage in bytes.
        :return: The disk usage in bytes.
        """
        return psutil.disk_usage("/").used

    def reset_system_stats(self):
        """
        Resets the system statistics.
        """
        for descriptive_stat in self.system_stats.values():
            descriptive_stat.clear()

    def collect_stats(self, interval_s: int):
        """
        Collects statistics on a provided time interval.
        :param interval_s: The interval in seconds in which statistics should be collected.
        """
        self.debug("Collecting stats")
        stats = {
            "timestamp_s": timestamp(),
            "plugin_stats": self.plugin_stats,
            "system_stats": {
                "cpu_load_percent": self.system_stats["cpu_load_percent"].get(),
                "memory_use_bytes": self.system_stats["memory_use_bytes"].get(),
                "disk_use_bytes": self.system_stats["disk_use_bytes"].get()
            },
            "laha_stats": {
                "instantaneous_measurements_stats": {
                    "box_samples": {
                        "ttl": -1,
                        "count": 0,
                        "size_bytes": 0
                    }
                },
                "aggregate_measurements_stats": {
                    "measurements": {
                        "ttl": self.mongo_client.get_ttl("measurements"),
                        "count": self.mongo_client.measurements_collection.count(),
                        "size_bytes": self.mongo_client.get_collection_size_bytes(mongo.Collection.MEASUREMENTS)
                    },
                    "trends": {
                        "ttl": self.get_mongo_client().get_ttl("trends"),
                        "count": self.mongo_client.trends_collection.count(),
                        "size_bytes": self.mongo_client.get_collection_size_bytes(mongo.Collection.TRENDS)
                    }
                },
                "detections_stats": {
                    "events": {
                        "ttl": self.mongo_client.get_ttl("events"),
                        "count": self.mongo_client.events_collection.count(),
                        "size_bytes": self.events_size_bytes()
                    }
                },
                "incidents_stats": {
                    "incidents": {
                        "ttl": self.mongo_client.get_ttl("incidents"),
                        "count": self.mongo_client.incidents_collection.count(),
                        "size_bytes": self.incidents_size_bytes()
                    }
                },
                "phenomena_stats": {
                    "phenomena": {
                        "ttl": -1,
                        "count": self.mongo_client.phenomena_collection.count(),
                        "size_bytes": self.phenomena_size_bytes()
                    }
                },
                "gc_stats": {
                    "samples": self.gc_stats[protobuf.mauka_pb2.SAMPLES],
                    "measurements": self.gc_stats[protobuf.mauka_pb2.MEASUREMENTS],
                    "trends": self.gc_stats[protobuf.mauka_pb2.TRENDS],
                    "events": self.gc_stats[protobuf.mauka_pb2.EVENTS],
                    "incidents": self.gc_stats[protobuf.mauka_pb2.INCIDENTS],
                    "phenomena:": self.gc_stats[protobuf.mauka_pb2.PHENOMENA]
                },
                "active_devices": len(self.mongo_client.get_active_box_ids()),
                "box_triggering_thresholds": box_triggering_thresholds(self.active_devices(), self.mongo_client),
                "box_measurement_rates": [{box_id: measurement_rate} for box_id, measurement_rate in
                                          self.box_measurement_rates.items()]
            },
            "other_stats": {
                "ground_truth": {
                    "count": self.mongo_client.ground_truth_collection.count(),
                    "size_bytes": self.mongo_client.get_collection_size_bytes(mongo.Collection.GROUND_TRUTH)
                }
            }
        }
        self.mongo_client.laha_stats_collection.insert_one(stats)
        self.reset_system_stats()
        self.debug("Stats stored")
        timer = threading.Timer(interval_s, self.collect_stats, args=[interval_s])
        timer.start()

    def on_message(self, topic: str, mauka_message: protobuf.mauka_pb2.MaukaMessage):
        """
        Called async when a topic this plugin subscribes to produces a message
        :param topic: The topic that is producing the message
        :param mauka_message: The message that was produced
        """
        self.debug("Received message %s" % str(mauka_message))
        if protobuf.pb_util.is_heartbeat_message(mauka_message):
            self.debug("Received heartbeat message, updating plugin stats.")
            self.plugin_stats[mauka_message.source] = json.loads(mauka_message.heartbeat.status)
            box_measurement_rate_request = protobuf.pb_util.build_box_measurement_rate_request("system_stats_plugin",
                                                                                               list(self.active_devices()))
            self.produce(self.routes.box_measurement_rate_request, box_measurement_rate_request)
        elif protobuf.pb_util.is_gc_stat(mauka_message):
            self.debug("Received gc_stat message")
            self.handle_gc_stat_message(mauka_message)
        elif protobuf.pb_util.is_box_measurement_rate_response(mauka_message):
            self.debug("Received box_measurement_rates message")
            self.handle_box_measurement_rate_response(mauka_message)
        else:
            self.logger.error("Received incorrect mauka message [%s] at %s",
                              protobuf.pb_util.which_message_oneof(mauka_message), SystemStatsPlugin.NAME)

# if __name__ == "__main__":
#     print(box_triggering_thresholds({"1003", "1004", "1005"}))
