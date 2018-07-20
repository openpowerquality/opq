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
from scipy import optimize


def waveform_filter(raw_waveform: numpy.ndarray, fundamental_freq: float = constants.CYCLES_PER_SECOND,
                    fundamental_vrms: float = constants.EXPECTED_VRMS) -> dict:
    """
    Function filter the fundamental waveform to retrieve the potential transient waveform
    :param raw_waveform: The raw sampled voltages
    :param fundamental_freq: The expected fundamental frequency of the waveform
    :param fundamental_vrms: The expected vrms voltage of the waveform
    :return: The filtered waveform, that is the waveform without the fundamental frequency component
    """

    # Fit sinusoidal curve to data
    set_amp = fundamental_vrms * numpy.sqrt(2)
    set_freq = fundamental_freq
    guess_phase = 0.0
    set_mean = 0.0
    idx = numpy.arange(0, len(raw_waveform) / constants.SAMPLE_RATE_HZ, 1 / constants.SAMPLE_RATE_HZ)

    def optimize_func(args):
        """
        Optimized the function for finding and fitting the frequency.
        :param args: A list containing in this order: guess_amp, guess_freq, guess_phase, guess_mean.
        :return: Optimized function.
        """
        return set_amp * numpy.sin(set_freq * 2 * numpy.pi * idx + args[0]) + set_mean - raw_waveform

    est_phase = optimize.leastsq(optimize_func, numpy.array([guess_phase]))[0]
    fundamental_waveform = set_amp * numpy.sin(set_freq * 2 * numpy.pi * idx + est_phase) + set_mean
    filtered_waveform = raw_waveform - fundamental_waveform

    return {"fundamental_waveform": fundamental_waveform, "filtered_waveform": filtered_waveform}

def oscillatory_classifier(filtered_waveform: numpy.ndarray, configs: dict) -> (bool, dict):
    """
    Identifies whether the transient is oscillatory and, if so, further classifies the transient as a medium, low, or
    high frequency oscillatory transient and calculates additional meta data for the transient such as the magnitude,
    duration, and spectral content.
    :param filtered_waveform: The transient waveform, that is the sampled waveform without the fundamental frequency
    included
    :param configs: Includes the necessary parameters needed to classify the transient
    :return: A tuple which has contains a boolean indicator of whether the transient was indeed classified as being
    oscillatory and then a dictionary of the calculated meta data.
    """

def impulsive_classifier(filtered_waveform: numpy.ndarray, configs: dict) -> (bool, dict):
    """
    Identifies whether the transient is impulsive and, if so, calculates additional meta data for the transient, such as
    the magnitude, duration, and rise/fall and fall/rise times.
    :param filtered_waveform: The transient waveform, that is the sampled waveform without the fundamental frequency
    included
    :param configs: Includes the necessary parameters needed to classify the transient
    :return: A tuple which has contains a boolean indicator of whether the transient was indeed classified as being
    impulsive and then a dictionary of the calculated meta data.
    """

def arcing_classifier(filtered_waveform: numpy.ndarray, configs: dict) -> (bool, dict):
    """
    Identifies whether the transient is arcing and, if so, calculates additional meta data for the transient, such as
    the number of zero crossings in the transient waveform
    :param filtered_waveform: The transient waveform, that is the sampled waveform without the fundamental frequency
    included
    :param configs: Includes the necessary parameters needed to classify the transient
    :return: A tuple which has contains a boolean indicator of whether the transient was indeed classified as being
    arcing and then a dictionary of the calculated meta data.
    """

def periodic_notching_classifier(filtered_waveform: numpy.ndarray, configs: dict) -> (bool, dict):
    """
    Identifies whether the transient is periodic notching and, if so, calculates additional meta data for the transient,
    such as the amplitude, width, period, and time
    :param filtered_waveform: The transient waveform, that is the sampled waveform without the fundamental frequency
    included
    :param configs: Includes the necessary parameters needed to classify the transient
    :return: A tuple which has contains a boolean indicator of whether the transient was indeed classified as being
    periodic notching and then a dictionary of the calculated meta data.
    """

def pf_cap_switching_classifier(filtered_waveform: numpy.ndarray, fundamental_waveform: numpy.ndarray,
                     configs: dict) -> (bool, dict):
    """
    Identifies whether the transient is pf_cap_switching and, if so, calculates additional meta data for the transient,
    such as the frequency, peak amplitude, and oscillatory decay time
    :param filtered_waveform: The transient waveform, that is the sampled waveform without the fundamental frequency
    included
    :param fundamental_waveform: The fundamental waveform, that is the sampled waveform without any interference
    :param configs: Includes the necessary parameters needed to classify the transient
    :return: A tuple which has contains a boolean indicator of whether the transient was indeed classified as being
    pf_cap_switching and then a dictionary of the calculated meta data.
    """

def multiple_zero_xing_classifier(raw_waveform: numpy.ndarray, configs: dict) -> (bool, dict):
    """
    Identifies whether the transient is pf_cap_switching and, if so, calculates additional meta data for the transient,
    such as the peak, mean, and range of the transient amplitude, and the number of zero crossings caused by the
    transient
    :param raw_waveform: The raw sampled waveform
    :param configs: Includes the necessary parameters needed to classify the transient
    :return: A tuple which has contains a boolean indicator of whether the transient was indeed classified as being
    a multiple zero crossing transient, and then a dictionary of the calculated meta data.
    """

def transient_incident_classifier(event_id: int, box_id: str, raw_waveform: numpy.ndarray,
                                  box_event_start_ts: int, configs: dict):
    """
    Identifies  as a Sag, Swell, or Interruption. Creates a Mongo Incident document
    :param event_id:
    :param box_id:
    :param raw_waveform:
    :param box_event_start_ts:
    :param configs:
    :return:
    """

    filtered_waveform = waveform_filter(raw_waveform, )

    implusive = impulsive_classifier()

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
