from plugins.frequency_variation_plugin import frequency_variation
from plugins.frequency_variation_plugin import frequency_incident_classifier
from opq_mauka import load_config

import unittest
import mongo
import numpy
import constants


class FrequencyVariationTests(unittest.TestCase):

    def setUp(self):
        self.freq_ref = constants.CYCLES_PER_SECOND
        self.config = load_config("./config.json")
        self.freq_var_low = float(self.config["plugins.FrequencyVariationPlugin.frequency.variation.threshold.low"])
        self.freq_var_high = float(self.config["plugins.FrequencyVariationPlugin.frequency.variation.threshold.high"])
        self.freq_interruption = float(self.config["plugins.FrequencyVariationPlugin.frequency.interruption"])
        self.frequency_window_cycles = int(self.config["plugins.MakaiEventPlugin.frequencyWindowCycles"])

    def test_no_variation(self):
        """
        Test frequencies between 60.1Hz and 59.9Hz, we expect to classify these frequencies as non-incidents, i.e.
        frequency_variation() should return false along with the calculated variation which should be less than 0.1
        frequency_incident_classifier() should return an empty list
        """

        """frequency_variation Method"""
        test_frequencies = [59.91, 60.0, 60.09]
        for freq in test_frequencies:
            incident_type, variation = frequency_variation(freq, self.freq_ref, self.freq_var_high, self.freq_var_low,
                                                           self.freq_interruption)
            if incident_type:
                message = "Frequency:{} Hz Classified as {}".format(freq, incident_type.value)
            else:
                message = ""
            self.assertEqual(incident_type, False, msg=message)

            message = "Frequency Variation:{} Hz Expected:{} Hz".format(variation, freq - self.freq_ref)
            self.assertEqual(variation, freq - self.freq_ref, msg=message)

        """frequency_incident_classifier Method"""
        test_windowed_frequencies = [60.0 for _ in range(1)]  # 1 window of samples,
        incidents = frequency_incident_classifier(0, "", numpy.array(test_windowed_frequencies), 0, self.freq_ref,
                                                  self.freq_var_high, self.freq_var_low, self.freq_interruption,
                                                  int(self.frequency_window_cycles * constants.SAMPLES_PER_CYCLE))
        message = "Frequency Window:{} Classified as:{}".format(test_windowed_frequencies, incidents)
        self.assertEqual(len(incidents), 0, msg=message)

        test_windowed_frequencies = [60.0 for _ in range(10)]  # 10 windows of samples,
        incidents = frequency_incident_classifier(0, "", numpy.array(test_windowed_frequencies), 0, self.freq_ref,
                                                  self.freq_var_high, self.freq_var_low, self.freq_interruption,
                                                  int(self.frequency_window_cycles * constants.SAMPLES_PER_CYCLE))
        message = "Frequency Windows:{} Classified as:{}".format(test_windowed_frequencies, incidents)
        self.assertEqual(len(incidents), 0, msg=message)

    def test_swell(self):
        """
        Test frequencies greater than or equal to 60.1Hz, we expect to classify these frequencies as swells
        """

        """frequency_variation Method"""
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

        """frequency_incident_classifier Method"""
        test_windowed_frequencies = [70.0 for _ in range(1)]  # 1 window of samples
        incidents = frequency_incident_classifier(0, "", numpy.array(test_windowed_frequencies), 0, self.freq_ref,
                                                  self.freq_var_high, self.freq_var_low, self.freq_interruption,
                                                  int(self.frequency_window_cycles * constants.SAMPLES_PER_CYCLE))
        message = "Frequency Window:{} Classified as:{}".format(test_windowed_frequencies, incidents)
        self.assertEqual(len(incidents), 1, msg=message)

        # 10 windows of samples
        test_windowed_frequencies = [70.0 for _ in range(10)]

        incidents = frequency_incident_classifier(0, "", numpy.array(test_windowed_frequencies), 0, self.freq_ref,
                                                  self.freq_var_high, self.freq_var_low, self.freq_interruption,
                                                  int(self.frequency_window_cycles * constants.SAMPLES_PER_CYCLE))

        message = "Frequency Windows:{} Classified as:{}".format(test_windowed_frequencies, incidents)
        self.assertEqual(len(incidents), 1, msg=message)
        self.assertAlmostEqual(incidents[0]["incident_start_ts"], 0, delta=0.1)
        self.assertAlmostEqual(incidents[0]["incident_end_ts"], len(test_windowed_frequencies) *
                               constants.SAMPLES_PER_CYCLE / constants.SAMPLE_RATE_HZ * 1000, delta=0.1)
        self.assertAlmostEqual(incidents[0]["avg_deviation"], numpy.average(test_windowed_frequencies[0:10]) - 60.0,
                               delta=0.1)
        self.assertEqual(incidents[0]["incident_classifications"], [mongo.IncidentClassification.FREQUENCY_SWELL])

        # 20 windows of samples, incident from index 0 to 9
        test_windowed_frequencies = [70.0 for _ in range(10)] + [60.0 for _ in range(10)]

        incidents = frequency_incident_classifier(0, "", numpy.array(test_windowed_frequencies), 0, self.freq_ref,
                                                  self.freq_var_high, self.freq_var_low, self.freq_interruption,
                                                  int(self.frequency_window_cycles * constants.SAMPLES_PER_CYCLE))

        message = "Frequency Windows:{} Classified as:{}".format(test_windowed_frequencies, incidents)
        self.assertEqual(len(incidents), 1, msg=message)
        self.assertAlmostEqual(incidents[0]["incident_start_ts"], 0, delta=0.1)
        self.assertAlmostEqual(incidents[0]["incident_end_ts"], 10 * constants.SAMPLES_PER_CYCLE /
                               constants.SAMPLE_RATE_HZ * 1000, delta=0.1)
        self.assertAlmostEqual(incidents[0]["avg_deviation"], numpy.average(test_windowed_frequencies[0:10]) - 60.0,
                               delta=0.1)
        self.assertEqual(incidents[0]["incident_classifications"], [mongo.IncidentClassification.FREQUENCY_SWELL])

        # 20 windows of samples, incident from index 10 to 19
        test_windowed_frequencies = [60.0 for _ in range(10)] + [70.0 for _ in range(10)]

        incidents = frequency_incident_classifier(0, "", numpy.array(test_windowed_frequencies), 0, self.freq_ref,
                                                  self.freq_var_high, self.freq_var_low, self.freq_interruption,
                                                  int(self.frequency_window_cycles * constants.SAMPLES_PER_CYCLE))

        message = "Frequency Windows:{} Classified as:{}".format(test_windowed_frequencies, incidents)
        self.assertEqual(len(incidents), 1, msg=message)
        self.assertAlmostEqual(incidents[0]["incident_start_ts"], 10 * constants.SAMPLES_PER_CYCLE /
                               constants.SAMPLE_RATE_HZ * 1000, delta=0.1)
        self.assertAlmostEqual(incidents[0]["incident_end_ts"], len(test_windowed_frequencies) *
                               constants.SAMPLES_PER_CYCLE / constants.SAMPLE_RATE_HZ * 1000, delta=0.1)
        self.assertAlmostEqual(incidents[0]["avg_deviation"], numpy.average(test_windowed_frequencies[10:20]) - 60.0,
                               delta=0.1)
        self.assertEqual(incidents[0]["incident_classifications"], [mongo.IncidentClassification.FREQUENCY_SWELL])

        # 30 windows of samples, incident from index 10 to 19
        test_windowed_frequencies = [60.0 for _ in range(10)] + [70.0 for _ in range(10)] + [60.0 for _ in range(10)]

        incidents = frequency_incident_classifier(0, "", numpy.array(test_windowed_frequencies), 0, self.freq_ref,
                                                  self.freq_var_high, self.freq_var_low, self.freq_interruption,
                                                  int(self.frequency_window_cycles * constants.SAMPLES_PER_CYCLE))

        message = "Frequency Windows:{} Classified as:{}".format(test_windowed_frequencies, incidents)
        self.assertEqual(len(incidents), 1, msg=message)
        self.assertAlmostEqual(incidents[0]["incident_start_ts"], 10 * constants.SAMPLES_PER_CYCLE /
                               constants.SAMPLE_RATE_HZ * 1000, delta=0.01)
        self.assertAlmostEqual(incidents[0]["incident_end_ts"], 20 * constants.SAMPLES_PER_CYCLE /
                               constants.SAMPLE_RATE_HZ * 1000, delta=0.01)
        self.assertAlmostEqual(incidents[0]["avg_deviation"], numpy.average(test_windowed_frequencies[10:20]) - 60.0,
                               delta=0.01)
        self.assertEqual(incidents[0]["incident_classifications"], [mongo.IncidentClassification.FREQUENCY_SWELL])

        # 25 windows of samples, incidents from index 5 to 9 and 15 to 19
        test_windowed_frequencies = [60.0 for _ in range(5)] + [70.0 for _ in range(5)] + [60.0 for _ in range(5)] + \
                                    [70.0 for _ in range(5)] + [60.0 for _ in range(5)]

        incidents = frequency_incident_classifier(0, "", numpy.array(test_windowed_frequencies), 0, self.freq_ref,
                                                  self.freq_var_high, self.freq_var_low, self.freq_interruption,
                                                  int(self.frequency_window_cycles * constants.SAMPLES_PER_CYCLE))

        message = "Frequency Windows:{} Classified as:{}".format(test_windowed_frequencies, incidents)
        self.assertEqual(len(incidents), 2, msg=message)
        self.assertAlmostEqual(incidents[0]["incident_start_ts"], 5 * constants.SAMPLES_PER_CYCLE /
                               constants.SAMPLE_RATE_HZ * 1000, delta=0.01)
        self.assertAlmostEqual(incidents[0]["incident_end_ts"], 10 * constants.SAMPLES_PER_CYCLE /
                               constants.SAMPLE_RATE_HZ * 1000, delta=0.01)
        self.assertAlmostEqual(incidents[0]["avg_deviation"], numpy.average(test_windowed_frequencies[5:10]) - 60.0,
                               delta=0.01)
        self.assertEqual(incidents[0]["incident_classifications"], [mongo.IncidentClassification.FREQUENCY_SWELL])

        self.assertEqual(len(incidents), 2, msg=message)
        self.assertAlmostEqual(incidents[1]["incident_start_ts"], 15 * constants.SAMPLES_PER_CYCLE /
                               constants.SAMPLE_RATE_HZ * 1000, delta=0.01)
        self.assertAlmostEqual(incidents[1]["incident_end_ts"], 20 * constants.SAMPLES_PER_CYCLE /
                               constants.SAMPLE_RATE_HZ * 1000, delta=0.01)
        self.assertAlmostEqual(incidents[1]["avg_deviation"], numpy.average(test_windowed_frequencies[15:20]) - 60.0,
                               delta=0.01)
        self.assertEqual(incidents[1]["incident_classifications"], [mongo.IncidentClassification.FREQUENCY_SWELL])

    def test_sag(self):
        """
        Test frequencies between 58Hz and 59.9Hz, we expect to classify these frequencies as sags
        """

        """frequency_variation Method"""
        test_frequencies = [58.01, 59.0, 59.9]
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

        """frequency_incident_classifier Method"""
        test_windowed_frequencies = [59.0 for _ in range(1)]  # 1 window of samples
        incidents = frequency_incident_classifier(0, "", numpy.array(test_windowed_frequencies), 0, self.freq_ref,
                                                  self.freq_var_high, self.freq_var_low, self.freq_interruption,
                                                  int(self.frequency_window_cycles * constants.SAMPLES_PER_CYCLE))
        message = "Frequency Window:{} Classified as:{}".format(test_windowed_frequencies, incidents)
        self.assertEqual(len(incidents), 1, msg=message)

        # 10 windows of samples
        test_windowed_frequencies = [59.0 for _ in range(10)]

        incidents = frequency_incident_classifier(0, "", numpy.array(test_windowed_frequencies), 0, self.freq_ref,
                                                  self.freq_var_high, self.freq_var_low, self.freq_interruption,
                                                  int(self.frequency_window_cycles * constants.SAMPLES_PER_CYCLE))

        message = "Frequency Windows:{} Classified as:{}".format(test_windowed_frequencies, incidents)
        self.assertEqual(len(incidents), 1, msg=message)
        self.assertAlmostEqual(incidents[0]["incident_start_ts"], 0, delta=0.1)
        self.assertAlmostEqual(incidents[0]["incident_end_ts"], len(test_windowed_frequencies) *
                               constants.SAMPLES_PER_CYCLE / constants.SAMPLE_RATE_HZ * 1000, delta=0.1)
        self.assertAlmostEqual(incidents[0]["avg_deviation"], numpy.average(test_windowed_frequencies[0:10]) - 60.0,
                               delta=0.1)
        self.assertEqual(incidents[0]["incident_classifications"], [mongo.IncidentClassification.FREQUENCY_SAG])

        # 20 windows of samples, incident from index 0 to 9
        test_windowed_frequencies = [59.0 for _ in range(10)] + [60.0 for _ in range(10)]

        incidents = frequency_incident_classifier(0, "", numpy.array(test_windowed_frequencies), 0, self.freq_ref,
                                                  self.freq_var_high, self.freq_var_low, self.freq_interruption,
                                                  int(self.frequency_window_cycles * constants.SAMPLES_PER_CYCLE))

        message = "Frequency Windows:{} Classified as:{}".format(test_windowed_frequencies, incidents)
        self.assertEqual(len(incidents), 1, msg=message)
        self.assertAlmostEqual(incidents[0]["incident_start_ts"], 0, delta=0.1)
        self.assertAlmostEqual(incidents[0]["incident_end_ts"], 10 * constants.SAMPLES_PER_CYCLE /
                               constants.SAMPLE_RATE_HZ * 1000, delta=0.1)
        self.assertAlmostEqual(incidents[0]["avg_deviation"], numpy.average(test_windowed_frequencies[0:10]) - 60.0,
                               delta=0.1)
        self.assertEqual(incidents[0]["incident_classifications"], [mongo.IncidentClassification.FREQUENCY_SAG])

        # 20 windows of samples, incident from index 10 to 19
        test_windowed_frequencies = [60.0 for _ in range(10)] + [59.0 for _ in range(10)]

        incidents = frequency_incident_classifier(0, "", numpy.array(test_windowed_frequencies), 0, self.freq_ref,
                                                  self.freq_var_high, self.freq_var_low, self.freq_interruption,
                                                  int(self.frequency_window_cycles * constants.SAMPLES_PER_CYCLE))

        message = "Frequency Windows:{} Classified as:{}".format(test_windowed_frequencies, incidents)
        self.assertEqual(len(incidents), 1, msg=message)
        self.assertAlmostEqual(incidents[0]["incident_start_ts"], 10 * constants.SAMPLES_PER_CYCLE /
                               constants.SAMPLE_RATE_HZ * 1000, delta=0.1)
        self.assertAlmostEqual(incidents[0]["incident_end_ts"], len(test_windowed_frequencies) *
                               constants.SAMPLES_PER_CYCLE / constants.SAMPLE_RATE_HZ * 1000, delta=0.1)
        self.assertAlmostEqual(incidents[0]["avg_deviation"], numpy.average(test_windowed_frequencies[10:20]) - 60.0,
                               delta=0.1)
        self.assertEqual(incidents[0]["incident_classifications"], [mongo.IncidentClassification.FREQUENCY_SAG])

        # 30 windows of samples, incident from index 10 to 19
        test_windowed_frequencies = [60.0 for _ in range(10)] + [59.0 for _ in range(10)] + [60.0 for _ in range(10)]

        incidents = frequency_incident_classifier(0, "", numpy.array(test_windowed_frequencies), 0, self.freq_ref,
                                                  self.freq_var_high, self.freq_var_low, self.freq_interruption,
                                                  int(self.frequency_window_cycles * constants.SAMPLES_PER_CYCLE))

        message = "Frequency Windows:{} Classified as:{}".format(test_windowed_frequencies, incidents)
        self.assertEqual(len(incidents), 1, msg=message)
        self.assertAlmostEqual(incidents[0]["incident_start_ts"], 10 * constants.SAMPLES_PER_CYCLE /
                               constants.SAMPLE_RATE_HZ * 1000, delta=0.01)
        self.assertAlmostEqual(incidents[0]["incident_end_ts"], 20 * constants.SAMPLES_PER_CYCLE /
                               constants.SAMPLE_RATE_HZ * 1000, delta=0.01)
        self.assertAlmostEqual(incidents[0]["avg_deviation"], numpy.average(test_windowed_frequencies[10:20]) - 60.0,
                               delta=0.01)
        self.assertEqual(incidents[0]["incident_classifications"], [mongo.IncidentClassification.FREQUENCY_SAG])

        # 25 windows of samples, incidents from index 5 to 9 and 15 to 19
        test_windowed_frequencies = [60.0 for _ in range(5)] + [59.0 for _ in range(5)] + [60.0 for _ in range(5)] + \
                                    [59.0 for _ in range(5)] + [60.0 for _ in range(5)]

        incidents = frequency_incident_classifier(0, "", numpy.array(test_windowed_frequencies), 0, self.freq_ref,
                                                  self.freq_var_high, self.freq_var_low, self.freq_interruption,
                                                  int(self.frequency_window_cycles * constants.SAMPLES_PER_CYCLE))

        message = "Frequency Windows:{} Classified as:{}".format(test_windowed_frequencies, incidents)
        self.assertEqual(len(incidents), 2, msg=message)
        self.assertAlmostEqual(incidents[0]["incident_start_ts"], 5 * constants.SAMPLES_PER_CYCLE /
                               constants.SAMPLE_RATE_HZ * 1000, delta=0.01)
        self.assertAlmostEqual(incidents[0]["incident_end_ts"], 10 * constants.SAMPLES_PER_CYCLE /
                               constants.SAMPLE_RATE_HZ * 1000, delta=0.01)
        self.assertAlmostEqual(incidents[0]["avg_deviation"], numpy.average(test_windowed_frequencies[5:10]) - 60.0,
                               delta=0.01)
        self.assertEqual(incidents[0]["incident_classifications"], [mongo.IncidentClassification.FREQUENCY_SAG])

        self.assertEqual(len(incidents), 2, msg=message)
        self.assertAlmostEqual(incidents[1]["incident_start_ts"], 15 * constants.SAMPLES_PER_CYCLE /
                               constants.SAMPLE_RATE_HZ * 1000, delta=0.01)
        self.assertAlmostEqual(incidents[1]["incident_end_ts"], 20 * constants.SAMPLES_PER_CYCLE /
                               constants.SAMPLE_RATE_HZ * 1000, delta=0.01)
        self.assertAlmostEqual(incidents[1]["avg_deviation"], numpy.average(test_windowed_frequencies[15:20]) - 60.0,
                               delta=0.01)
        self.assertEqual(incidents[1]["incident_classifications"], [mongo.IncidentClassification.FREQUENCY_SAG])

    def test_interruption(self):
        """
        Test frequencies less than or equal to 58Hz, we expect to classify these frequencies as interruptions
        """

        """frequency_variation Method"""
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

        """frequency_incident_classifier Method"""
        test_windowed_frequencies = [50.0 for _ in range(1)]  # 1 window of samples
        incidents = frequency_incident_classifier(0, "", numpy.array(test_windowed_frequencies), 0, self.freq_ref,
                                                  self.freq_var_high, self.freq_var_low, self.freq_interruption,
                                                  int(self.frequency_window_cycles * constants.SAMPLES_PER_CYCLE))
        message = "Frequency Window:{} Classified as:{}".format(test_windowed_frequencies, incidents)
        self.assertEqual(len(incidents), 1, msg=message)

        # 10 windows of samples
        test_windowed_frequencies = [50.0 for _ in range(10)]

        incidents = frequency_incident_classifier(0, "", numpy.array(test_windowed_frequencies), 0, self.freq_ref,
                                                  self.freq_var_high, self.freq_var_low, self.freq_interruption,
                                                  int(self.frequency_window_cycles * constants.SAMPLES_PER_CYCLE))

        message = "Frequency Windows:{} Classified as:{}".format(test_windowed_frequencies, incidents)
        self.assertEqual(len(incidents), 1, msg=message)
        self.assertAlmostEqual(incidents[0]["incident_start_ts"], 0, delta=0.1)
        self.assertAlmostEqual(incidents[0]["incident_end_ts"], len(test_windowed_frequencies) *
                               constants.SAMPLES_PER_CYCLE / constants.SAMPLE_RATE_HZ * 1000, delta=0.1)
        self.assertAlmostEqual(incidents[0]["avg_deviation"], numpy.average(test_windowed_frequencies[0:10]) - 60.0,
                               delta=0.1)
        self.assertEqual(incidents[0]["incident_classifications"],
                         [mongo.IncidentClassification.FREQUENCY_INTERRUPTION])

        # 20 windows of samples, incident from index 0 to 9
        test_windowed_frequencies = [50.0 for _ in range(10)] + [60.0 for _ in range(10)]

        incidents = frequency_incident_classifier(0, "", numpy.array(test_windowed_frequencies), 0, self.freq_ref,
                                                  self.freq_var_high, self.freq_var_low, self.freq_interruption,
                                                  int(self.frequency_window_cycles * constants.SAMPLES_PER_CYCLE))

        message = "Frequency Windows:{} Classified as:{}".format(test_windowed_frequencies, incidents)
        self.assertEqual(len(incidents), 1, msg=message)
        self.assertAlmostEqual(incidents[0]["incident_start_ts"], 0, delta=0.1)
        self.assertAlmostEqual(incidents[0]["incident_end_ts"], 10 * constants.SAMPLES_PER_CYCLE /
                               constants.SAMPLE_RATE_HZ * 1000, delta=0.1)
        self.assertAlmostEqual(incidents[0]["avg_deviation"], numpy.average(test_windowed_frequencies[0:10]) - 60.0,
                               delta=0.1)
        self.assertEqual(incidents[0]["incident_classifications"],
                         [mongo.IncidentClassification.FREQUENCY_INTERRUPTION])

        # 20 windows of samples, incident from index 10 to 19
        test_windowed_frequencies = [60.0 for _ in range(10)] + [50.0 for _ in range(10)]

        incidents = frequency_incident_classifier(0, "", numpy.array(test_windowed_frequencies), 0, self.freq_ref,
                                                  self.freq_var_high, self.freq_var_low, self.freq_interruption,
                                                  int(self.frequency_window_cycles * constants.SAMPLES_PER_CYCLE))

        message = "Frequency Windows:{} Classified as:{}".format(test_windowed_frequencies, incidents)
        self.assertEqual(len(incidents), 1, msg=message)
        self.assertAlmostEqual(incidents[0]["incident_start_ts"], 10 * constants.SAMPLES_PER_CYCLE /
                               constants.SAMPLE_RATE_HZ * 1000, delta=0.1)
        self.assertAlmostEqual(incidents[0]["incident_end_ts"], len(test_windowed_frequencies) *
                               constants.SAMPLES_PER_CYCLE / constants.SAMPLE_RATE_HZ * 1000, delta=0.1)
        self.assertAlmostEqual(incidents[0]["avg_deviation"], numpy.average(test_windowed_frequencies[10:20]) - 60.0,
                               delta=0.1)
        self.assertEqual(incidents[0]["incident_classifications"],
                         [mongo.IncidentClassification.FREQUENCY_INTERRUPTION])

        # 30 windows of samples, incident from index 10 to 19
        test_windowed_frequencies = [60.0 for _ in range(10)] + [50.0 for _ in range(10)] + [60.0 for _ in range(10)]

        incidents = frequency_incident_classifier(0, "", numpy.array(test_windowed_frequencies), 0, self.freq_ref,
                                                  self.freq_var_high, self.freq_var_low, self.freq_interruption,
                                                  int(self.frequency_window_cycles * constants.SAMPLES_PER_CYCLE))

        message = "Frequency Windows:{} Classified as:{}".format(test_windowed_frequencies, incidents)
        self.assertEqual(len(incidents), 1, msg=message)
        self.assertAlmostEqual(incidents[0]["incident_start_ts"], 10 * constants.SAMPLES_PER_CYCLE /
                               constants.SAMPLE_RATE_HZ * 1000, delta=0.01)
        self.assertAlmostEqual(incidents[0]["incident_end_ts"], 20 * constants.SAMPLES_PER_CYCLE /
                               constants.SAMPLE_RATE_HZ * 1000, delta=0.01)
        self.assertAlmostEqual(incidents[0]["avg_deviation"], numpy.average(test_windowed_frequencies[10:20]) - 60.0,
                               delta=0.01)
        self.assertEqual(incidents[0]["incident_classifications"],
                         [mongo.IncidentClassification.FREQUENCY_INTERRUPTION])

        # 25 windows of samples, incidents from index 5 to 9 and 15 to 19
        test_windowed_frequencies = [60.0 for _ in range(5)] + [50.0 for _ in range(5)] + [60.0 for _ in range(5)] + \
                                    [50.0 for _ in range(5)] + [60.0 for _ in range(5)]

        incidents = frequency_incident_classifier(0, "", numpy.array(test_windowed_frequencies), 0, self.freq_ref,
                                                  self.freq_var_high, self.freq_var_low, self.freq_interruption,
                                                  int(self.frequency_window_cycles * constants.SAMPLES_PER_CYCLE))

        message = "Frequency Windows:{} Classified as:{}".format(test_windowed_frequencies, incidents)
        self.assertEqual(len(incidents), 2, msg=message)
        self.assertAlmostEqual(incidents[0]["incident_start_ts"], 5 * constants.SAMPLES_PER_CYCLE /
                               constants.SAMPLE_RATE_HZ * 1000, delta=0.01)
        self.assertAlmostEqual(incidents[0]["incident_end_ts"], 10 * constants.SAMPLES_PER_CYCLE /
                               constants.SAMPLE_RATE_HZ * 1000, delta=0.01)
        self.assertAlmostEqual(incidents[0]["avg_deviation"], numpy.average(test_windowed_frequencies[5:10]) - 60.0,
                               delta=0.01)
        self.assertEqual(incidents[0]["incident_classifications"],
                         [mongo.IncidentClassification.FREQUENCY_INTERRUPTION])

        self.assertEqual(len(incidents), 2, msg=message)
        self.assertAlmostEqual(incidents[1]["incident_start_ts"], 15 * constants.SAMPLES_PER_CYCLE /
                               constants.SAMPLE_RATE_HZ * 1000, delta=0.01)
        self.assertAlmostEqual(incidents[1]["incident_end_ts"], 20 * constants.SAMPLES_PER_CYCLE /
                               constants.SAMPLE_RATE_HZ * 1000, delta=0.01)
        self.assertAlmostEqual(incidents[1]["avg_deviation"], numpy.average(test_windowed_frequencies[15:20]) - 60.0,
                               delta=0.01)
        self.assertEqual(incidents[1]["incident_classifications"],
                         [mongo.IncidentClassification.FREQUENCY_INTERRUPTION])
