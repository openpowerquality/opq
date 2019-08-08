"""
This plugin calculates the IEEE 1159 voltage events
"""

import typing
import multiprocessing

import numpy as np
import analysis
import mongo
import constants

import config
import plugins.base_plugin
import protobuf.mauka_pb2
import protobuf.util

# Pu signifying a current cycle has already been accounted for in an incident
ALREADY_ACCOUNTED = -1


def valid_bound(start: int, end: int, cycle_max: int = None) -> bool:
    """
    This function asserts that where a cycle_max, where provided, is not exceeding by the
    current range.
    params: start - the starting index of the range being examined
    params: end - the end index of the range being examined
    params: cycle_max - the maximum separation (minus one) allowed between the start and end indices
    return: bool indicating the range of indices does not exceet cycle streak max provided
    """
    if cycle_max is None:
        return True
    else:
        return (end - start) < cycle_max


def indices_to_ranges(indices: np.ndarray, cycle_min: int, cycle_max: int = None) -> typing.List[tuple]:
    """
    This function looks at an array of indices to find ranges (start and end) of indices that are in accordance with
    the min and max cycle streak length provided.
    params: indices - a numpy array of indices to some other array
    params: cycle_min, cycle_max - the upper and lower bounds of a valid index range length
    """
    ranges = []
    start = indices[0]
    prev = start - 1
    end = start
    for i in range(indices.size):
        ind = indices[i]
        if (ind == (prev + 1)) & valid_bound(start, end, cycle_max):
            end = ind
        else:
            if (end + 1 - start) >= cycle_min:
                ranges.append((start, end + 1))
            start = ind
            end = ind
        prev = ind

    if end != start:
        ranges.append((start, end + 1))
    return ranges


def nullifiy_and_add_incidents(classes: typing.List[mongo.IncidentClassification], offsets: typing.List[tuple],
                               ranges: typing.List[tuple], class_key: mongo.IncidentClassification,
                               pu_array: np.ndarray):
    """
    This function takes an array of indices from an rms_feature array (assumed to be valid incidents)
    adds the corresponding IncidentClassification and cycle offset/index start and ends  and signals
    that the range or rms/pu values can no longer be considered for fur incident.
    params: classes, offsets
    params: ranges - list for which each entry has the start and end index/cycle offset of an incident
    params: class_key - the type/name of the incident in question
    is changed to indicate an incident already accounted for (the pu values of an incident are set to -1 so
    they will not be considered by future searches for incidents)
    """
    for idx, _ in enumerate(ranges):
        start_ind = ranges[idx][0]
        end_ind = ranges[idx][1]
        pu_array[start_ind:end_ind] = ALREADY_ACCOUNTED
        classes.append(class_key)
        offsets.append(ranges[idx])


def find_incidents(classes: typing.List[mongo.IncidentClassification], offsets: typing.List[tuple],
                   pu_array: np.ndarray, sag_range: typing.List[float], swell_range: typing.List[float], cycle_min: int,
                   cycle_max: int = None):
    """
    This function adds to the classes and offset lists incident information (type and cycle offsets) by analyzing
    the pu_array array for segments of pus matching duration (in cycles) and value range specificatons
    If incidents are found the pu_array array is changed to avoid counting a segment in multiple incidents.
    params: classes, offsets - lists of the incident classification types and corresponding offsets.
    params: pu_array - array each entry of which the pu value of a given window (rms/nominal rms).
    params: sag_range, swell_range - range of pu values for which a given cycle should be considered a sag/swell
    params: cycle_min/max - the cycle streak length range required for a segment of pu_array to be classified as an
    incident.
    params: pu_array - are of pu values for each window in the rms_features
    max none correponds to no upper limit on the length of the segments
    return: no return but does add to or alter pu_array, classes and offsets
    """
    indices_swell = np.where(np.logical_and(pu_array <= swell_range[1], pu_array >= swell_range[0]))[0]
    indices_sag = np.where(np.logical_and(pu_array <= sag_range[1], pu_array >= sag_range[0]))[0]

    if indices_sag.size > cycle_min:
        ranges = indices_to_ranges(indices_sag, cycle_min, cycle_max)
        nullifiy_and_add_incidents(classes, offsets, ranges, mongo.IncidentClassification.VOLTAGE_SAG, pu_array)

    if indices_swell.size > cycle_min:
        ranges = indices_to_ranges(indices_swell, cycle_min, cycle_max)
        nullifiy_and_add_incidents(classes, offsets, ranges, mongo.IncidentClassification.VOLTAGE_SWELL, pu_array)

    if cycle_min >= 60 * constants.CYCLES_PER_SECOND:
        indices_interrupt = np.where(np.logical_and(pu_array <= 0.001, pu_array >= 0))[0]
        if indices_swell.size > cycle_min:
            ranges = indices_to_ranges(indices_interrupt, cycle_min, cycle_max)
            nullifiy_and_add_incidents(classes, offsets, ranges, mongo.IncidentClassification.VOLTAGE_INTERRUPTION,
                                       pu_array)


