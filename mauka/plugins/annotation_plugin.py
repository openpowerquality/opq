"""
This module contains the plugin for producting Annotation Phenomena.
"""

from typing import List

import config
from log import maybe_debug
import mongo
import plugins.base_plugin
import protobuf.mauka_pb2
import protobuf.pb_util
from plugins.routes import Routes


def perform_annotation(incident_ids: List[int],
                       event_ids: List[int],
                       annotation: str) -> int:
    return 0


class AnnotationPlugin(plugins.base_plugin.MaukaPlugin):
    """
    This plugin subscribes to annotation request messages.
    """
    NAME: str = "AnnotationPlugin"

    def __init__(self, conf: config.MaukaConfig, exit_event):
        super().__init__(conf, [Routes.annotation_request], AnnotationPlugin.NAME, exit_event)

    def on_message(self, topic: str, mauka_message: protobuf.mauka_pb2.MaukaMessage):
        if protobuf.pb_util.is_annotation_request(mauka_message):
            self.debug("Recv annotation request")
            phenomena_id: int = perform_annotation(mauka_message.annotation_request.incidents_ids[:],
                                                   mauka_message.annotation_request.event_ids[:],
                                                   mauka_message.annotation_request.annotation)

            self.produce(Routes.laha_gc, protobuf.pb_util.build_gc_update(self.name,
                                                                          protobuf.mauka_pb2.PHENOMENA,
                                                                          phenomena_id))
            # for incident_id in incident_ids:
            #     # Produce a message to the GC
            #     self.produce(Routes.laha_gc, protobuf.pb_util.build_gc_update(self.name,
            #                                                                   protobuf.mauka_pb2.INCIDENTS,
            #                                                                   incident_id))
        else:
            self.logger.error("Received incorrect message type for AnnotationPlugin: %s", str(mauka_message))
