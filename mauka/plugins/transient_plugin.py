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


def transient_incident_classifier(event_id: int, box_id: str, windowed_frequencies: numpy.ndarray,
                                  box_event_start_ts: int, configs: dict):
    """
    Identifies  as a Sag, Swell, or Interruption. Creates a Mongo Incident document
    :param event_id:
    :param box_id:
    :param windowed_frequencies:
    :param box_event_start_ts:
    :param configs:
    :return:
    """
    # TODO
    return None

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
        self.configs = {
            "noise_floor_percent": float(self.config_get("plugins.TransientPlugin.noise.floor.percent")),
            "oscillatory_min_cycles": int(self.config_get("plugins.TransientPlugin.oscillatory.min.cycles")),
            "oscillatory_low_freq_max": float(self.config_get("plugins.TransientPlugin.oscillatory.low.freq.max.hz")),
            "oscillatory_med_freq_max": float(self.config_get("plugins.TransientPlugin.oscillatory.med.freq.max.hz")),
            "oscillatory_high_freq_max": float(self.config_get("plugins.TransientPlugin.oscillatory.high.freq.max.hz")),
            "arc_zero_xing_threshold": int(self.config_get("plugins.TransientPlugin.arcing.zero.crossing.threshold")),
            "pf_cap_switch_low_ratio": float(self.config_get("plugins.TransientPlugin.PF.cap.switching.low.ratio")),
            "pf_cap_switch_high_ratio": float(self.config_get("plugins.TransientPlugin.PF.cap.switching.high.ratio")),
            "pf_cap_switch_low_freq": float(self.config_get("plugins.TransientPlugin.PF.cap.switching.low.freq.hz")),
            "pf_cap_switch_high_freq": float(self.config_get("plugins.TransientPlugin.PF.cap.switching.high.freq.hz"))
            }

    def on_message(self, topic, mauka_message):
        """
        Called async when a topic this plugin subscribes to produces a message
        :param topic: The topic that is producing the message
        :param mauka_message: The message that was produced
        """
        self.debug("{} on_message".format(topic))
        if protobuf.util.is_payload(mauka_message, protobuf.mauka_pb2.VOLTAGE_RAW):
            self.debug("on_message {}:{} len:{}".format(mauka_message.payload.event_id,
                                                        mauka_message.payload.box_id,
                                                        len(mauka_message.payload.data)))

            incidents = transient_incident_classifier(mauka_message.payload.event_id, mauka_message.payload.box_id,
                                                      protobuf.util.repeated_as_ndarray(mauka_message.payload.data),
                                                      mauka_message.payload.start_timestamp_ms, self.configs)

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
            self.logger.error("Received incorrect mauka message [%s] at TransientPlugin",
                              protobuf.util.which_message_oneof(mauka_message))
