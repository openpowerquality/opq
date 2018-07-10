"""
This plugin calculates the ITIC region of a voltage, duration pair.
"""
import enum
import typing
import multiprocessing

import numpy
import matplotlib.path

import analysis
import mongo
import plugins.base_plugin
import protobuf.mauka_pb2
import protobuf.util


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

PROHIBITED_REGION_POLYGON = [
    [HUNDREDTH_OF_A_CYCLE, 500],
    [1, 200],
    [3, 140],
    [3, 120],
    [20, 120],
    [500, 120],
    [500, 110],
    [10000, 110],
    [10000, 500],
    [HUNDREDTH_OF_A_CYCLE, 500]
]
"""Polygon representing the prohibited region"""

NO_DAMAGE_REGION_POLYGON = [
    [20, 0],
    [20, 40],
    [20, 70],
    [500, 70],
    [500, 80],
    [10000, 80],
    [10000, 90],
    [10000, 0],
    [20, 0]
]
"""Polygon representing the no damage region"""

NO_INTERRUPTION_REGION_POLYGON = [
    [0, 0],
    [0, 500],
    [HUNDREDTH_OF_A_CYCLE, 500],
    [1, 200],
    [3, 140],
    [3, 120],
    [20, 120],
    [500, 120],
    [500, 110],
    [10000, 110],
    [10000, 90],
    [10000, 80],
    [500, 80],
    [500, 70],
    [20, 70],
    [20, 40],
    [20, 0],
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
    path = matplotlib.path.Path(vertices=numpy.array(polygon), closed=True)
    return path.contains_point([x_point, y_point])


def itic_region(rms_voltage: float, duration_ms: float) -> IticRegion:
    """
    Returns the ITIC region of a given RMS voltage and duration.
    The reference curve is at http://www.keysight.com/upload/cmc_upload/All/1.pdf
    :param rms_voltage: The RMS voltage value
    :param duration_ms: The duration of the voltage event in milliseconds
    :return: The appropriate ITIC region enum
    """
    percent_nominal = (rms_voltage / 120.0) * 100.0

    # First, let's check the extreme edge cases. This can save us some time computing
    # point in polygon if we can identify an extreme edge case first.
    if duration_ms < analysis.c_to_ms(0.01):
        return IticRegion.NO_INTERRUPTION

    if rms_voltage <= 0:
        if duration_ms <= 20:
            return IticRegion.NO_INTERRUPTION

        return IticRegion.NO_DAMAGE

    # In the x and y directions
    if duration_ms >= 10000 and percent_nominal >= 500:
        return IticRegion.PROHIBITED

    # In the x-direction
    if duration_ms >= 10000:
        if percent_nominal >= 110:
            return IticRegion.PROHIBITED
        elif percent_nominal <= 90:
            return IticRegion.NO_DAMAGE

        return IticRegion.NO_INTERRUPTION

    # In the y-direction
    if percent_nominal >= 500:
        if duration_ms <= HUNDREDTH_OF_A_CYCLE:
            return IticRegion.NO_INTERRUPTION

        return IticRegion.PROHIBITED

    # If the voltage is not an extreme case, we run point in polygon calculations to determine which region its in
    if point_in_polygon(duration_ms, percent_nominal, NO_INTERRUPTION_REGION_POLYGON):
        return IticRegion.NO_INTERRUPTION

    if point_in_polygon(duration_ms, percent_nominal, PROHIBITED_REGION_POLYGON):
        return IticRegion.PROHIBITED

    if point_in_polygon(duration_ms, percent_nominal, NO_DAMAGE_REGION_POLYGON):
        return IticRegion.NO_DAMAGE

    # If it's directly on the line of one of the polygons, its easiest to just say no_interruption
    return IticRegion.NO_INTERRUPTION


def itic(mauka_message: protobuf.mauka_pb2.MaukaMessage, segment_threshold: float, logger=None,
         opq_mongo_client: mongo.OpqMongoClient = None):
    """
    Computes the ITIC region for a given waveform.
    :param mauka_message:
    :param segment_threshold: Threshold for segmentation
    :param logger: Optional logger to use to print information
    :param opq_mongo_client:  Optional DB client to re-use (otherwise new one will be created)
    :return: ITIC region.
    """
    mongo_client = mongo.get_default_client(opq_mongo_client)
    if len(mauka_message.payload.data) < 0.01:
        return

    segments = analysis.segment(mauka_message.payload.data, segment_threshold)

    if logger is not None:
        logger.debug("Calculating ITIC with {} segments.".format(len(segments)))

    for segment in segments:
        start_idx = segment[0]
        end_idx = segment[1] + 1
        subarray = mauka_message.payload.data[start_idx:end_idx]
        mean_rms = numpy.mean(subarray)

        itic_enum = itic_region(mean_rms, analysis.c_to_ms(len(subarray)))

        if itic_enum == IticRegion.NO_INTERRUPTION:
            continue
        else:
            incident_start_timestamp_ms = mauka_message.payload.start_timestamp_ms + analysis.c_to_ms(start_idx)
            incident_end_timestamp_ms = mauka_message.payload.start_timestamp_ms + analysis.c_to_ms(end_idx)
            if itic_enum is IticRegion.PROHIBITED:
                incident_classification = mongo.IncidentClassification.ITIC_PROHIBITED
            else:
                incident_classification = mongo.IncidentClassification.ITIC_NO_DAMAGE

            mongo.store_incident(
                mauka_message.event_id,
                mauka_message.box_id,
                incident_start_timestamp_ms,
                incident_end_timestamp_ms,
                mongo.IncidentMeasurementType.VOLTAGE,
                mean_rms - 120.0,
                [incident_classification],
                [],
                {},
                mongo_client
            )
            if logger is not None:
                logger.debug("Found ITIC incident [{}] from event {} and box {}".format(
                    itic_enum,
                    mauka_message.event_id,
                    mauka_message.box_id
                ))


class IticPlugin(plugins.base_plugin.MaukaPlugin):
    """
    Mauka plugin that calculates ITIC for any event that includes a raw waveform
    """
    NAME = "IticPlugin"

    def __init__(self, config: typing.Dict, exit_event: multiprocessing.Event):
        """
        Initializes this plugin
        :param config: Configuration dictionary
        :param exit_event: Exit event
        """
        super().__init__(config, ["RmsWindowedVoltage"], IticPlugin.NAME, exit_event)
        self.segment_threshold = self.config["plugins.IticPlugin.segment.threshold.rms"]

    def on_message(self, topic, mauka_message):
        """
        Called async when a topic this plugin subscribes to produces a message
        :param topic: The topic that is producing the message
        :param mauka_message: The message that was produced
        """
        self.debug("on_message")
        if protobuf.util.is_payload(mauka_message, protobuf.mauka_pb2.VOLTAGE_RMS_WINDOWED):
            itic(mauka_message,
                 self.segment_threshold,
                 self.logger,
                 self.mongo_client)
        else:
            self.logger.error("Received incorrect mauka message [%s] at IticPlugin",
                              protobuf.util.which_message_oneof(mauka_message))
