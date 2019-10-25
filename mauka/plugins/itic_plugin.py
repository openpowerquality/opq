"""
This plugin calculates the ITIC region of a voltage, duration pair.
"""
import enum
import multiprocessing.queues
import typing

import shapely
import shapely.geometry

import analysis
import config
import mongo
import plugins.base_plugin
from plugins.routes import Routes
import protobuf.mauka_pb2
import protobuf.pb_util



class IticRegion(enum.Enum):
    """
    Enumerations of ITIC regions.
    """
    NO_INTERRUPTION = "NO_INTERRUPTION"
    PROHIBITED = "PROHIBITED"
    NO_DAMAGE = "NO_DAMAGE"
    OTHER = "OTHER"


HUNDREDTH_OF_A_CYCLE = analysis.c_to_ms(0.01)
"""Hundredth of a power cycle in milliseconds"""

MAX_X = 30_000_000
MAX_Y = 30_000_000

PROHIBITED_REGION_POLYGON = [
    [0.01, MAX_Y],
    [0.01, 500],
    [analysis.ms_to_c(1), 200],
    [analysis.ms_to_c(3), 140],
    [analysis.ms_to_c(3), 120],
    [analysis.ms_to_c(20), 120],
    [analysis.ms_to_c(500), 120],
    [analysis.ms_to_c(500), 110],
    [analysis.ms_to_c(10000), 110],
    [analysis.ms_to_c(MAX_X), 110],
    [analysis.ms_to_c(MAX_X), MAX_Y],
    [0.01, MAX_Y]
]
"""Polygon representing the prohibited region"""

NO_DAMAGE_REGION_POLYGON = [
    [analysis.ms_to_c(20), 0],
    [analysis.ms_to_c(20), 40],
    [analysis.ms_to_c(20), 70],
    [analysis.ms_to_c(500), 70],
    [analysis.ms_to_c(500), 80],
    [analysis.ms_to_c(10_000), 80],
    [analysis.ms_to_c(10_000), 90],
    [analysis.ms_to_c(MAX_X), 90],
    [analysis.ms_to_c(MAX_X), 0],
    [analysis.ms_to_c(20), 0]
]
"""Polygon representing the no damage region"""

NO_INTERRUPTION_REGION_POLYGON = [
    [0, 0],
    [0, MAX_Y],
    [0.01, MAX_Y],
    [0.01, 500],
    [analysis.ms_to_c(1), 200],
    [analysis.ms_to_c(3), 140],
    [analysis.ms_to_c(3), 120],
    [analysis.ms_to_c(20), 120],
    [analysis.ms_to_c(500), 120],
    [analysis.ms_to_c(500), 110],
    [analysis.ms_to_c(10_000), 110],
    [analysis.ms_to_c(MAX_X), 110],
    [analysis.ms_to_c(MAX_X), 90],
    [analysis.ms_to_c(10_000), 90],
    [analysis.ms_to_c(10_000), 80],
    [analysis.ms_to_c(500), 80],
    [analysis.ms_to_c(500), 70],
    [analysis.ms_to_c(20), 70],
    [analysis.ms_to_c(20), 40],
    [analysis.ms_to_c(20), 0],
    [0, 0]
]
"""Polygon representing the no interruption region"""


def point_in_polygon(x_point: float, y_point: float, polygon: typing.List[typing.List[float]]) -> bool:
    """
    Checks if a point is in a given polygon.
    :param x_point: x
    :param y_point: y
    :param polygon: The polygon to check for inclusion
    :return: Whether or not the given point is in the provided polygon
    """
    polygon = list(map(lambda xy: (xy[0], xy[1]), polygon))
    polygon = shapely.geometry.Polygon(polygon)
    point = shapely.geometry.Point(analysis.ms_to_c(x_point), y_point)
    return polygon.contains(point) or polygon.intersects(point)



def itic_region(rms_voltage: float, duration_ms: float) -> IticRegion:
    """
    Returns the ITIC region of a given RMS voltage and duration.
    The reference curve is at http://www.keysight.com/upload/cmc_upload/All/1.pdf
    :param rms_voltage: The RMS voltage value
    :param duration_ms: The duration of the voltage event in milliseconds
    :return: The appropriate ITIC region enum
    """
    percent_nominal = (rms_voltage / 120.0) * 100.0

    if point_in_polygon(duration_ms, percent_nominal, NO_INTERRUPTION_REGION_POLYGON):
        return IticRegion.NO_INTERRUPTION

    if point_in_polygon(duration_ms, percent_nominal, PROHIBITED_REGION_POLYGON):
        return IticRegion.PROHIBITED

    if point_in_polygon(duration_ms, percent_nominal, NO_DAMAGE_REGION_POLYGON):
        return IticRegion.NO_DAMAGE

    # If it's directly on the line of one of the polygons, its easiest to just say no_interruption
    return IticRegion.NO_INTERRUPTION


def maybe_debug(itic_plugin: typing.Optional['IticPlugin'],
                msg: str):
    """
    Only debug information if this plugin is registered for debugging.
    :param itic_plugin: An instance of the IticPlugin.
    :param msg: The debug message.
    """
    if itic_plugin is not None:
        itic_plugin.debug(msg)

