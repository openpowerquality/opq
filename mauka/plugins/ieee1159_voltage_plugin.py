"""
This plugin calculates the IEEE 1159 voltage events.
"""
import enum
import typing
import multiprocessing

import numpy as np

import analysis
import mongo
import constants

import plugins.base_plugin
import protobuf.mauka_pb2
import protobuf.util

# Pu signifying a current cycle has already been accounted for in an incident
ALREADY_ACCOUNTED = -1

def valid_bound(start, end, cycle_max):
    """
    This function asserts that where a cycle_max is provided the current set of consecutive indices
    (cycle streak) does not exceed the value indicated by cycle_max
    params: start - the starting index of the range being examined
    params: end - the end index of the range being examined
    params: cycle_max - the maximum separation (minus one) allowed between the start and end indices 
    return: bool indicating the range of indices does not exceet cycle streak max provided 
    """
    if(cycle_max == None):
        return True
    else:
        return (end - start) < cycle_max

def indices_to_ranges(indices, cycle_min, cycle_max = None):
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
            if((end + 1 - start) >= cycle_min):
                ranges.append((start, end + 1)) 
                # The plus on is such that the offset end is end of the last cycle included
            start = ind
            end = ind
        prev = ind

    if(end != start):
        ranges.append((start, end + 1))
    return ranges

def nullifiy_and_add_incidents(classes, offsets, ranges, class_key, pus):
    """
    This function takes an array of indices from an rms_feature array (assumed to be valid incidents)
    adds the corresponding IncidentClassification and offset indicating where in the rms_feature 
    array a given incident is located and signals that the incident has already been accounted for.
    params: classes, offsets - lists of the incident classification types and corresponding offsets. Added to
    params: ranges - list for which each entry has the start and end index of an incident
    params: class_key - the type/name of the incident in question
    params: pus - array each entry of which the pu value of a given window (rms/nominal rms). This array
    is changed to indicate an incident already accounted for (the pu values of an incident are set to -1 so
    they will not be considered by future searches for incidents)
    """
    to_nullify = []
    for i in range(len(ranges)):
        start_ind = ranges[i][0] 
        end_ind = ranges[i][1]
        pus[start_ind:end_ind] = ALREADY_ACCOUNTED
        classes.append(class_key) 
        offsets.append(ranges[i])

def find_incidents(classes, offsets, pus, sag_range, swell_range, cycle_min, cycle_max = None): # All of these passed by reference (objects)
    """
    This function adds to the classes and offset lists incident information (type and cycle offsets) by analyzing
    the pus array for segments of pu values according to what range the segments pu values fall into (sag, swell
    interrupt as provided) and if the lengths of the segments are in accordance with the cycle_min and cycle_max
    if incidents are found then the pus array is changed to reflect that the given segment can no longer hold anymore
    incidents. 
    params: classes, offsets - lists of the incident classification types and corresponding offsets. Added to
    params: pus - array each entry of which the pu value of a given window (rms/nominal rms). 
    params: sag_range, swell_range - range of pu values for which a given cycle should be considered a sag/swell
    params: cycle_min/max - the cycle streak length range required for a segment of pus to be classified as an incident.
    max none correponds to no upper limit on the length of the segments
    return: no return but does add to or alter pus, classes and offsets
    """
    indices_swell = np.where(np.logical_and(pus <= swell_range[1], pus >= swell_range[0]))[0]
    indices_sag = np.where(np.logical_and(pus <= sag_range[1], pus >= sag_range[0]))[0]
    
    if(indices_sag.size > cycle_min):
        ranges = indices_to_ranges(indices_sag, cycle_min, cycle_max)
        nullifiy_and_add_incidents(classes, offsets, ranges, mongo.IncidentClassification.VOLTAGE_SAG, pus)

    if(indices_swell.size > cycle_min):
        ranges = indices_to_ranges(indices_swell, cycle_min, cycle_max)
        nullifiy_and_add_incidents(classes, offsets, ranges, mongo.IncidentClassification.VOLTAGE_SWELL, pus)
      
    if(cycle_min >= 60*constants.CYCLES_PER_SECOND):
        indices_interrupt = np.where(np.logical_and(pus <= 0.001, pus >= 0))[0]
        if(indices_swell.size > cycle_min):
            ranges = indices_to_ranges(indices_interrupt, cycle_min, cycle_max)
            nullifiy_and_add_incidents(classes, offsets, ranges, mongo.IncidentClassification.VOLTAGE_INTERRUPTION, pus)
        
