"""
This plugin detects, classifies, and stores frequency variation incidents.
Frequency variations are classified as +/-0.10hz as specified by IEEE standards
"""
import multiprocessing
import typing

import numpy

import config
import constants
import plugins.base_plugin
import protobuf.mauka_pb2
import protobuf.pb_util
import mongo


def maybe_debug(frequency_variation_plugin: typing.Optional['FrequencyVariationPlugin'],
                msg: str):
    if frequency_variation_plugin is not None:
        frequency_variation_plugin.debug(msg)


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


def frequency_incident_classifier(event_id: int,
                                  box_id: str,
                                  windowed_frequencies: numpy.ndarray,
                                  box_event_start_ts: int,
                                  freq_ref: float,
                                  freq_var_high: float,
                                  freq_var_low: float,
                                  freq_interruption: float,
                                  window_size: int,
                                  max_lull: int,
                                  opq_mongo_client: typing.Optional[mongo.OpqMongoClient] = None,
                                  frequency_variation_plugin: typing.Optional['FrequencyVariationPlugin'] = None):
    """
    Classifies a frequency incident as a Sag, Swell, or Interruption. Creates a Mongo Incident document
    :param event_id: Makai Event ID
    :param box_id: Box reporting event
    :param windowed_frequencies: High fidelity frequency measurements of windows
    :param box_event_start_ts: start timestamp of event in milliseconds
    :param freq_ref: the reference frequency
    :param freq_var_high: the threshold amount of variation to trigger a frequency swell incident
    :param freq_var_low: the threshold amount of variation to trigger a frequency sag incident
    :param freq_interruption: the frequency to trigger a frequency interruption incident
    :param window_size: The number of samples per window
    :param max_lull:
    :param opq_mongo_client:
    :param frequency_variation_plugin:
    """

    mongo_client = mongo.get_default_client(opq_mongo_client)
    window_duration_ms = (window_size / constants.SAMPLE_RATE_HZ) * 1000
    running_incident = False
    incident_start_ts = box_event_start_ts
    incident_variations = []
    incidents = []
    lull_variations = []
    lull_incidents = []
    lull_count = 0

    maybe_debug(frequency_variation_plugin, "Calculating frequency with {} segments.".format(len(windowed_frequencies)))
    maybe_debug(frequency_variation_plugin, "window_duration_ms: {}".format(window_duration_ms))

    for idx, freq in enumerate(windowed_frequencies):
        # check whether there is a frequency variation and if so what type
        curr_incident, curr_variation = frequency_variation(freq, freq_ref, freq_var_high,
                                                            freq_var_low, freq_interruption)
        if running_incident != curr_incident:
            if lull_count == max_lull or running_incident is False:  # start of new incident and or end of incident
                if running_incident:  # make and store incident doc if end of incident
                    incident_end_ts = (idx - max_lull) * window_duration_ms + box_event_start_ts

                    maybe_debug(
                        frequency_variation_plugin,
                        "Found Frequency incident [{}] from event {} and box {}".format(
                            running_incident,
                            event_id,
                            box_id
                        ))
                    incidents.append({"event_id": event_id, "box_id": box_id, "incident_start_ts": incident_start_ts,
                                      "incident_end_ts": incident_end_ts,
                                      "incident_type": mongo.IncidentMeasurementType.FREQUENCY,
                                      "avg_deviation": numpy.average(incident_variations),
                                      "incident_classifications": [running_incident], "annotations": [], "metadata": {},
                                      "mongo_client": mongo_client})

                incident_variations = [curr_variation]
                incident_start_ts = idx * window_duration_ms + box_event_start_ts
                running_incident = curr_incident
                lull_count = 0
                lull_incidents = []
                lull_variations = []
            else:
                lull_incidents.append(curr_incident)
                lull_variations.append(curr_variation)
                lull_count += 1
        else:
            incident_variations = incident_variations + lull_variations
            incident_variations.append(curr_variation)
            lull_count = 0
            lull_incidents = []
            lull_variations = []

    # ensure if there is any frequency variation at the end of the event then it is still saved
    if running_incident:  # make and store incident doc
        incident_end_ts = len(windowed_frequencies - lull_count) * window_duration_ms + box_event_start_ts
        maybe_debug(
            frequency_variation_plugin,
            "Found Frequency incident [{}] from event {} and box {}".format(
                running_incident,
                event_id,
                box_id
            ))
        incidents.append({"event_id": event_id, "box_id": box_id, "incident_start_ts": incident_start_ts,
                          "incident_end_ts": incident_end_ts,
                          "incident_type": mongo.IncidentMeasurementType.FREQUENCY,
                          "avg_deviation": numpy.average(incident_variations),
                          "incident_classifications": [running_incident], "annotations": [], "metadata": {},
                          "mongo_client": mongo_client})
    return incidents


