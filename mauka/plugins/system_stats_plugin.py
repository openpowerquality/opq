"""
This plugin calculates and stores statistics about mauka and the system,
"""
import multiprocessing.queues
import numpy
import threading
import time
import typing

import config
import mongo
import plugins.base_plugin
import protobuf.mauka_pb2
import protobuf.util


def timestamp() -> int:
    return int(time.time())


class SystemStatsService:
    def __init__(self, interval_s: int):
        self.interval_s = interval_s

    def start_service(self):
        timer = threading.Timer(self.interval_s, self.collect_stats, args=[self.interval_s])
        timer.start()

    def collect_stats(self, interval_s: int):
        timer = threading.Timer(interval_s, self.collect_stats, args=[interval_s])
        timer.start()


class SystemStatsPlugin(plugins.base_plugin.MaukaPlugin):
    """
    Mauka plugin that calculates ITIC for any event that includes a raw waveform
    """
    NAME = "SystemStatsPlugin"

    def __init__(self, conf: config.MaukaConfig, exit_event: multiprocessing.Event):
        """
        Initializes this plugin
        :param conf: Configuration dictionary
        :param exit_event: Exit event
        """
        super().__init__(conf, [""], SystemStatsPlugin.NAME, exit_event)
        self.interval_s = conf.get("plugins.SystemStatsPlugin.intervalS")
        self.system_stats_service = SystemStatsService(self.interval_s)

    def handle_heartbeat(self, heartbeat):
        pass

    def on_message(self, topic, mauka_message):
        """
        Called async when a topic this plugin subscribes to produces a message
        :param topic: The topic that is producing the message
        :param mauka_message: The message that was produced
        """
        if protobuf.util.is_heartbeat_message(mauka_message):
            self.handle_heartbeat(mauka_message)
        else:
            self.logger.error("Received incorrect mauka message [%s] at %s",
                              (protobuf.util.which_message_oneof(mauka_message), SystemStatsPlugin.NAME))

