"""
This plugin detects, classifies, and stores transient incidents.
Transient are classified using the IEEE 1159 standard
"""
import typing
import multiprocessing
import numpy

from scipy import optimize
from scipy import stats
from scipy import signal

import constants
import plugins.base_plugin
import protobuf.mauka_pb2
import protobuf.util
import mongo


def transient_sliding_window(filtered_waveform: numpy.ndarray, noise_floor: float, max_lull_ms: float) -> list:
    """
    Function to find candidate transient window start and stop indices
    :param filtered_waveform:
    :param noise_floor:
    :param max_lull_ms:
    :return:
    """
    voltage_above_noise_floor = filtered_waveform >= noise_floor
    transient_windows = []
    max_samples = int(constants.SAMPLES_PER_MILLISECOND * max_lull_ms)
    lull_counter = 0
    new_pass = True
    start = 0

    for i in range(len(filtered_waveform)):
        if voltage_above_noise_floor[i]:
            lull_counter = 0
            if new_pass:
                start = i
                new_pass = False
        elif not new_pass:
            lull_counter += 1

        if lull_counter > max_samples:
            transient_windows.append((start, i - max_samples))
            lull_counter = 0
            new_pass = True

    if not new_pass:
        transient_windows.append((start, len(filtered_waveform)))

    return transient_windows


def noise_canceler(voltage, noise_floor):
    """
    Cancels waveform measurements below noise floor. This method is intended to be used in a vectorized fashion.
    :param voltage: The voltage measurement
    :param noise_floor: The noise floor
    :return: voltage above noise floor.
    """
    if abs(voltage) < noise_floor:
        return 0.0
    else:
        if voltage < 0:
            return voltage + noise_floor
        else:
            return voltage - noise_floor


def find_zero_xings(waveform: numpy.ndarray) -> numpy.ndarray:
    """
    Function which returns a boolean array indicating the positions of zero crossings in the the waveform
    :param waveform:
    :return: a boolean array indicating the positions of zero crossings in the the waveform
    """
    return numpy.diff(numpy.signbit(waveform))


def waveform_filter(raw_waveform: numpy.ndarray, filter_order: int, transient_cutoff_frequency: float) -> dict:
    """
    Function to filter out the fundamental waveform to retrieve the potential transient waveform
    :param raw_waveform: The raw sampled voltages
    :param filter_order: The order of the low pass Butterworth filter
    :param transient_cutoff_frequency: The cutoff frequency of the low pass Butterworth filter.
    :return: The filtered waveform, that is the waveform without the fundamental frequency component
    """

    # smooth digital signal w/ Butterworth filter
    # First, design the Butterworth filter
    # Cutoff frequencies in half-cycles / sample
    cutoff_frequency_nyquist = transient_cutoff_frequency * 2 / constants.SAMPLE_RATE_HZ
    numerator, denominator = signal.butter(filter_order, cutoff_frequency_nyquist, output='ba')

    fundamental_waveform = signal.filtfilt(numerator, denominator, raw_waveform)
    filtered_waveform = raw_waveform - fundamental_waveform

    return {"fundamental_waveform": fundamental_waveform, "filtered_waveform": filtered_waveform,
            "raw_waveform": raw_waveform}