# pylint: disable=W0613
def itic(mauka_message: protobuf.mauka_pb2.MaukaMessage,
         segment_threshold: float,
         itic_plugin: typing.Optional['IticPlugin'] = None,
         opq_mongo_client: typing.Optional[mongo.OpqMongoClient] = None) -> typing.List[int]:
    """
    Computes the ITIC region for a given waveform.
    :param itic_plugin: An instance of this plugin.
    :param mauka_message: A mauka message.
    :param segment_threshold: Threshold for segmentation
    :param opq_mongo_client:  Optional DB client to re-use (otherwise new one will be created)
    :return: ITIC region.
    """
    mongo_client = mongo.get_default_client(opq_mongo_client)
    if len(mauka_message.payload.data) < 0.01:
        maybe_debug(itic_plugin, "Bad payload data length: %d" % len(mauka_message.payload.data))

    maybe_debug(itic_plugin, "Preparing to get segments for %d Vrms values" % len(mauka_message.payload.data))
    # segments = analysis.segment(mauka_message.payload.data, segment_threshold)
    segments = analysis.segment_array(numpy.array(list(mauka_message.payload.data)))

    if len(segments) == 0:
        maybe_debug(itic_plugin, "No segments found. Ignoring")
        return []

    maybe_debug(itic_plugin, "Calculating ITIC with {} segments.".format(len(segments)))

    incident_ids = []
    for i, segment in enumerate(segments):
        # start_idx = segment[0]
        # end_idx = segment[1] + 1
        # subarray = mauka_message.payload.data[start_idx:end_idx]
        segment_len = analysis.c_to_ms(len(segment))
        start_t = analysis.c_to_ms(sum([len(segments[x]) for x in range(0, i)]))
        end_t = start_t + segment_len
        mean_rms = segment.mean()
        maybe_debug(itic_plugin, "start=%f end=%f mean=%f" % (start_t, end_t, mean_rms))

        itic_enum = itic_region(mean_rms, segment_len)

        if itic_enum == IticRegion.NO_INTERRUPTION:
            maybe_debug(itic_plugin, "NO_INTERRUPTION")
            continue
        else:
            incident_start_timestamp_ms = mauka_message.payload.start_timestamp_ms + start_t
            incident_end_timestamp_ms = mauka_message.payload.start_timestamp_ms + end_t
            if itic_enum is IticRegion.PROHIBITED:
                maybe_debug(itic_plugin, "PROHIBITED")
                incident_classification = mongo.IncidentClassification.ITIC_PROHIBITED
            else:
                maybe_debug(itic_plugin, "NO_DAMAGE")
                incident_classification = mongo.IncidentClassification.ITIC_NO_DAMAGE

            incident_id = mongo.store_incident(
                mauka_message.payload.event_id,
                mauka_message.payload.box_id,
                incident_start_timestamp_ms,
                incident_end_timestamp_ms,
                mongo.IncidentMeasurementType.VOLTAGE,
                mean_rms - 120.0,
                [incident_classification],
                [],
                {},
                mongo_client)

            maybe_debug(itic_plugin, "Stored incident")

            maybe_debug(itic_plugin,
                        "Found ITIC incident [{}] from event {} and box {}".format(
                            itic_enum,
                            mauka_message.event_id,
                            mauka_message.box_id))

            incident_ids.append(incident_id)

    return incident_ids


class IticPlugin(plugins.base_plugin.MaukaPlugin):
    """
    Mauka plugin that calculates ITIC for any event that includes a raw waveform
    """
    NAME = "IticPlugin"

    def __init__(self, conf: config.MaukaConfig, exit_event: multiprocessing.Event):
        """
        Initializes this plugin
        :param conf: Configuration dictionary
        :param exit_event: Exit event
        """
        super().__init__(conf, [Routes.rms_windowed_voltage], IticPlugin.NAME, exit_event)
        self.segment_threshold = self.config.get("plugins.IticPlugin.segment.threshold.rms")

    def on_message(self, topic, mauka_message):
        """
        Called async when a topic this plugin subscribes to produces a message
        :param topic: The topic that is producing the message
        :param mauka_message: The message that was produced
        """
        if protobuf.pb_util.is_payload(mauka_message, protobuf.mauka_pb2.VOLTAGE_RMS_WINDOWED):
            self.debug("Recv RmwWindowedVoltage")
            incident_ids = itic(mauka_message,
                                self.segment_threshold,
                                self,
                                self.mongo_client)

            for incident_id in incident_ids:
                # Produce a message to the GC
                self.produce(Routes.laha_gc, protobuf.pb_util.build_gc_update(self.name,
                                                                              protobuf.mauka_pb2.INCIDENTS,
                                                                              incident_id))
        else:
            self.logger.error("Received incorrect mauka message [%s] at IticPlugin",
                              protobuf.pb_util.which_message_oneof(mauka_message))


def rerun(mauka_message: protobuf.mauka_pb2.MaukaMessage,
          segment_threshold: float,
          logger,
          mongo_client: mongo.OpqMongoClient = None):
    """
    Rerun ITIC analysis over the given mauka_message.
    :param mauka_message: The mauka_message containing a box event to re-analyze.
    :param segment_threshold: The threshold for the segmentation algorithm
    :param logger: The application logger
    :param mongo_client: An optional instance of a mongo client
    """
    client = mongo.get_default_client(mongo_client)

    if protobuf.pb_util.is_payload(mauka_message, protobuf.mauka_pb2.VOLTAGE_RMS_WINDOWED):
        itic(mauka_message,
             segment_threshold,
             logger,
             client)
    else:
        logger.error("Received incorrect mauka message [%s] at IticPlugin rerun",
                     protobuf.pb_util.which_message_oneof(mauka_message))
