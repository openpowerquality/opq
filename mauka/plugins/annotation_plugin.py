"""
This module contains the plugin for producing Annotation Phenomena.
"""

from typing import Dict, List, Set

import config
from log import maybe_debug
import mongo
import plugins.base_plugin
import protobuf.mauka_pb2
import protobuf.pb_util
from plugins.routes import Routes


def perform_annotation(opq_mongo_client: mongo.OpqMongoClient,
                       incident_ids: List[int],
                       event_ids: List[int],
                       annotation: str,
                       start_timestamp_ms: int,
                       end_timestamp_ms: int) -> int:
    incidents_query: Dict = {
        "incident_id": {"$in": incident_ids}
    }

    incidents_projection: Dict[str, bool] = {
        "_id": False,
        "box_id": True,
        "event_id": True
    }

    box_events_query: Dict = {
        "event_id": {"$in": event_ids}
    }

    box_events_projection: Dict[str, bool] = {
        "_id": False,
        "event_id": True,
        "box_id": True
    }

    incident_docs: List[Dict] = list(opq_mongo_client.incidents_collection.find(incidents_query,
                                                                                projection=incidents_projection))
    box_event_docs: List[Dict] = list(opq_mongo_client.box_events_collection.find(box_events_query,
                                                                                  projection=box_events_projection))

    incident_box_ids: Set[str] = set(map(lambda doc: doc["box_id"], incident_docs))
    box_event_box_ids: Set[str] = set(map(lambda doc: doc["box_id"], box_event_docs))
    box_event_ids_from_incidents: Set[int] = set(map(lambda doc: doc["event_id"], box_event_docs))
    all_event_ids: List[int] = list(box_event_ids_from_incidents.union(set(event_ids)))
    affected_box_ids: List[str] = list(incident_box_ids.union(box_event_box_ids))

    return mongo.store_annotation_phenomena(opq_mongo_client,
                                            start_timestamp_ms,
                                            end_timestamp_ms,
                                            affected_box_ids,
                                            incident_ids,
                                            all_event_ids,
                                            annotation)


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
            phenomena_id: int = perform_annotation(self.mongo_client,
                                                   mauka_message.annotation_request.incidents_ids[:],
                                                   mauka_message.annotation_request.event_ids[:],
                                                   mauka_message.annotation_request.annotation,
                                                   mauka_message.annotation_request.start_timestamp_ms,
                                                   mauka_message.annotation_request.end_timestamp_ms)

            self.produce(Routes.laha_gc, protobuf.pb_util.build_gc_update(self.name,
                                                                          protobuf.mauka_pb2.PHENOMENA,
                                                                          phenomena_id))
        else:
            self.logger.error("Received incorrect message type for AnnotationPlugin: %s", str(mauka_message))
