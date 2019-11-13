# pylint: disable=I1101, E1101
"""
This plugin calculates total harmonic distortion (THD) over waveforms.
"""
import multiprocessing
import typing

import mauka_native_py

import config
import mongo
import log
import plugins.base_plugin
from plugins.routes import Routes
import protobuf.mauka_pb2
import protobuf.pb_util


def thd(mauka_message: protobuf.mauka_pb2.MaukaMessage,
        thd_threshold_percent: float,
        opq_mongo_client: mongo.OpqMongoClient,
        thd_plugin: typing.Optional['ThdPlugin'] = None) -> typing.List[int]:
    """
    Calculates THD per cycle over a range of data.
    :param mauka_message: The Mauka message.
    :param thd_threshold_percent: The THD threshold percent.
    :param opq_mongo_client: An instance of an OPQ mongo client.
    :param thd_plugin: An instance of the THD plugin.
    :return: A list of incident ids (if any)
    """
    try:
        data: typing.List[float] = list(mauka_message.payload.data)
        log.maybe_debug("Found %d samples." % len(data), thd_plugin)
        incidents = mauka_native_py.classify_thd(mauka_message.payload.start_timestamp_ms, thd_threshold_percent, data)
        log.maybe_debug("Found %d THD Incidents." % len(incidents), thd_plugin)
    except Exception as e:
        incidents = []
        thd_plugin.logger.error("Error finding THD incidents: %s", str(e))

    incident_ids: typing.List[int] = []

    for incident in incidents:
        try:
            incident_id = mongo.store_incident(
                mauka_message.payload.event_id,
                mauka_message.payload.box_id,
                incident.start_time_ms,
                incident.end_time_ms,
                mongo.IncidentMeasurementType.VOLTAGE,
                -1,
                [mongo.IncidentClassification.EXCESSIVE_THD],
                [],
                {},
                opq_mongo_client
            )
            log.maybe_debug("Stored incident with id=%s" % incident_id, thd_plugin)
            incident_ids.append(incident_id)
        except Exception as e:
            thd_plugin.logger.error("Error storing THD incident %s", str(e))

    return incident_ids


class ThdPlugin(plugins.base_plugin.MaukaPlugin):
    """
    Mauka plugin that calculates THD over raw waveforms.
    """
    NAME = "ThdPlugin"

    def __init__(self, conf: config.MaukaConfig, exit_event: multiprocessing.Event):
        """
        Initializes this plugin
        :param conf: Mauka configuration
        :param exit_event: Exit event that can disable this plugin from parent process
        """
        super().__init__(conf, [Routes.adc_samples, Routes.thd_request_event], ThdPlugin.NAME, exit_event)
        self.threshold_percent = float(self.config.get("plugins.ThdPlugin.threshold.percent"))

    def on_message(self, topic, mauka_message):
        """
        Fired when this plugin receives a message. This will wait a certain amount of time to make sure that data
        is in the database before starting thd calculations.
        :param topic: Topic of the message.
        :param mauka_message: Contents of the message.
        """
        if protobuf.pb_util.is_payload(mauka_message, protobuf.mauka_pb2.ADC_SAMPLES):
            self.debug("on_message {}:{} len:{}".format(mauka_message.payload.event_id,
                                                        mauka_message.payload.box_id,
                                                        len(mauka_message.payload.data)))
            incident_ids = thd(mauka_message, self.threshold_percent, self.mongo_client, self)

            for incident_id in incident_ids:
                # Produce a message to the GC
                self.produce(Routes.laha_gc, protobuf.pb_util.build_gc_update(self.name,
                                                                              protobuf.mauka_pb2.INCIDENTS,
                                                                              incident_id))
        else:
            self.logger.error("Received incorrect mauka message [%s] at ThdPlugin",
                              protobuf.pb_util.which_message_oneof(mauka_message))