class FrequencyVariationPlugin(plugins.base_plugin.MaukaPlugin):
    """
    Mauka plugin that classifies and stores frequency variation incidents for any event that includes a raw waveform
    """
    NAME = "FrequencyVariationPlugin"

    def __init__(self, conf: config.MaukaConfig, exit_event: multiprocessing.Event):
        """
        Initializes this plugin
        :param conf: Mauka configuration
        :param exit_event: Exit event that can disable this plugin from parent process
        """
        super().__init__(conf, ["WindowedFrequency"], FrequencyVariationPlugin.NAME, exit_event)
        self.freq_ref = float(self.config.get("plugins.FrequencyVariationPlugin.frequency.ref"))
        self.freq_var_low = float(self.config.get("plugins.FrequencyVariationPlugin.frequency.variation.threshold.low"))
        self.freq_var_high = float(self.config.get(
            "plugins.FrequencyVariationPlugin.frequency.variation.threshold.high"))
        self.freq_interruption = float(self.config.get("plugins.FrequencyVariationPlugin.frequency.interruption"))
        self.frequency_window_cycles = int(self.config.get("plugins.MakaiEventPlugin.frequencyWindowCycles"))
        self.max_lull = int(self.config.get("plugins.FrequencyVariationPlugin.max.lull.windows"))

    def on_message(self, topic, mauka_message):
        """
        Called async when a topic this plugin subscribes to produces a message
        :param topic: The topic that is producing the message
        :param mauka_message: The message that was produced
        """
        self.debug("{} on_message".format(topic))
        if protobuf.pb_util.is_payload(mauka_message, protobuf.mauka_pb2.FREQUENCY_WINDOWED):
            self.debug("on_message {}:{} len:{}".format(mauka_message.payload.event_id,
                                                        mauka_message.payload.box_id,
                                                        len(mauka_message.payload.data)))

            incidents = frequency_incident_classifier(mauka_message.payload.event_id,
                                                      mauka_message.payload.box_id,
                                                      protobuf.pb_util.repeated_as_ndarray(mauka_message.payload.data),
                                                      mauka_message.payload.start_timestamp_ms,
                                                      self.freq_ref,
                                                      self.freq_var_high,
                                                      self.freq_var_low,
                                                      self.freq_interruption,
                                                      self.frequency_window_cycles * constants.SAMPLES_PER_CYCLE,
                                                      self.max_lull,
                                                      self.mongo_client,
                                                      self)

            for incident in incidents:
                incident_id = mongo.store_incident(
                    incident["event_id"],
                    incident["box_id"],
                    incident["incident_start_ts"],
                    incident["incident_end_ts"],
                    incident["incident_type"],
                    incident["avg_deviation"],
                    incident["incident_classifications"],
                    incident["annotations"],
                    incident["metadata"],
                    self.mongo_client
                )

                # Produce a message to the GC
                self.produce("laha_gc", protobuf.pb_util.build_gc_update(self.name,
                                                                         protobuf.mauka_pb2.INCIDENTS,
                                                                         incident_id))
        else:
            self.logger.error("Received incorrect mauka message [%s] at FrequencyVariationPlugin",
                              protobuf.pb_util.which_message_oneof(mauka_message))


def rerun(mongo_client: mongo.OpqMongoClient, logger, mauka_message: protobuf.mauka_pb2.MaukaMessage):
    """
    Rerun a makai event through the frequency variation plugin.
    :param mongo_client: Mongo client to make the query.
    :param logger: Application logger.
    :param mauka_message: The mauka message to rerrun the frequency variation plugin over.
    """
    if protobuf.pb_util.is_payload(mauka_message, protobuf.mauka_pb2.FREQUENCY_WINDOWED):
        client = mongo.get_default_client(mongo_client)
        incidents = frequency_incident_classifier(mauka_message.payload.event_id, mauka_message.payload.box_id,
                                                  protobuf.pb_util.repeated_as_ndarray(mauka_message.payload.data),
                                                  mauka_message.payload.start_timestamp_ms,
                                                  60.0, 0.1, 0.1,
                                                  58.0,
                                                  1 * constants.SAMPLES_PER_CYCLE,
                                                  3,
                                                  None)

        for incident in incidents:
            mongo.store_incident(
                incident["event_id"],
                incident["box_id"],
                incident["incident_start_ts"],
                incident["incident_end_ts"],
                incident["incident_type"],
                incident["avg_deviation"],
                incident["incident_classifications"],
                incident["annotations"],
                incident["metadata"],
                client
            )
    else:
        logger.error("Received incorrect mauka message [%s] at FrequencyVariationPlugin",
                     protobuf.pb_util.which_message_oneof(mauka_message))
