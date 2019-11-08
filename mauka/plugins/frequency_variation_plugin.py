"""
This plugin detects, classifies, and stores frequency variation incidents.
Frequency variations are classified as +/-0.10hz as specified by IEEE standards
"""
import multiprocessing
import typing

import mauka_native_py as native

import config
import log
import plugins.base_plugin
from plugins.routes import Routes
import protobuf.mauka_pb2 as mauka_pb2
import protobuf.pb_util
import mongo


def find_frequency_variation_incidents(mauka_message: mauka_pb2.MaukaMessage,
                                       frequency_threshold_low: float,
                                       frequency_threshold_high: float,
                                       min_incident_len_c: float,
                                       opq_mongo_client: mongo.OpqMongoClient,
                                       plugin: typing.Optional['FrequencyVariationPlugin'] = None) -> typing.List[int]:
    frequencies_per_cycle: typing.List[float] = list(mauka_message.payload.data)
    log.maybe_debug("Found %d frequencies" % len(frequencies_per_cycle), plugin)
    bounds = [[0.0, frequency_threshold_low],
              [frequency_threshold_high, 1_000_000]]
    log.maybe_debug("Using bounds=%s" % str(bounds), plugin)
    ranges = native.bounded_ranges(mauka_message.payload.start_timestamp_ms,
                                   frequencies_per_cycle,
                                   bounds)
    log.maybe_debug("Found %d ranges" % (len(ranges)), plugin)

    incident_ids: typing.List[int] = []
    for incident_range in ranges:
        if incident_range.end_idx - incident_range.start_idx < min_incident_len_c:
            log.maybe_debug("Ignoring incident with len_c = %f" % incident_range.end_idx - incident_range.start_idx,
                            plugin)
            continue

        max_deviation = 60.0 - max(min(frequencies_per_cycle[incident_range.start_idx:incident_range.end_idx]),
                                   max(frequencies_per_cycle[incident_range.start_idx:incident_range.end_idx]))
        log.maybe_debug("max_deviation=%f" % max_deviation, plugin)
        if incident_range.bound_min == bounds[0][0] and incident_range.bound_max == bounds[0][1]:
            log.maybe_debug("frequency_sag", plugin)
            incident_id = mongo.store_incident(
                mauka_message.payload.event_id,
                mauka_message.payload.box_id,
                incident_range.start_ts_ms,
                incident_range.end_ts_ms,
                mongo.IncidentMeasurementType.FREQUENCY,
                max_deviation,
                [mongo.IncidentClassification.FREQUENCY_SAG],
                [],
                {},
                opq_mongo_client
            )
            incident_ids.append(incident_id)
            log.maybe_debug("Stored incident with id=%s" % incident_id, plugin)
        elif incident_range.bound_min == bounds[1][0] and incident_range.bound_max == bounds[1][1]:
            # Frequency swell
            log.maybe_debug("frequency_swell", plugin)
            incident_id = mongo.store_incident(
                mauka_message.payload.event_id,
                mauka_message.payload.box_id,
                incident_range.start_ts_ms,
                incident_range.end_ts_ms,
                mongo.IncidentMeasurementType.FREQUENCY,
                max_deviation,
                [mongo.IncidentClassification.FREQUENCY_SWELL],
                [],
                {},
                opq_mongo_client
            )
            incident_ids.append(incident_id)
            log.maybe_debug("Stored incident with id=%s" % incident_id, plugin)
        else:
            # Unknown
            log.maybe_debug("Unknown range bounds = %d, %d" % (incident_range.bound_min, incident_range.bound_max),
                            plugin)

    return incident_ids


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
        super().__init__(conf, [Routes.windowed_frequency], FrequencyVariationPlugin.NAME, exit_event)
        self.freq_var_low = float(self.config.get("plugins.FrequencyVariationPlugin.frequency.variation.threshold.low"))
        self.freq_var_high = float(self.config.get(
            "plugins.FrequencyVariationPlugin.frequency.variation.threshold.high"))
        self.min_incident_len_c = float(self.config.get("plugins.FrequencyVariationPlugin.min_incident_len_c"))

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

            incident_ids = find_frequency_variation_incidents(mauka_message,
                                                              self.freq_var_low,
                                                              self.freq_var_high,
                                                              self.min_incident_len_c,
                                                              self.mongo_client,
                                                              self)

            self.debug("Preparing to update GC for %d incident_ids" % incident_ids)
            for incident_id in incident_ids:
                # Produce a message to the GC
                self.produce(Routes.laha_gc, protobuf.pb_util.build_gc_update(self.name,
                                                                              protobuf.mauka_pb2.INCIDENTS,
                                                                              incident_id))
                self.debug("Updated GC for incident %d" % incident_id)

            self.debug("Done analyzing data from event %d" % mauka_message.payload.event_id)
        else:
            self.logger.error("Received incorrect mauka message [%s] at FrequencyVariationPlugin",
                              protobuf.pb_util.which_message_oneof(mauka_message))
