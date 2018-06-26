from plugins.FrequencyVariationPlugin import frequency_variation
from OpqMauka import load_config

import unittest
import mongo
import numpy
import constants


class FrequencyVariationTests(unittest.TestCase):

    def setUp(self):
        self.freq_ref = constants.CYCLES_PER_SECOND
        self.config = load_config("../../config.json")
        self.freq_var_low = float(self.config["plugins.FrequencyVariationPlugin.frequency.variation.threshold.low"])
        self.freq_var_high = float(self.config["plugins.FrequencyVariationPlugin.frequency.variation.threshold.high"])
        self.freq_interruption = float(self.config["plugins.FrequencyVariationPlugin.frequency.interruption"])

    def test_no_variation(self):
        """
        Test frequencies between 60.1Hz and 59.9Hz, we expect to classify these frequencies as non-incidents, i.e.
        frequency_variation() should return false along with the calculated variation which should be less than 0.1
        """

        """FrequencyVariationPlugin frequency_variation Method"""
        test_frequencies = [59.91, 60.0, 60.09]
        for freq in test_frequencies:
            incident_type, variation = frequency_variation(freq, self.freq_ref, self.freq_var_high,
                                                                self.freq_var_low, self.freq_interruption)
            if incident_type:
                message = "Frequency:{} Hz Classified as {}".format(freq, incident_type.value)
            else:
                message = ""
            self.assertEqual(incident_type, False, msg=message)

            message = "Frequency Variation:{} Hz Expected:{} Hz".format(variation, freq - self.freq_ref)
            self.assertEqual(variation, freq - self.freq_ref, msg=message)

    def test_swell(self):
        """
        Test frequencies greater than or equal to 60.1Hz, we expect to classify these frequencies as swells
        """

        """FrequencyVariationPlugin frequency_variation Method"""
        test_frequencies = [60.1, 60.25, 70.0]
        for freq in test_frequencies:
            incident_type, variation = frequency_variation(freq, self.freq_ref, self.freq_var_high, self.freq_var_low,
                                                           self.freq_interruption)
            if incident_type:
                message = "Frequency:{} Hz Classified as {}".format(freq, incident_type.value)
            else:
                message = "Frequency:{} Hz Classified as No Variation"
            self.assertEqual(incident_type, mongo.IncidentClassification.FREQUENCY_SWELL, msg=message)

            message = "Frequency Variation:{} Hz Expected:{} Hz".format(variation, freq - self.freq_ref)
            self.assertEqual(variation, freq - self.freq_ref, msg=message)

    def test_sag(self):
        """
        Test frequencies between 58Hz and 59.9Hz, we expect to classify these frequencies as sags
        """

        """FrequencyVariationPlugin frequency_variation Method"""
        test_frequencies = [58.01, 59, 59.9]
        for freq in test_frequencies:
            incident_type, variation = frequency_variation(freq, self.freq_ref, self.freq_var_high, self.freq_var_low,
                                                           self.freq_interruption)
            if incident_type:
                message = "Frequency:{} Hz Classified as {}".format(freq, incident_type.value)
            else:
                message = "Frequency:{} Hz Classified as No Variation"
            self.assertEqual(incident_type, mongo.IncidentClassification.FREQUENCY_SAG, msg=message)

            message = "Frequency Variation:{} Hz Expected:{} Hz".format(variation, freq - self.freq_ref)
            self.assertEqual(variation, freq - self.freq_ref, msg=message)

    def test_interruption(self):
        """
        Test frequencies less than or equal to 58Hz, we expect to classify these frequencies as interruptions
        """

        """FrequencyVariationPlugin frequency_variation Method"""
        test_frequencies = [58.0, 50.0, 0.0]
        for freq in test_frequencies:
            incident_type, variation = frequency_variation(freq, self.freq_ref, self.freq_var_high, self.freq_var_low,
                                                           self.freq_interruption)
            if incident_type:
                message = "Frequency:{} Hz Classified as {}".format(freq, incident_type.value)
            else:
                message = "Frequency:{} Hz Classified as No Variation"
            self.assertEqual(incident_type, mongo.IncidentClassification.FREQUENCY_INTERRUPTION, msg=message)

            message = "Frequency Variation:{} Hz Expected:{} Hz".format(variation, freq - self.freq_ref)
            self.assertEqual(variation, freq - self.freq_ref, msg=message)

