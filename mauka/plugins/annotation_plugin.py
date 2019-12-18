"""
This module contains the plugin for producting Annotation Phenomena.
"""

import typing

import config
from log import maybe_debug
import mongo
import plugins.base_plugin
import protobuf.mauka_pb2
import protobuf.pb_util
from plugins.routes import Routes


def perform_annotation() -> None:
    pass


class AnnotationPlugin(plugins.base_plugin.MaukaPlugin):
    """
    This plugin subscribes to annotation request messages.
    """
    NAME: str = "AnnotationPlugin"

    def __init__(self, conf: config.MaukaConfig, exit_event):
        super().__init__(conf, [Routes.annotation_request], AnnotationPlugin.NAME, exit_event)

    def on_message(self, topic: str, mauka_message: protobuf.mauka_pb2.MaukaMessage):
        if protobuf.pb_util.is_payload(mauka_message, protobuf.mauka_pb2.VOLTAGE_RMS_WINDOWED):
            self.debug("Recv windowed voltage")
            incident_ids = semi_violation(self.mongo_client, mauka_message, self)
            for incident_id in incident_ids:
                # Produce a message to the GC
                self.produce(Routes.laha_gc, protobuf.pb_util.build_gc_update(self.name,
                                                                              protobuf.mauka_pb2.INCIDENTS,
                                                                              incident_id))
