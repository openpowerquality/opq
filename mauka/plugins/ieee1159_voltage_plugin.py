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

def greater_equal_than_IeeeDuration(duration_one, duration_two):
    """
    Test if duration_one is greater than or equal to duration_two
    
    params: mongo.IncidentIeeeDuration, mongo.IncidentIeeeDuration
    return: bool (duration_one >= duration_two)
    """
    if(duration_one == mongo.IncidentIeeeDuration.SUSTAINED):
        return True
    elif(duration_two == mongo.IncidentIeeeDuration.SUSTAINED):
        return False
    elif(duration_one == mongo.IncidentIeeeDuration.TEMPORARY):
        return True
    elif(duration_two == mongo.IncidentIeeeDuration.TEMPORARY):
        return False
    elif(duration_one == mongo.IncidentIeeeDuration.MOMENTARY):
        return True
    elif(duration_two == mongo.IncidentIeeeDuration.MOMENTARY):
        return False
    elif(duration_one == mongo.IncidentIeeeDuration.INSTANTANEOUS):
        return True
    elif(duration_two == mongo.IncidentIeeeDuration.INSTANTANEOUS):
        return False
    else:
        return True

def type_and_max_duration(pu): 
    """ 
    From a give pu value, this function determings the type (SAG/SWELL/INTERRUP) and the max duration for which the   
    given pu value is eligible (independent of previous cycles/windows). The pu range for each type  remains the same 
    or gets more restrictive as the duration increases. For example a pu value of 1.11 falls within the pu range of 
    all durations so returning SUSTAINED indicates that the value would be eligible if the duration were SUSTAINED or 
    anything smaller. 
    Uses ranges as specified by IEEE.  
    param: pu (actual rms/nominal rms) 
    return: mongo.IncidentClassification
    return: mongo.IncidentIeeeDuration

    """

    if((pu >= 1.1) & (pu <= 1.8)): # SWELL     
        if(pu <= 1.4):
            if(pu <= 1.2):
                return mongo.IncidentClassification.VOLTAGE_SWELL, mongo.IncidentIeeeDuration.SUSTAINED
            return mongo.IncidentClassification.VOLTAGE_SWELL, mongo.IncidentIeeeDuration.MOMENTARY
        return mongo.IncidentClassification.VOLTAGE_SWELL, mongo.IncidentIeeeDuration.INSTANTANEOUS
    elif((pu >= 0.1) & (pu <= 0.9)): # SAG
        if(pu >= 0.8):
            return mongo.IncidentClassification.VOLTAGE_SAG, mongo.IncidentIeeeDuration.SUSTAINED
        return mongo.IncidentClassification.VOLTAGE_SAG, mongo.IncidentIeeeDuration.TEMPORARY
    elif(pu <= 0.001): # INTERRUPTION
        return mongo.IncidentClassification.VOLTAGE_INTERRUPTION, mongo.IncidentIeeeDuration.SUSTAINED
    return mongo.IncidentClassification.UNDEFINED, mongo.IncidentIeeeDuration.UNDEFINED



def durationAsContinuous(class_type, cycle_streak):
    
    """
    This function returns the duration according to cycle streak and independent of pu. 
    In doings so it is the duration assuming that the current cycle is a continuation of the previous incident.
    param: class_type (mongo.IncidentClassification), only used to handle the special case of VOLTAGE_INTERRUPTIONs
    param:cycle_streak the number of similar cycles observed prior to the current cycle + 1. Essentially what the
    duration would be if current cycle was similar to previous
    """
    if(class_type == mongo.IncidentClassification.VOLTAGE_INTERRUPTION):
        if (cycle_streak < 60*constants.CYCLES_PER_SECOND):
            return mongo.IncidentIeeeDuration.UNDEFINED
        return mongo.IncidentIeeeDuration.SUSTAINED
    elif((cycle_streak >= 0.5) & (cycle_streak <= 30)):
        return mongo.IncidentIeeeDuration.INSTANTANEOUS
    elif((cycle_streak > 30) & (cycle_streak <= 3*constants.CYCLES_PER_SECOND)):
        return mongo.IncidentIeeeDuration.MOMENTARY
    elif((cycle_streak > 3*constants.CYCLES_PER_SECOND) & (cycle_streak <= 60*constants.CYCLES_PER_SECOND)):
        return mongo.IncidentIeeeDuration.TEMPORARY
    elif(cycle_streak > 60*constants.CYCLES_PER_SECOND):
        return mongo.IncidentIeeeDuration.SUSTAINED
    else:
        return mongo.IncidentIeeeDuration.UNDEFINED # Should not be reached
    
