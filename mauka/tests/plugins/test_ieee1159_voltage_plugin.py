import unittest
import numpy as np

import analysis
import constants
from plugins.ieee1159_voltage_plugin import classify_ieee1156_voltage
from plugins.makai_event_plugin import vrms, vrms_waveform
from mongo import IncidentClassification

"""
The following functions are used just for testing purposes. Do not try to trick them...
"""
def determineClass(pu, cycle_streak): 
    """ 
    Determines the voltage incident type based off of the IEEE1156 standards. Note that undervoltages and overvoltages
    are simply considered sags/swells of longer duration
    param: pu (actual rms/nominal rms)
    param: cycle_streak streak of cycles for a given incident type
    return: IncidentClassification for the given params
    """
    if((cycle_streak >= 0.5) & (cycle_streak <= 30)):
        if((pu >= 0.1) & (pu <= 0.9)):
            return IncidentClassification.VOLTAGE_SAG        
        elif((pu >= 1.1) & (pu <= 1.8)):
            return IncidentClassification.VOLTAGE_SWELL
        elif(pu <= 0.001):
            return IncidentClassification.UNDEFINED
    elif((cycle_streak > 30) & (cycle_streak <= 3*constants.CYCLES_PER_SECOND)):
        if((pu >= 0.1) & (pu <= 0.9)):
            return IncidentClassification.VOLTAGE_SAG
        elif((pu >= 1.1) & (pu <= 1.4)):
            return IncidentClassification.VOLTAGE_SWELL
        elif(pu <= 0.001):
            return IncidentClassification.UNDEFINED
    elif((cycle_streak > 3*constants.CYCLES_PER_SECOND) & (cycle_streak <= 60*constants.CYCLES_PER_SECOND)):
        if((pu >= 0.1) & (pu <= 0.9)):
            return IncidentClassification.VOLTAGE_SAG
        elif((pu >= 1.1) & (pu <= 1.2)):
            return IncidentClassification.VOLTAGE_SWELL
        elif(pu <= 0.001):
            return IncidentClassification.UNDEFINED
    elif(cycle_streak > 60*constants.CYCLES_PER_SECOND):
        if((pu >= 0.8) & (pu <= 0.9)):
            return IncidentClassification.VOLTAGE_SAG
        elif((pu >= 1.1) & (pu <= 1.2)):
            return IncidentClassification.VOLTAGE_SWELL
        elif(pu <= 0.001):
            return IncidentClassification.VOLTAGE_INTERRUPTION
    return IncidentClassification.UNDEFINED


def generate_sample_waveform_rmsfeatures(cycles, a_multipliers):
    """ 
    This function generated a waveform following the template specifiec in cycles and a_muplipliers
    params: cycles, a_multipliers dictates regions of the waveform (numbers of cycles) and their amplitudes relative 
    to nominal
    returns: rms values for each cycle of the generated waveform
    """
    fs = constants.SAMPLE_RATE_HZ
    f_nominal = constants.CYCLES_PER_SECOND
    a_nominal = 170
    waves = []
    t_tot = 0
    for i in range(len(cycles)):
        num_cycles = cycles[i]
        a_multiplier = a_multipliers[i]
        t = num_cycles/f_nominal
        t_tot += t
        waves.append(a_nominal*a_multiplier*np.sin(2*f_nominal*np.pi*np.linspace(0.0, t, (int)(fs*t), endpoint = False)))
    
    test_waveform = waves[0]
    for j in range(len(waves) - 1):
        test_waveform = np.concatenate((test_waveform, waves[j+1]))

    rms_features = vrms_waveform(test_waveform)

    return rms_features

def generate_keys(cycles, a_multipliers):
    """
    This generates a list of the key types and cycle durations. 
    
    params: cycles - this essential segments the wave into constant behaving regions. 
    Each entry of this list provides a cycle length of a region and the pu value of that region is provided
    in the corresponding index of a_multipliers. 
    params: a_multipliers - each entry is a pu value of wave region
    returns: list of start and end timestamps in cycles relative to the start of the array. 
    returns: list of DEFINED IncidentClassifications associate with each time/cycle interval.  
    
    NOTE(!): The length of each parameter list is the number of different regions in the wave. This function that and assumes
    no interaction between regions. If you violate these assumption, a test may fail due to the key_class/timestamps 
    being incorrect. If this assumption does not work for your test cases, enter keys by manually. 

    """
    # assert(len(cycles) == len(a_multipliers))
    key_classes = []
    key_timestamps = []
    cycle_offset = 0
    for i in range(len(cycles)):
        Ieee1156Class = determineClass(a_multipliers[i], cycles[i])
        if (Ieee1156Class != IncidentClassification.UNDEFINED):
            key_classes.append(Ieee1156Class)
            key_timestamps.append([cycle_offset, cycle_offset + cycles[i]])
        cycle_offset += cycles[i]
    return key_classes, key_timestamps


