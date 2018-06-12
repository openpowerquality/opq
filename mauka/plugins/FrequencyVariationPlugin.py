"""
This plugin detects, classifies, and stores frequency variation incidents.
Frequency variations are classified as +/-0.10hz as specified by IEEE standards
"""
import typing
import multiprocessing
import numpy
import constants
import plugins.base
import protobuf.mauka_pb2
import protobuf.util
import mongo

class FrequencyVariationPlugin(plugins.base.MaukaPlugin):
    """
    Mauka plugin that classifies and stores frequency variation incidents for any event that includes a raw waveform
    """
    NAME = "FrequencyVariationPlugin"

    def __init__(self, config: typing.Dict, exit_event: multiprocessing.Event):
        """
        Initializes this plugin
        :param config: Mauka configuration
        :param exit_event: Exit event that can disable this plugin from parent process
        """
        super().__init__(config, ["WindowedFrequency"], FrequencyVariationPlugin.NAME, exit_event)
        self.freq_ref = float(self.config_get("plugins.FrequencyVariationPlugin.frequency.ref"))
        self.freq_var_low = float(self.config_get("plugins.FrequencyVariationPlugin.frequency.variation.threshold.low"))
        self.freq_var_high = float(self.config_get("plugins.FrequencyVariationPlugin.frequency.variation.threshold.high"))
        self.freq_interruption = float(self.config_get("plugins.FrequencyVariationPlugin.frequency.interruption"))

    def __frequency_variation_type(self, frequency: float):
        """
        Determine the variation type if any based on IEEE 1159 standards
        :param frequency: the frequency measured over the window
        :return: variation_type: the variation type if there is a variation from the reference, otherwise False
        """
        variation_type = False

        if frequency >= (self.freq_ref + self.freq_var_high):
            variation_type = mongo.BoxEventType.FREQUENCY_SWELL
        elif frequency <= self.freq_interruption:
            variation_type = mongo.BoxEventType.FREQUENCY_INTERRUPTION
        elif frequency <= (self.freq_ref - self.freq_var_low):
            variation_type = mongo.BoxEventType.FREQUENCY_DIP

        return variation_type

    def __frequency_incident_classifier(self, event_id: int, box_id: str, windowed_frequencies: numpy.ndarray,
                                       window_size: float = constants.SAMPLES_PER_CYCLE):
        """
        Classifies a frequency incident as a Sag, Swell, or Interruption. Creates a Mongo Anomaly document
        :param event_id: Makai Event ID
        :param box_id: Box reporting event
        :param windowed_frequencies: High fidelity frequency measurements of windows
        :param window_size: The number of samples per window
        """

        window_duration_ms = (window_size / constants.SAMPLE_RATE_HZ) * 1000
        prev_anomaly = False
        anomaly_start = 0

        for i in range(len(windowed_frequencies)):
            # check whether there is a frequency variation and if so what type
            curr_anomaly = self.__frequency_variation_type(windowed_frequencies[i])
            if prev_anomaly != curr_anomaly:  # start of new anomaly and or end of anomaly
                if prev_anomaly:  # make anomaly doc
                    duration  = (i - anomaly_start) * window_size * window_duration_ms
                    anomaly = mongo.make_anomaly_document(event_id,  # Event id
                                                          box_id,  # box id
                                                          prev_anomaly.value,  # Event name
                                                          "unknown",  # Location
                                                          0,  # Start ts ms
                                                          0,  # End ts ms
                                                          duration,  # Duration ms
                                                          anomaly_start,  # Start idx
                                                          i,  # End idx
                                                          {"min": numpy.min(windowed_frequencies[anomaly_start:i]),
                                                           "max": numpy.max(windowed_frequencies[anomaly_start:i]),
                                                           "avg": numpy.average(windowed_frequencies[anomaly_start:i])})
                    # self.mongo_client.anomalies_collection.insert_one(anomaly)
                    self.debug(str(anomaly))

                anomaly_start = i

            prev_anomaly = curr_anomaly

    def on_message(self, topic, mauka_message):
        """
        Called async when a topic this plugin subscribes to produces a message
        :param topic: The topic that is producing the message
        :param mauka_message: The message that was produced
        """
        self.debug("on_message")
        if protobuf.util.is_payload(mauka_message, protobuf.mauka_pb2.FREQUENCY_WINDOWED):
            self.debug("on_message {}:{} len:{}".format(mauka_message.payload.event_id,
                                                        mauka_message.payload.box_id,
                                                        len(mauka_message.payload.data)))
            self.__frequency_incident_classifier(mauka_message.payload.event_id,
                                                mauka_message.payload.box_id,
                                                protobuf.util.repeated_as_ndarray(
                                                mauka_message.payload.data
                                                ))

        else:
            self.logger.error("Received incorrect mauka message [{}] at FrequencyVariationPlugin".format(
                protobuf.util.which_message_oneof(mauka_message)
            ))