def oscillatory_classifier(filtered_waveform: numpy.ndarray) -> (bool, dict):
    """
    Identifies whether the transient is oscillatory and, if so, further classifies the transient as a medium, low, or
    high frequency oscillatory transient and calculates additional meta data for the transient such as the magnitude,
    duration, and spectral content.
    :param filtered_waveform: The transient waveform, that is the sampled waveform without the fundamental frequency
    included
    :return: A tuple which has contains a boolean indicator of whether the transient was indeed classified as being
    oscillatory and then a dictionary of the calculated meta data.
    """

    # Fit damped sine wave to signal
    guess_amp = constants.NOMINAL_VRMS * numpy.sqrt(2)
    guess_decay = 200.0
    guess_freq = 2500.0
    guess_phase = 0.0
    guess_mean = 0.0
    idx = numpy.arange(0, len(filtered_waveform) / constants.SAMPLE_RATE_HZ, 1 / constants.SAMPLE_RATE_HZ)
    alpha = 0.05

    i = 0
    while len(idx) != len(filtered_waveform):
        if len(idx) > len(filtered_waveform):
            idx = idx[:len(filtered_waveform)]
        elif len(idx) < len(filtered_waveform):
            idx = numpy.arange(0, (len(filtered_waveform) + i) / constants.SAMPLE_RATE_HZ, 1 / constants.SAMPLE_RATE_HZ)
            i = i + 1

    def optimize_func(args):
        """
        Optimized the function for finding and fitting the frequency.
        :param args: A list containing in this order: guess_amp, guess_freq, guess_phase, guess_mean.
        :return: Optimized function.
        """
        y_hat = args[0] * numpy.exp(-1.0 * args[1] * idx) * numpy.cos(args[2] * 2 * numpy.pi * idx + args[3]) + args[4]
        return filtered_waveform - y_hat

    lst_sq_sol = optimize.leastsq(optimize_func,
                                  numpy.array([guess_amp, guess_decay, guess_freq, guess_phase, guess_mean]))

    rss1 = numpy.power(optimize_func(lst_sq_sol[0]), 2).sum()

    def optimize_func_constrained(args):
        """
        Optimized the function for finding and fitting the frequency.
        :param args: A list containing in this order:
        :return: Optimized function.
        """
        y_hat = args[0] * numpy.exp(-1.0 * args[1] * idx) + args[1]
        return filtered_waveform - y_hat

    lst_sq_sol_constrained = optimize.leastsq(optimize_func_constrained, numpy.array([0, 0]))

    rss0 = numpy.power(optimize_func_constrained(lst_sq_sol_constrained[0]), 2).sum()
    # Start ignoring PyLintBear
    numerator = numpy.divide((rss0 - rss1), 2)
    denominator = numpy.divide(rss1, (len(idx) - 4 - 1))
    # Stop ignoring
    f_statistic = numerator / denominator
    p_value = 1 - stats.f.cdf(f_statistic, 2, (len(idx) - 4 - 1))

    if p_value < alpha:
        return True, {'Frequency': lst_sq_sol[0][2], 'p_value': p_value}
    else:
        return False, {}


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

    noise_canceled_waveform = numpy.vectorize(noise_canceler)(filtered_waveform, configs['noise_floor'])

    if numpy.vectorize(lambda v: v >= 0)(noise_canceled_waveform).all():
        polarity = 'Positive'
        peak_index = noise_canceled_waveform.argmax()
        peak_voltage = filtered_waveform[peak_index]
        start_index = (noise_canceled_waveform != 0).argmax()
        decay_voltages = noise_canceled_waveform[peak_index:]
        end_index = decay_voltages.argmin() + peak_index
        rise_time = (peak_index - start_index) / constants.SAMPLE_RATE_HZ
        decay_time = (end_index - peak_index) / constants.SAMPLE_RATE_HZ
    elif numpy.vectorize(lambda v: v <= 0)(noise_canceled_waveform).all():
        polarity = 'Negative'
        peak_index = noise_canceled_waveform.argmin()
        peak_voltage = filtered_waveform[peak_index]
        start_index = (noise_canceled_waveform != 0).argmax()
        decay_voltages = noise_canceled_waveform[peak_index:]
        end_index = decay_voltages.argmax() + peak_index
        rise_time = (peak_index - start_index) / constants.SAMPLE_RATE_HZ
        decay_time = (end_index - peak_index) / constants.SAMPLE_RATE_HZ
    else:
        return False, {}

    return True, {"Polarity": polarity, "Peak_Voltage": peak_voltage, "Rise_Time": rise_time,
                  "Decay_Time": decay_time, "Start_Index": start_index, "Peak_Index": peak_index,
                  "End_Index": end_index}


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
    noise_canceled_waveform = numpy.vectorize(noise_canceler)(filtered_waveform, configs['noise_floor'])

    transient_zero_xings = find_zero_xings(noise_canceled_waveform)
    num_cycles = transient_zero_xings.sum()

    if num_cycles >= 10:
        if numpy.unique(numpy.diff(numpy.where(transient_zero_xings)), return_counts=True)[1].max() > 2:
            return True, {'Num_Cycles': num_cycles}

    return False, {}


