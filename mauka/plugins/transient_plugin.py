"""
This plugin detects, classifies, and stores transient incidents.
Transient are classified using the IEEE 1159 standard
"""
import typing
import multiprocessing
import numpy
import constants
import plugins.base_plugin
import protobuf.mauka_pb2
import protobuf.util
import mongo



class TransientPlugin(plugins.base_plugin.MaukaPlugin):
    """
    Mauka plugin that detects and classifies transients in accordance to the IEEE 1159 standard."""
    NAME = "TransientPlugin"

    def __init__(self, config: typing.Dict, exit_event: multiprocessing.Event):
        """
        Initializes this plugin
        :param config: Mauka configuration
        :param exit_event: Exit event that can disable this plugin from parent process
        """
        super().__init__(config, ["RawVoltage"], TransientPlugin.NAME, exit_event)
        self.noise_floor_percent = float(self.config_get("plugins.TransientPlugin.noise.floor.percent"))


    def on_message(self, topic, mauka_message):
        """
        Called async when a topic this plugin subscribes to produces a message
        :param topic: The topic that is producing the message
        :param mauka_message: The message that was produced
        """
        self.debug("{} on_message".format(topic))
        if protobuf.util.is_payload(mauka_message, protobuf.mauka_pb2.FREQUENCY_WINDOWED):
            self.debug("on_message {}:{} len:{}".format(mauka_message.payload.event_id,
                                                        mauka_message.payload.box_id,
                                                        len(mauka_message.payload.data)))

            incidents = transient_incident_classifier(mauka_message.payload.event_id, mauka_message.payload.box_id,
                                                      protobuf.util.repeated_as_ndarray(mauka_message.payload.data),
                                                      mauka_message.payload.start_timestamp_ms,
                                                      self.freq_ref, self.freq_var_high, self.freq_var_low,
                                                      self.freq_interruption, logger=self.logger)

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
                    incident["mongo_client"]
                )
        else:
            self.logger.error("Received incorrect mauka message [%s] at FrequencyVariationPlugin",
                              protobuf.util.which_message_oneof(mauka_message))
