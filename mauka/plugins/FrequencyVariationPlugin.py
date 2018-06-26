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


def frequency_variation(frequency: float, freq_ref: float, freq_var_high: float,
                        freq_var_low: float, freq_interruption: float):
    """
    Determine the variation type if any based on IEEE 1159 standards
    :param frequency: the frequency measured over the window
    :param freq_ref: the reference frequency
    :param freq_var_high:
    :param freq_var_low:
    :param freq_interruption:
    :return: variation_type: the variation type if there is a variation from the reference, otherwise False
    """

    if frequency >= (freq_ref + freq_var_high):
        variation_type = mongo.IncidentClassification.FREQUENCY_SWELL
    elif frequency <= freq_interruption:
        variation_type = mongo.IncidentClassification.FREQUENCY_INTERRUPTION
    elif frequency <= (freq_ref - freq_var_low):
        variation_type = mongo.IncidentClassification.FREQUENCY_SAG
    else:
        variation_type = False

    return variation_type, frequency - freq_ref



def frequency_incident_classifier(event_id: int, box_id: str, windowed_frequencies: numpy.ndarray,
                                    box_event_start_ts: int, freq_ref: float, freq_var_high: float, freq_var_low: float,
                                    freq_interruption: float, window_size: float = constants.SAMPLES_PER_CYCLE,
                                    opq_mongo_client: mongo.OpqMongoClient = None, logger = None):
    """
    Classifies a frequency incident as a Sag, Swell, or Interruption. Creates a Mongo Incident document
    :param event_id: Makai Event ID
    :param box_id: Box reporting event
    :param windowed_frequencies: High fidelity frequency measurements of windows
    :param freq_ref: the reference frequency
    :param freq_var_high:
    :param freq_var_low:
    :param freq_interruption:
    :param window_size: The number of samples per window
    :param opq_mongo_client:
    :param logger:
    """

    mongo_client = mongo.get_default_client(opq_mongo_client)
    window_duration_ms = (window_size / constants.SAMPLE_RATE_HZ) * 1000
    prev_incident = False
    incident_start_ts = box_event_start_ts
    incident_variations = []

    if logger is not None:
        logger.debug("Calculating frequency with {} segments.".format(len(windowed_frequencies)))

    for i in range(len(windowed_frequencies)):
        # check whether there is a frequency variation and if so what type
        curr_incident, curr_variation = frequency_variation(windowed_frequencies[i], freq_ref, freq_var_high,
                                                                freq_var_low, freq_interruption)
        if prev_incident != curr_incident:  # start of new incident and or end of incident
            if prev_incident:  # make and store incident doc if end of incident
                incident_end_ts = i * window_duration_ms + box_event_start_ts
                if logger is not None:
                    logger.debug("Found Frequency incident [{}] from event {} and box {}".format(
                        prev_incident,
                        event_id,
                        box_id
                    ))
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

            incident_variations = [curr_variation]
            incident_start_ts = i * window_duration_ms + box_event_start_ts

        else:
            incident_variations.append(curr_variation)

        prev_incident = curr_incident

    # ensure if there is any frequency variation at the end of the event then it is still saved
    if prev_incident:  # make and store incident doc
        incident_end_ts = len(windowed_frequencies) * window_duration_ms + box_event_start_ts
        if logger is not None:
            logger.debug("Found Frequency incident [{}] from event {} and box {}".format(
                prev_incident,
                event_id,
                box_id
            ))
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
            frequency_incident_classifier(mauka_message.payload.event_id,
                                                 mauka_message.payload.box_id,
                                                 protobuf.util.repeated_as_ndarray(
                                                    mauka_message.payload.data
                                                 ),
                                                 mauka_message.payload.start_timestamp_ms,
                                                 self.freq_ref, self.freq_var_high, self.freq_var_low,
                                                 self.freq_interruption, logger=self.logger)

        else:
            self.logger.error("Received incorrect mauka message [{}] at FrequencyVariationPlugin".format(
                protobuf.util.which_message_oneof(mauka_message)
            ))
