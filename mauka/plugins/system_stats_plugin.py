"""
This plugin calculates and stores statistics about mauka and the system,
"""
import json
import multiprocessing.queues
import threading
import time
import typing

import config
import plugins.base_plugin
import protobuf.mauka_pb2
import protobuf.util


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

    def collect_stats(self, interval_s: int):
        """
        Collects statistics on a provided time interval.
        :param interval_s: The interval in seconds in which statistics should be collected.
        """
        stats = {
            "timestamp_s": timestamp(),
            "plugin_stats": self.plugin_stats
        }
        self.mongo_client.laha_stats_collection.insert_one(stats)
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