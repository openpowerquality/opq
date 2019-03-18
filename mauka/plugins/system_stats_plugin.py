"""
This plugin calculates and stores statistics about mauka and the system,
"""
import functools
import json
import multiprocessing.queues
import threading
import time
import typing

import config
import mongo
import plugins.base_plugin
import protobuf.mauka_pb2
import protobuf.util

import psutil


def timestamp() -> int:
    """
    Returns the current timestamp in seconds since the epoch.
    :return: The current timestamp in seconds since the epoch.
    """
    return int(time.time())


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
        super().__init__(conf, ["heartbeat"], SystemStatsPlugin.NAME, exit_event)
        self.interval_s = conf.get("plugins.SystemStatsPlugin.intervalS")
        self.plugin_stats: typing.Dict[str, typing.Dict[str, int]] = {}

        # Start stats collection
        timer = threading.Timer(self.interval_s, self.collect_stats, args=[self.interval_s])
        timer.start()

    def events_size_bytes(self) -> int:
        self.debug("Collecting event stats...")
        events_collection_size_bytes = self.mongo_client.get_collection_size_bytes(mongo.Collection.EVENTS)
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

    def num_active_devices(self) -> int:
        measurements_last_minute = self.mongo_client.measurements_collection.find({"timestamp_ms": {"$gt": (timestamp() - 5) * 1000}},
                                                                                  projection={"_id": False,
                                                                                              "timestamp_ms": True,
                                                                                              "box_id": True})
        box_ids = set(map(lambda measurement: measurement["box_id"], measurements_last_minute))
        return len(box_ids)



    def phenomena_size_bytes(self) -> int:
        return 0

    def collect_stats(self, interval_s: int):
        """
        Collects statistics on a provided time interval.
        :param interval_s: The interval in seconds in which statistics should be collected.
        """
        self.debug("Collecting stats...")
        mem_stats = psutil.virtual_memory()
        # active_devices = self.num_active_devices()
        # box_samples_ttl = self.mongo_client.get_ttl("box_samples")



        stats = {
            "timestamp_s": timestamp(),
            "plugin_stats": self.plugin_stats,
            "system_stats": {
                "cpu_load_percent": psutil.cpu_percent(),
                "memory_use_bytes": mem_stats.total - mem_stats.available,
                "disk_use_bytes": psutil.disk_usage("/").used
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
                }
            },
            "other_stats": {
                "ground_truth": {
                    "count": self.mongo_client.ground_truth_collection.count(),
                    "size_bytes": self.mongo_client.get_collection_size_bytes(mongo.Collection.GROUND_TRUTH)
                }
            }
        }
        self.mongo_client.laha_stats_collection.insert_one(stats)
        self.debug("Stats stored.")
        timer = threading.Timer(interval_s, self.collect_stats, args=[interval_s])
        timer.start()

    def on_message(self, topic: str, mauka_message: protobuf.mauka_pb2.MaukaMessage):
        """
        Called async when a topic this plugin subscribes to produces a message
        :param topic: The topic that is producing the message
        :param mauka_message: The message that was produced
        """
        if protobuf.util.is_heartbeat_message(mauka_message):
            self.plugin_stats[mauka_message.source] = json.loads(mauka_message.heartbeat.status)
        else:
            self.logger.error("Received incorrect mauka message [%s] at %s",
                              protobuf.util.which_message_oneof(mauka_message), SystemStatsPlugin.NAME)