class Ieee1159VoltagePluginTests(unittest.TestCase):


    def test_many(self):
        cycles = [200, 5000, 100, 4000, 180, 220, 6000, 10, 10, 10] 
        a_multipliers = [0.2, 0.88, 2.0, 1.11, 1.0, 1.11, 0.000001, 1.3, 0.5, 10] 
        key_classes, key_timestamps = generate_keys(cycles, a_multipliers)
        results, time_stamps = classify_ieee1156_voltage(generate_sample_waveform_rmsfeatures(cycles, a_multipliers))
        self.assertEqual(set(results), set(key_classes))
        self.assertEqual(set(time_stamps), set(key_timestamps))
        
    def test_single(self):
        cycles = [190] 
        a_multipliers = [1.1] 
        key_classes, key_timestamps = generate_keys(cycles, a_multipliers)
        results, time_stamps = classify_ieee1156_voltage(generate_sample_waveform_rmsfeatures(cycles, a_multipliers))
        self.assertEqual(set(results), set(key_classes))
        self.assertEqual(set(time_stamps), set(key_timestamps))
        
    def test_sag_swell_separated(self):
        cycles = [2, 21, 100, 10] 
        a_multipliers = [1, 1.3, 1.0, 0.2] 
        key_classes, key_timestamps = generate_keys(cycles, a_multipliers)
        results, time_stamps = classify_ieee1156_voltage(generate_sample_waveform_rmsfeatures(cycles, a_multipliers))
        self.assertEqual(set(results), set(key_classes))
        self.assertEqual(set(time_stamps), set(key_timestamps))

    def test_odd_undefined_separated(self):
        cycles = [31, 100, 180] 
        a_multipliers = [1.3, 2.0, 0.2] 
        key_classes, key_timestamps = generate_keys(cycles, a_multipliers)
        results, time_stamps = classify_ieee1156_voltage(generate_sample_waveform_rmsfeatures(cycles, a_multipliers))
        self.assertEqual(set(results), set(key_classes))
        self.assertEqual(set(time_stamps), set(key_timestamps))
        
    def test_no_separation_end(self):
        cycles = [190, 270]
        a_multipliers = [1.1, 0.6]
        key_classes, key_timestamps = generate_keys(cycles, a_multipliers)
        results, time_stamps = classify_ieee1156_voltage(generate_sample_waveform_rmsfeatures(cycles, a_multipliers))
        self.assertEqual(set(results), set(key_classes))
        self.assertEqual(set(time_stamps), set(key_timestamps))
        
    def test_sustained(self):
        cycles = [4000, 5000, 10, 60000]
        a_multipliers = [0.85, 1.11, 1.0, 0.0005]
        key_classes, key_timestamps = generate_keys(cycles, a_multipliers)
        results, time_stamps = classify_ieee1156_voltage(generate_sample_waveform_rmsfeatures(cycles, a_multipliers))
        self.assertEqual(set(results), set(key_classes))
        self.assertEqual(set(time_stamps), set(key_timestamps))
        
    def test_no_separation_false_end(self):
        cycles = [10, 30, 100, 100] 
        a_multipliers = [1.0, 0.8, 1.3, 0.00005] 
        key_classes, key_timestamps = generate_keys(cycles, a_multipliers)
        results, time_stamps = classify_ieee1156_voltage(generate_sample_waveform_rmsfeatures(cycles, a_multipliers))
        self.assertEqual(set(results), set(key_classes))
        self.assertEqual(set(time_stamps), set(key_timestamps))
        
    def test_false_interruption(self):
        cycles = [10, 400, 100, 500]
        a_multipliers = [1.0, 0.00005, 1.3, 0.00005]
        key_classes, key_timestamps = generate_keys(cycles, a_multipliers)
        results, time_stamps = classify_ieee1156_voltage(generate_sample_waveform_rmsfeatures(cycles, a_multipliers))
        self.assertEqual(set(results), set(key_classes))
        self.assertEqual(set(time_stamps), set(key_timestamps))
        
    def test_all_undefined(self):
        cycles = [10, 400, 4000, 500]
        a_multipliers = [0.00005, 0.00005, 2.0, 0.00005]
        key_classes, key_timestamps = generate_keys(cycles, a_multipliers)
        results, time_stamps = classify_ieee1156_voltage(generate_sample_waveform_rmsfeatures(cycles, a_multipliers))
        self.assertEqual(set(results), set(key_classes))
        self.assertEqual(set(time_stamps), set(key_timestamps))
