"""
This module contains the plugin definition for classifying voltage incidents by the Semi F47 standard.
"""

import typing

import shapely.geometry

import analysis
import config
from log import maybe_debug
import mongo
import plugins.base_plugin
import protobuf.mauka_pb2
import protobuf.pb_util
from plugins.routes import Routes

MAX_X_MS = 1_000_000

SEMI_F47_VIOLATION_POLYGON = [
    (1.001, 0),
    (1.001, 50),
    (analysis.ms_to_c(200), 50),
    (analysis.ms_to_c(200), 70),
    (analysis.ms_to_c(500), 70),
    (analysis.ms_to_c(500), 80),
    (analysis.ms_to_c(10_000), 80),
    (analysis.ms_to_c(10_000), 90),
    (analysis.ms_to_c(MAX_X_MS), 90),
    (analysis.ms_to_c(MAX_X_MS), 0),
    (1.001, 0),
]

POLYGON = shapely.geometry.Polygon(SEMI_F47_VIOLATION_POLYGON)


def point_in_poly(x_point: float, y_point: float) -> bool:
    """
    Checks if the given coordinates are within the SEMI F47 violation region.
    :param x_point: The x-coord.
    :param y_point: The y-coord.
    :return: True if it is, False otherwise.
    """

    # Semi-F47 extended states all devices should be able to ride out a sag of up to 1 cycle.
    if x_point <= 1:
        return False

    point = shapely.geometry.Point(x_point, y_point)
    return POLYGON.contains(point) or POLYGON.intersects(point)


def semi_violation(mongo_client: mongo.OpqMongoClient,
                   mauka_message: protobuf.mauka_pb2.MaukaMessage,
                   plugin: typing.Optional['SemiF47Plugin'] = None) -> typing.List[int]:
    """
    Calculate semi violations.
    :param mongo_client: Mongo client for DB access.
    :param mauka_message: Mauka message to calculate violations over.
    """
    incident_ids = []

    data = protobuf.pb_util.repeated_as_ndarray(mauka_message.payload.data)
    maybe_debug("Recv %d Vrms values" % len(data), plugin)
    try:
        segments = analysis.segment_array(data)
        maybe_debug("Found %d segments" % len(segments), plugin)
    except Exception as exception:
        plugin.logger.error("Error segmenting data for semi f47 plugin: %s", str(exception))
        segments = []

    for i, segment in enumerate(segments):
        try:
            segment_len_c = len(segment)
            segment_len_ms = analysis.c_to_ms(segment_len_c)
            segment_mean = segment.mean()

            maybe_debug("Segment len c=%d ms=%f mean=%f" % (segment_len_c, segment_len_ms, segment_mean), plugin)

            if point_in_poly(segment_len_c, analysis.rms_to_percent_nominal(segment_mean)):
                # New SEMI F47 violation
                start_t = analysis.c_to_ms(sum([len(segments[x]) for x in range(0, i)]))
                end_t = start_t + segment_len_ms
                incident_start_timestamp_ms = mauka_message.payload.start_timestamp_ms + start_t
                incident_end_timestamp_ms = mauka_message.payload.start_timestamp_ms + end_t
                maybe_debug("Semi F47 Violation from %f to %f" % (incident_start_timestamp_ms,
                                                                  incident_end_timestamp_ms), plugin)

                incident_id = mongo.store_incident(plugin.request_next_available_incident_id(),
                                                   mauka_message.payload.event_id,
                                                   mauka_message.payload.box_id,
                                                   incident_start_timestamp_ms,
                                                   incident_end_timestamp_ms,
                                                   mongo.IncidentMeasurementType.VOLTAGE,
                                                   segment_mean - 120.0,
                                                   [mongo.IncidentClassification.SEMI_F47_VIOLATION],
                                                   [],
                                                   {},
                                                   mongo_client)
                maybe_debug("Incident with id=%d stored" % incident_id, plugin)

                incident_ids.append(incident_id)
            else:
                maybe_debug("No Semi F47 Violation", plugin)
        except Exception as exception:
            plugin.logger.error("Error dealing with semi f47 incident: %s", str(exception))

    return incident_ids


class SemiF47Plugin(plugins.base_plugin.MaukaPlugin):
    """
    This plugin subscribes to RMS windowed voltage and classifies Semi F47 violations.
    """

    def __init__(self, conf: config.MaukaConfig, exit_event):
        super().__init__(conf, [Routes.rms_windowed_voltage], "SemiF47Plugin", exit_event)

    def on_message(self, topic: str, mauka_message: protobuf.mauka_pb2.MaukaMessage):
        if protobuf.pb_util.is_payload(mauka_message, protobuf.mauka_pb2.VOLTAGE_RMS_WINDOWED):
            self.debug("Recv windowed voltage")
            incident_ids = semi_violation(self.mongo_client, mauka_message, self)
            for incident_id in incident_ids:
                # Produce a message to the GC
                self.produce(Routes.laha_gc, protobuf.pb_util.build_gc_update(self.name,
                                                                              protobuf.mauka_pb2.INCIDENTS,
                                                                              incident_id))


def rerun(mongo_client: mongo.OpqMongoClient, mauka_message):
    """
    Rerun this plugin over the provided mauka message.
    :param mongo_client: Mongo client to perform DB queries.
    :param mauka_message: Mauka message to rerun this plugin over.
    """
    if protobuf.pb_util.is_payload(mauka_message, protobuf.mauka_pb2.VOLTAGE_RMS_WINDOWED):
        client = mongo.get_default_client(mongo_client)
        semi_violation(client, mauka_message)
