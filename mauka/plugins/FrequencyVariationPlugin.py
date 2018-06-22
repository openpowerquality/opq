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

    def __frequency_variation(self, frequency: float):
        """
        Determine the variation type if any based on IEEE 1159 standards
        :param frequency: the frequency measured over the window
        :return: variation_type: the variation type if there is a variation from the reference, otherwise False
        """

        if frequency >= (self.freq_ref + self.freq_var_high):
            variation_type = mongo.IncidentClassification.FREQUENCY_SWELL
        elif frequency <= self.freq_interruption:
            variation_type = mongo.IncidentClassification.FREQUENCY_INTERRUPTION
        elif frequency <= (self.freq_ref - self.freq_var_low):
            variation_type = mongo.IncidentClassification.FREQUENCY_DIP
        else:
            variation_type = False

        return variation_type, frequency - self.freq_ref

    def __frequency_incident_classifier(self, event_id: int, box_id: str, windowed_frequencies: numpy.ndarray,
                                        box_event_start_ts: int, window_size: float = constants.SAMPLES_PER_CYCLE,
                                        opq_mongo_client: mongo.OpqMongoClient = None):
        """
        Classifies a frequency incident as a Sag, Swell, or Interruption. Creates a Mongo Anomaly document
        :param event_id: Makai Event ID
        :param box_id: Box reporting event
        :param windowed_frequencies: High fidelity frequency measurements of windows
        :param window_size: The number of samples per window
        """

        mongo_client = mongo.get_default_client(opq_mongo_client)
        window_duration_ms = (window_size / constants.SAMPLE_RATE_HZ) * 1000
        prev_incident = False
        incident_start_ts = box_event_start_ts
        incident_variations = []

        for i in range(len(windowed_frequencies)):
            # check whether there is a frequency variation and if so what type
            curr_incident, curr_variation = self.__frequency_variation(windowed_frequencies[i])

            if prev_incident != curr_incident:  # start of new incident and or end of incident
                if prev_incident:  # make and store incident doc if end of incident
                    incident_end_ts = i * window_duration_ms + box_event_start_ts
                    mongo.store_incident(
                        event_id,  # Event id
                        box_id,  # box id
                        incident_start_ts,  # Start ts ms
                        incident_end_ts,  # End ts ms
                        mongo.IncidentMeasurementType.FREQUENCY,
                        numpy.average(incident_variations),  # incident's average deviation from nominal
                        [prev_incident],  # incident classifications
                        [], # annotations
                        {}, # metadata
                        mongo_client, # mongo client
                    )
                    # print("Storing Incident")
                    # print(incident_start_ts)
                    # print(incident_end_ts)
                    # print(mongo.IncidentMeasurementType.FREQUENCY)
                    # print(numpy.average(incident_variations))
                    # print([prev_incident])

                incident_variations = [curr_variation]
                incident_start_ts = i * window_duration_ms + box_event_start_ts

            else:
                incident_variations.append(curr_variation)

            prev_incident = curr_incident

        # ensure if there is any frequency variation at the end of the event then it is still saved
        if prev_incident:  # make and store incident doc
            incident_end_ts = len(windowed_frequencies) * window_duration_ms + box_event_start_ts
            mongo.store_incident(
                event_id,  # Event id
                box_id,  # box id
                incident_start_ts,  # Start ts ms
                incident_end_ts,  # End ts ms
                mongo.IncidentMeasurementType.FREQUENCY,
                numpy.average(incident_variations),  # incident's average deviation from nominal
                [prev_incident],  # incident classifications
                [],  # annotations
                {},  # metadata
                mongo_client,  # mongo client
            )
            # print("Storing Incident")
            # print(incident_start_ts)
            # print(incident_end_ts)
            # print(mongo.IncidentMeasurementType.FREQUENCY)
            # print(numpy.average(incident_variations))
            # print([prev_incident])


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
                                                 ),
                                                 mauka_message.payload.start_timestamp_ms)

        else:
            self.logger.error("Received incorrect mauka message [{}] at FrequencyVariationPlugin".format(
                protobuf.util.which_message_oneof(mauka_message)
            ))