def classifyIeee1159(rms_windowed_features):
    """
    This function looks through the rms_windowed_features numpy array to classify Ieee1159 Voltage incidents.
    It does so by iterating through the rms values in the provided array and looking for streaks of similar
    incidents. Note each entry of the provided array represents the rms value for a cycle/window (currently
    a window is a cycle). 
    
    Note that as is the actual writing of the incident to the mongo db is not performed within this function.
    This is done for testing purposes (making it easier to interface with the unittest by providing a simple,
    exportable function)
    
    return: incident_classes. A list of the incidents (mongo.IeeeClassifiaction) found
    return: incident_timestamps. A list of pairs of values representing the number of cycles from the start of 
    the array to beginning and the end of the incident. Meant to later be converted to ms timestamps
    """
    incident_cycle_offset_start = 0 # Number of cycles from the start of the array to the start of the incident
    window_streak = 0

    curr_type = mongo.IncidentClassification.UNDEFINED 
    curr_duration = mongo.IncidentIeeeDuration.UNDEFINED
    prev_type = mongo.IncidentClassification.UNDEFINED 
    prev_duration = mongo.IncidentIeeeDuration.UNDEFINED
    incident_classes = []
    incident_timestamps = []
    
    for rms_voltage in np.nditer(rms_windowed_features):
        
        curr_type, curr_duration = type_and_max_duration(np.abs(rms_voltage/constants.NOMINAL_VRMS))
        duration_current_included = durationAsContinuous(curr_type, window_streak + 1)
        
        if(curr_type == mongo.IncidentClassification.UNDEFINED):
            if(prev_type == mongo.IncidentClassification.UNDEFINED):
                incident_cycle_offset_start += 1
            elif((prev_type == mongo.IncidentClassification.VOLTAGE_INTERRUPTION) & (prev_duration == mongo.IncidentIeeeDuration.UNDEFINED)):
                incident_cycle_offset_start += window_streak + 1
                window_streak = 0
            else:
                incident_classes.append(prev_type)
                incident_timestamps.append([incident_cycle_offset_start, incident_cycle_offset_start + window_streak])
                incident_cycle_offset_start += window_streak + 1
                window_streak = 0
        elif(curr_type == prev_type): # Neither are UNDEFINED
            if(greater_equal_than_IeeeDuration(curr_duration, duration_current_included)): 
                # Since the current and previous have the same type and the max duration of 
                # the current works with cycle streak. Change the duration to reflect the actual cycle streak
                curr_duration = duration_current_included 
                window_streak += 1                              
            elif((prev_type == mongo.IncidentClassification.VOLTAGE_INTERRUPTION) & (prev_duration == mongo.IncidentIeeeDuration.UNDEFINED)):
                incident_cycle_offset_start += window_streak
                window_streak = 1
                curr_duration = durationAsContinuous(curr_type, window_streak)                   
            else:
                # The current pU value is not eligible for the actual duration if this cycle was included
                # as such we have a change of incident and add the incident that just finished TO our collection
                # of incidents. Check to make sure that provided the previous incident was in fact valid (e.g not an interrption range pu
                # value with insufficient duration)
                incident_classes.append(prev_type)
                incident_timestamps.append([incident_cycle_offset_start, incident_cycle_offset_start + window_streak])    
                incident_cycle_offset_start += window_streak
                window_streak = 1
                curr_duration = durationAsContinuous(curr_type, window_streak)                   
        elif(prev_type == mongo.IncidentClassification.UNDEFINED): 
            window_streak = 1
            curr_duration = durationAsContinuous(curr_type, window_streak)    
        else: # Different types both not UNDEFINED
            if((prev_type == mongo.IncidentClassification.VOLTAGE_INTERRUPTION) & (prev_duration == mongo.IncidentIeeeDuration.UNDEFINED)):
                incident_cycle_offset_start += window_streak
            else:
                incident_classes.append(prev_type)
                incident_timestamps.append([incident_cycle_offset_start, incident_cycle_offset_start + window_streak])    
                incident_cycle_offset_start += window_streak
            window_streak = 1
            curr_duration = durationAsContinuous(curr_type, window_streak)            
            
        prev_type = curr_type
        prev_duration = curr_duration
        
    if ((window_streak > 0) & (curr_duration != mongo.IncidentIeeeDuration.UNDEFINED)):
        incident_classes.append(curr_type)
        incident_timestamps.append([incident_cycle_offset_start, incident_cycle_offset_start + window_streak])
        
    return incident_classes, incident_timestamps

def ieee1159_voltage(mauka_message: protobuf.mauka_pb2.MaukaMessage, rms_features: np.ndarray, 
                     opq_mongo_client: mongo.OpqMongoClient = None): 
    """
    Calculate the ieee1159 voltage incidents and add them to the mongo database
    """
    incidents, cycle_offsets = classifyIeee1159(rms_features)
    
    for i in range(len(incidents)):
        start_idx = cycle_offsets[i][0]
        end_idx = cycle_offsets[i][1]
        max_deviation_from_nominal = np.amax(np.abs(rms_features[start_idx:end_idx])) - constants.NOMINAL_VRMS
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