def periodic_notching_classifier(filtered_waveform: numpy.ndarray, fundamental_waveform: numpy.ndarray,
                                 configs: dict) -> (bool, dict):
    """
    Identifies whether the transient is periodic notching and, if so, calculates additional meta data for the transient,
    such as the amplitude, width, period, and time.
    :param filtered_waveform: The transient waveform, that is the sampled waveform without the fundamental frequency
    included
    :param fundamental_waveform: The fundamental waveform of the signal during the transient window, used to determine
    whether the notching is negative power or not.
    :param configs: Includes the necessary parameters needed to classify the transient
    :return: A tuple which has contains a boolean indicator of whether the transient was indeed classified as being
    periodic notching and then a dictionary of the calculated meta data.
    """

    # cancel out measurements of filtered_waveform below noise_floor
    noise_canceled_waveform = numpy.vectorize(noise_canceler)(filtered_waveform, configs['noise_floor'])

    # determine whether the notching is negative power or not
    if 1 in numpy.sign(noise_canceled_waveform) * numpy.sign(fundamental_waveform):
        return False, {}

    # determine whether the notching is nearly periodic
    first_non_zero_index = numpy.nonzero(noise_canceled_waveform)[0][0]
    last_non_zero_index = numpy.nonzero(noise_canceled_waveform)[0][-1]
    transient = noise_canceled_waveform[first_non_zero_index: last_non_zero_index + 1]

    # determine whether transient wave is nearly periodic
    transient_abs = numpy.abs(transient)

    auto_corr = numpy.correlate(transient_abs, transient_abs[:int(transient_abs.size / 2)], mode='valid')
    auto_corr = auto_corr[int(auto_corr.size / 2):]
    auto_corr = auto_corr / numpy.max(auto_corr)
    peaks = signal.find_peaks(auto_corr, height=configs["auto_corr_thresh_periodicity"])
    periods = numpy.diff(peaks[0])
    if numpy.std(numpy.abs(numpy.diff(periods))) > configs["max_std_periodic_notching"]:
        return False, {}
    else:
        average_amplitude = numpy.average(
            transient_abs[signal.find_peaks(transient_abs)[0]]) + configs['noise_floor']
        average_period = numpy.average(periods) / constants.SAMPLE_RATE_HZ
        return True, {'amplitude': average_amplitude, 'period': average_period}


def multiple_zero_xing_classifier(waveforms: dict, configs: dict) -> (bool, dict):
    """
    Identifies whether the transient causes multiple zero crossings and, if so, calculates additional meta data for the
    transient, such as the additional number of zero crossings caused by the transient
    :param waveforms: The raw, fundamental, and filtered waveform
    :param configs: Includes the necessary parameters needed to classify the transient
    :return: A tuple which has contains a boolean indicator of whether the transient was indeed classified as being
    a multiple zero crossing transient, and then a dictionary of the calculated metadata.
    """
    raw_zero_xings = find_zero_xings(waveforms['raw_waveform'])
    fundamental_zero_xings = find_zero_xings(waveforms['fundamental_waveform'])

    if raw_zero_xings.sum() > fundamental_zero_xings.sum():
        # Start ignoring PyLintBear
        extra_zero_xings = numpy.logical_xor(raw_zero_xings, fundamental_zero_xings)
        # Stop ignoring
        voltages_at_extra_xings = waveforms['filtered_waveform'][numpy.where(extra_zero_xings)[0]]
        extra_xings_above_noise_floor = numpy.abs(voltages_at_extra_xings) > configs['noise_floor']
        num_xings = extra_xings_above_noise_floor.sum()
        return num_xings > 0, {'num_extra_zero_crossings': num_xings}
    else:
        return False, {}