def classify_ieee1159_voltage(rms_features: np.ndarray):
    """
    This function classifies an ieee1159 voltage incident by analyzing rms_feature array (containing voltage rms
    values over
    a window/cycle). Searches for incidents in descending order of duration.
    """
    pu_array = np.abs(rms_features / constants.NOMINAL_VRMS)
    classes = []
    offsets = []

    find_incidents(classes, offsets, pu_array, [0.8, 0.9], [1.1, 1.2], 60 * constants.CYCLES_PER_SECOND)
    find_incidents(classes, offsets, pu_array, [0.1, 0.9], [1.1, 1.2], 3 * constants.CYCLES_PER_SECOND,
                   60 * constants.CYCLES_PER_SECOND)
    find_incidents(classes, offsets, pu_array, [0.1, 0.9], [1.1, 1.4], 30, 3 * constants.CYCLES_PER_SECOND)
    find_incidents(classes, offsets, pu_array, [0.1, 0.9], [1.1, 1.8], 0.5, 30)

    return classes, offsets


def ieee1159_voltage(mauka_message: protobuf.mauka_pb2.MaukaMessage, rms_features: np.ndarray,
                     opq_mongo_client: mongo.OpqMongoClient = None) -> typing.List[int]:
    """
    Calculate the ieee1159 voltage incidents and add them to the mongo database
    """
    incidents, cycle_offsets = classify_ieee1159_voltage(rms_features)
    incident_ids = []

    for idx, incident in enumerate(incidents):
        start_idx = cycle_offsets[idx][0]
        end_idx = cycle_offsets[idx][1]
        deviations = np.abs(rms_features[start_idx:end_idx]) - constants.NOMINAL_VRMS
        # The absolute value of the rms_features here and elsewhere is unecessary provided the rms has been applied
        max_deviation = np.amax(deviations)
        max_deviation_neg = np.amax(-deviations)
        if max_deviation < max_deviation_neg:
            max_deviation = -max_deviation_neg

        incident_id = mongo.store_incident(
            mauka_message.payload.event_id,
            mauka_message.payload.box_id,
            mauka_message.payload.start_timestamp_ms + analysis.c_to_ms(start_idx),
            mauka_message.payload.start_timestamp_ms + analysis.c_to_ms(end_idx),
            mongo.IncidentMeasurementType.VOLTAGE,
            max_deviation,
            [incident],
            [],
            {},
            opq_mongo_client
        )

        incident_ids.append(incident_id)

    return incident_ids


class Ieee1159VoltagePlugin(plugins.base_plugin.MaukaPlugin):
    """
    Mauka plugin that calculates IEEE1159 voltage incidents from rms_waveform
    """
    NAME = "Ieee1159VoltagePlugin"

    def __init__(self, conf: config.MaukaConfig, exit_event: multiprocessing.Event):
        """
        Initializes this plugin
        :param conf: Configuration dictionary
        :param exit_event: Exit event
        """
        super().__init__(conf, ["RmsWindowedVoltage"], Ieee1159VoltagePlugin.NAME, exit_event)

    def on_message(self, topic, mauka_message):
        """
        Called async when a topic this plugin subscribes to produces a message
        :param topic: The topic that is producing the message
        :param mauka_message: The message that was produced
        """
        self.debug("on_message")
        if protobuf.util.is_payload(mauka_message, protobuf.mauka_pb2.VOLTAGE_RMS_WINDOWED):
            incident_ids = ieee1159_voltage(mauka_message,
                                            protobuf.util.repeated_as_ndarray(
                                                mauka_message.payload.data
                                            ),
                                            self.mongo_client)
            for incident_id in incident_ids:
                # Produce a message to the GC
                self.produce("laha_gc", protobuf.util.build_gc_update(self.name,
                                                                      protobuf.mauka_pb2.INCIDENTS,
                                                                      incident_id))

        else:
            self.logger.error("Received incorrect mauka message [%s] at IticPlugin",
                              protobuf.util.which_message_oneof(mauka_message))


def rerun(mauka_message: protobuf.mauka_pb2.MaukaMessage,
          logger,
          mongo_client: mongo.OpqMongoClient = None):
    """
    Retruns this plugin over the provided mauka message.
    :param mauka_message: Mauka message to rerun this plugin over.
    :param logger: Application logger.
    :param mongo_client: An optional mongo client to perform DB queries
    """
    client = mongo.get_default_client(mongo_client)

    if protobuf.util.is_payload(mauka_message, protobuf.mauka_pb2.VOLTAGE_RMS_WINDOWED):
        ieee1159_voltage(mauka_message,
                         protobuf.util.repeated_as_ndarray(
                             mauka_message.payload.data
                         ),
                         client)
    else:
        logger.error("Received incorrect mauka message [%s] at VoltagePlugin rerun",
                     protobuf.util.which_message_oneof(mauka_message))