def classify_ieee1156_voltage(rms_features):
    """
    This function classifies an ieee1156 voltage incident by analyzing rms_feature array (containing voltage rms values over
    a window/cycle). Searches for incidents in decending order of durations. Reminder: arrays and lists are passed by 
    reference in python
    """
    pus = np.abs(rms_features/constants.NOMINAL_VRMS)
    classes = []
    offsets = []
    
    # Note the order here matters
    find_incidents(classes, offsets, pus, [0.8, 0.9], [1.1, 1.2], 60*constants.CYCLES_PER_SECOND)
    find_incidents(classes, offsets, pus, [0.1, 0.9], [1.1, 1.2], 3*constants.CYCLES_PER_SECOND, 60*constants.CYCLES_PER_SECOND)
    find_incidents(classes, offsets, pus, [0.1, 0.9], [1.1, 1.4], 30, 3*constants.CYCLES_PER_SECOND)
    find_incidents(classes, offsets, pus, [0.1, 0.9], [1.1, 1.8], 0.5, 30)
    
    return classes, offsets

def ieee1159_voltage(mauka_message: protobuf.mauka_pb2.MaukaMessage, rms_features: np.ndarray, 
                     opq_mongo_client: mongo.OpqMongoClient = None): 
    """
    Calculate the ieee1159 voltage incidents and add them to the mongo database
    """
    incidents, cycle_offsets = classify_ieee1156_voltage(rms_features)
    
    for i in range(len(incidents)):
        start_idx = cycle_offsets[i][0]
        end_idx = cycle_offsets[i][1]
        max_deviation_from_nominal = np.amax(np.abs(rms_features[start_idx:end_idx]) - constants.NOMINAL_VRMS) 
        mongo.store_incident(
            mauka_message.payload.event_id,
            mauka_message.payload.box_id,
            mauka_message.payload.start_timestamp_ms + analysis.c_to_ms(start_idx),
            mauka_message.payload.start_timestamp_ms + analysis.c_to_ms(end_idx),
            mongo.IncidentMeasurementType.VOLTAGE,
            max_deviation_from_nominal,
            [incidents[i]],
            [],
            {},
            opq_mongo_client
        )
                
class Ieee1159VoltagePlugin(plugins.base_plugin.MaukaPlugin):
    """
    Mauka plugin that calculates IEEE1159 voltage incidents from rms_waveform
    """
    NAME = "Ieee1159VoltagePlugin"

    def __init__(self, config: typing.Dict, exit_event: multiprocessing.Event):
        """
        Initializes this plugin
        :param config: Configuration dictionary
        :param exit_event: Exit event
        """
        super().__init__(config, ["RmsWindowedVoltage"], Ieee1159VoltagePlugin.NAME, exit_event)

    def on_message(self, topic, mauka_message):
        """
        Called async when a topic this plugin subscribes to produces a message
        :param topic: The topic that is producing the message
        :param mauka_message: The message that was produced
        """
        self.debug("on_message")
        if protobuf.util.is_payload(mauka_message, protobuf.mauka_pb2.VOLTAGE_RMS_WINDOWED):
            ieee1159_voltage(mauka_message,
                             protobuf.util.repeated_as_ndarray(
                                 mauka_message.payload.data
                             ),
                             self.mongo_client
                            )
        else:
            self.logger.error("Received incorrect mauka message [%s] at IticPlugin",
                              protobuf.util.which_message_oneof(mauka_message))
