"""
This plugin calculates the ITIC region of a voltage, duration pair.
"""
import enum
import typing
import multiprocessing
import threading

import constants
import mongo
import plugins.base

import numpy
import matplotlib.path


class IticRegion(enum.Enum):
    """
    Enumerations of ITIC regions.
    """
    NO_INTERRUPTION = "NO_INTERRUPTION"
    PROHIBITED = "PROHIBITED"
    NO_DAMAGE = "NO_DAMAGE"
    OTHER = "OTHER"


def c_to_ms(c: float) -> float:
    """
    Convert cycles to milliseconds
    :param c: cycles
    :return: milliseconds
    """
    return (c * (1 / 60)) * 1000.0


HUNDREDTH_OF_A_CYCLE = c_to_ms(0.01)
"""Hundredth of a power cycle in milliseconds"""

prohibited_region_polygon = [
    [HUNDREDTH_OF_A_CYCLE, 500],
    [1, 200],
    [3, 140],
    [3, 120],
    [20, 120],
    [5000, 120],
    [5000, 110],
    [10000, 110],
    [10000, 500],
    [HUNDREDTH_OF_A_CYCLE, 500]
]
"""Polygon representing the prohibited region"""

no_damage_region_polygon = [
    [20, 0],
    [20, 40],
    [20, 70],
    [5000, 70],
    [5000, 80],
    [10000, 80],
    [10000, 90],
    [10000, 0],
    [20, 0]
]
"""Polygon representing the no damage region"""

no_interruption_region_polygon = [
    [0, 0],
    [0, 500],
    [HUNDREDTH_OF_A_CYCLE, 500],
    [1, 200],
    [3, 140],
    [3, 120],
    [20, 120],
    [5000, 120],
    [5000, 110],
    [10000, 110],
    [10000, 90],
    [10000, 80],
    [5000, 80],
    [5000, 70],
    [20, 70],
    [20, 40],
    [20, 0],
    [0, 0]
]
"""Polygon representing the no interruption region"""


def point_in_polygon(x: float, y: float, polygon: typing.List[typing.List[float]]) -> bool:
    """
    Checks if a point is in a given polygon.
    :param x: x
    :param y: y
    :param polygon: The polygon to check for inclusion
    :return: Whether or not the given point is in the provided polygon
    """
    path = matplotlib.path.Path(vertices=numpy.array(polygon), closed=True)
    return path.contains_point([x, y])


def itic_region(rms_voltage: float, duration_ms: float) -> enum.Enum:
    """
    Returns the ITIC region of a given RMS voltage and duration.
    The reference curve is at http://www.keysight.com/upload/cmc_upload/All/1.pdf
    :param rms_voltage: The RMS voltage value
    :param duration_ms: The duration of the voltage event in milliseconds
    :return: The appropriate ITIC region enum
    """

    percent_nominal = (rms_voltage / 120.0) * 100.0

    # First, let's check the extreme edge cases
    if duration_ms < c_to_ms(0.01):
        return IticRegion.NO_INTERRUPTION

    if rms_voltage <= 0:
        if duration_ms <= 20:
            return IticRegion.NO_INTERRUPTION
        else:
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
        else:
            return IticRegion.NO_INTERRUPTION

    # In the y-direction
    if percent_nominal >= 500:
        if duration_ms <= HUNDREDTH_OF_A_CYCLE:
            return IticRegion.NO_INTERRUPTION
        else:
            return IticRegion.PROHIBITED

    # If the voltage is not an extreme case, we run point in polygon calculations to determine which region its in
    if point_in_polygon(duration_ms, percent_nominal, no_interruption_region_polygon):
        return IticRegion.NO_INTERRUPTION

    if point_in_polygon(duration_ms, percent_nominal, prohibited_region_polygon):
        return IticRegion.PROHIBITED

    if point_in_polygon(duration_ms, percent_nominal, no_damage_region_polygon):
        return IticRegion.NO_DAMAGE

    # If it's directly on the line of one of the polygons, its easiest to just say no_interruption
    return IticRegion.NO_INTERRUPTION


class IticPlugin(plugins.base.MaukaPlugin):
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
        super().__init__(config, ["RequestDataEvent", "IticRequestEvent"], IticPlugin.NAME, exit_event)
        self.get_data_after_s = self.config["plugins.IticPlugin.getDataAfterS"]

    def itic(self, waveform: numpy.ndarray) -> str:
        """
        Returns the ITIC region as a string given a waveform.
        :param waveform: The waveform to measure.
        :return: ITIC region name for specified waveform
        """
        vrms_vals = self.vrms_waveform(waveform)
        duration_ms = (len(waveform) / constants.SAMPLE_RATE_HZ) * 1000
        vrms_min = numpy.min(vrms_vals)
        vrms_max = numpy.max(vrms_vals)

        if numpy.abs(vrms_min - 120.0) > numpy.abs(vrms_max - 120.0):
            return itic_region(vrms_min, duration_ms).name
        else:
            return itic_region(vrms_max, duration_ms).name

    def perform_itic_calculations(self, event_id: int):
        """
        Called on a timer in a separate thread to allow raw data to be acquired first by makai.
        When raw waveforms are found, ITIC calculations are performed and the result is stored back to box_events collection.
        :param event_id: Event id to calculate itic over.
        """
        try:
            box_events = self.mongo_client.box_events_collection.find({"event_id": event_id})
            for box_event in box_events:
                _id = self.object_id(box_event["_id"])
                box_id = box_event["box_id"]
                waveform = mongo.get_waveform(self.mongo_client, box_event["data_fs_filename"])
                calibrated_waveform = self.calibrate_waveform(waveform, constants.cached_calibration_constant(box_id))
                itic_region_str = self.itic(calibrated_waveform)

                self.mongo_client.box_events_collection.update_one({"_id": _id},
                                                        {"$set": {"itic": itic_region_str}})

                self.logger.debug("Calculated ITIC for " + str(event_id) + ":" + str(box_id) + ":" + itic_region_str)
        except Exception as e:
            self.logger.error("Error performing itic calculation: " + str(e))
            pass

    def on_message(self, topic, message):
        """
        Called async when a topic this plugin subscribes to produces a message
        :param topic: The topic that is producing the message
        :param message: The message that was produced
        """
        event_id = int(message)
        timer = threading.Timer(self.get_data_after_s, self.perform_itic_calculations, (event_id,))
        timer.start()