def transient_incident_classifier(event_id: int, box_id: str, raw_waveform: numpy.ndarray, box_event_start_ts: int,
                                  configs: dict, opq_mongo_client: mongo.OpqMongoClient = None, logger=None):
    """
    Classifies transient waveform. Creates a Mongo Incident document
    :param event_id:
    :param box_id:
    :param raw_waveform:
    :param box_event_start_ts:
    :param configs:
    :param opq_mongo_client:
    :param logger:
    :return: list of the classified incidents
    """

    mongo_client = mongo.get_default_client(opq_mongo_client)

    incidents = []
    meta = {}
    incident_classifications = []
    incident_flag = False

    waveforms = waveform_filter(raw_waveform, configs['filter_order'], configs['filter_cutoff_frequency'])
    candidate_transient_windows = transient_sliding_window(waveforms["filtered_waveform"], configs["noise_floor"],
                                                           configs["max_lull_ms"])

    if logger is not None:
        logger.debug("Calculating transients with {} segments.".format(len(candidate_transient_windows)))

    for window in candidate_transient_windows:
        windowed_waveforms = {"fundamental_waveform": waveforms["fundamental_waveform"][window[0]: window[1] + 1],
                              "filtered_waveform": waveforms["filtered_waveform"][window[0]: window[1] + 1],
                              "raw_waveform": waveforms["raw_waveform"][window[0]: window[1] + 1]}
        incident_start_ts = int(window[0] / constants.SAMPLES_PER_MILLISECOND + box_event_start_ts)
        incident_end_ts = int(incident_start_ts + (window[1] - window[0]) / constants.SAMPLES_PER_MILLISECOND)

        impulsive = impulsive_classifier(windowed_waveforms["filtered_waveform"], configs)
        if impulsive[0]:
            meta.update(impulsive[1])
            incident_classifications.append("IMPULSIVE_TRANSIENT")
            incident_flag = True

        else:
            arcing = arcing_classifier(windowed_waveforms["filtered_waveform"], configs)
            if arcing[0]:
                meta.update(arcing[1])
                incident_classifications.append("ARCING_TRANSIENT")
                incident_flag = True

            else:
                oscillatory = oscillatory_classifier(windowed_waveforms["filtered_waveform"])
                if oscillatory[0]:
                    meta.update(oscillatory[1])
                    incident_classifications.append("OSCILLATORY_TRANSIENT")
                    incident_flag = True

                else:
                    periodic_notching = periodic_notching_classifier(windowed_waveforms["filtered_waveform"],
                                                                     windowed_waveforms["fundamental_waveform"],
                                                                     configs)
                    if periodic_notching[0]:
                        meta.update(periodic_notching[1])
                        incident_classifications.append("PERIODIC_NOTCHING_TRANSIENT")
                        incident_flag = True

        multiple_zero_xing = multiple_zero_xing_classifier(windowed_waveforms,
                                                           configs)
        if multiple_zero_xing[0]:
            meta.update(multiple_zero_xing[1])
            incident_classifications.append("MULTIPLE_ZERO_CROSSING_TRANSIENT")
            incident_flag = True

        if incident_flag:
            incidents.append({"event_id": event_id,
                              "box_id": box_id,
                              "incident_start_ts": incident_start_ts,
                              "incident_end_ts": incident_end_ts,
                              "incident_type": mongo.IncidentMeasurementType.TRANSIENT,
                              "max_deviation": numpy.max(numpy.abs(windowed_waveforms["filtered_waveform"])),
                              "incident_classifications": incident_classifications,
                              "annotations": [],
                              "metadata": meta,
                              "mongo_client": mongo_client})

        incident_flag = False
        incident_classifications = []
        meta = {}

    return incidents


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
            "noise_floor": float(self.config_get("plugins.TransientPlugin.noise.floor")),
            "filter_cutoff_frequency": float(self.config_get("plugins.MakaiEventPlugin.cutoffFrequency")),
            "filter_order": float(self.config_get("plugins.MakaiEventPlugin.filterOrder")),
            "oscillatory_min_cycles": int(self.config_get("plugins.TransientPlugin.oscillatory.min.cycles")),
            "oscillatory_low_freq_max": float(self.config_get("plugins.TransientPlugin.oscillatory.low.freq.max.hz")),
            "oscillatory_med_freq_max": float(self.config_get("plugins.TransientPlugin.oscillatory.med.freq.max.hz")),
            "oscillatory_high_freq_max": float(self.config_get("plugins.TransientPlugin.oscillatory.high.freq.max.hz")),
            "arc_zero_xing_threshold": int(self.config_get("plugins.TransientPlugin.arcing.zero.crossing.threshold")),
            "max_lull_ms": float(self.config_get("plugins.TransientPlugin.max.lull.ms")),
            "max_std_periodic_notching": float(self.config_get(
                "plugins.TransientPlugin.max.periodic.notching.std.dev")),
            "auto_corr_thresh_periodicity": float(
                self.config_get("plugins.TransientPlugin.auto.corr.thresh.periodicity"))
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
                    incident["max_deviation"],
                    incident["incident_classifications"],
                    incident["annotations"],
                    incident["metadata"],
                    incident["mongo_client"]
                )
        else:
            self.logger.error("Received incorrect mauka message [%s] at TransientPlugin",
                              protobuf.util.which_message_oneof(mauka_message))
