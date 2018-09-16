import cProfile
import pstats
import io
import os
import numpy
import pandas as pd
import constants
from plugins.makai_event_plugin import frequency_waveform
from plugins.frequency_variation_plugin import frequency_incident_classifier
from config import MaukaConfig
from opq_mauka import load_config


def simulate_waveform(freq: float=constants.CYCLES_PER_SECOND, vrms: float = 120.0, noise: bool = False,
                      noise_variance: float = 1.0, num_samples: int = int(6 * constants.SAMPLES_PER_CYCLE),
                      sample_rate=constants.SAMPLE_RATE_HZ, rnd_seed=0) -> numpy.ndarray:

    rand = numpy.random.RandomState(seed=rnd_seed)

    if not noise:
        return numpy.sqrt(2) * vrms * numpy.sin([freq * 2 * numpy.pi * x / sample_rate for x in range(num_samples)])
    else:
        return numpy.sqrt(2) * vrms * numpy.sin([freq * 2 * numpy.pi * x / sample_rate for x in range(num_samples)]
                                                ) + numpy.sqrt(noise_variance) * rand.randn(num_samples)


def write_profile(operation, file, prof):
    # write profile to output file
    file.write('--------{}-------- \n \n'.format(operation))

    s = io.StringIO()
    ps = pstats.Stats(prof, stream=s).sort_stats('cumulative')
    ps.print_stats()
    file.write('{} \n \n'.format(s.getvalue()))

    # clear profile and close s
    prof.clear()
    s.close()


def profile_frequency_variation_plugin(data_file: str):
    """
    profiler for frequency variation plugin
    :param data_file:
    :param output_file:
    :return:
    """

    if not os.path.exists(data_file):
        print('Data File provided: {} Not Found'.format(data_file))
        return 0

    # read file
    df = pd.read_table(data_file, header=None)

    # load configurations
    config_dict = load_config("config.json")
    config = MaukaConfig(config_dict)
    window_size = int(int(config.get("plugins.MakaiEventPlugin.frequencyWindowCycles")) * constants.SAMPLES_PER_CYCLE)
    filter_order = int(config.get("plugins.MakaiEventPlugin.filterOrder"))
    cutoff_frequency = float(config.get("plugins.MakaiEventPlugin.cutoffFrequency"))
    freq_ref = float(constants.CYCLES_PER_SECOND)
    freq_var_low = float(config.get("plugins.FrequencyVariationPlugin.frequency.variation.threshold.low"))
    freq_var_high = float(config.get("plugins.FrequencyVariationPlugin.frequency.variation.threshold.high"))
    freq_interruption = float(config.get("plugins.FrequencyVariationPlugin.frequency.interruption"))
    max_lull = int(config.get("plugins.FrequencyVariationPlugin.max.lull.windows"))

    # create profiler
    pr = cProfile.Profile()

    # get entire waveform
    waveform = df.values.flatten()

    # obtain frequencies
    frequencies = frequency_waveform(waveform, window_size, filter_order, cutoff_frequency)

    # profile frequency_incident_classifier
    pr.enable()
    incidents = frequency_incident_classifier(0, "", frequencies, 0, freq_ref, freq_var_high, freq_var_low,
                                              freq_interruption, window_size, max_lull)
    pr.disable()

    # open write profile to output file
    file_name = data_file.split('/')[-1]
    output_file = "profilers/profile_results/profile_frequency_variation_plugin_{}".format(file_name)
    out_file = open(output_file, 'w')
    write_profile('Waveform Frequency Calculation', out_file, pr)

    # add incident count to profile
    out_file.write('Incident count: {} \n \n'.format(len(incidents)))
    out_file.write('Frequency Min: {} \n \n'.format(frequencies.min()))
    out_file.write('Frequency Max: {} \n \n'.format(frequencies.max()))

    # Simulate an incident
    waveform_1 = simulate_waveform(num_samples=int(100*constants.SAMPLES_PER_CYCLE))
    waveform_2 = simulate_waveform(freq=60.2, num_samples=int(10*constants.SAMPLE_RATE_HZ / 60.2))
    waveform_3 = simulate_waveform(num_samples=int(100*constants.SAMPLES_PER_CYCLE))
    waveform = numpy.concatenate((waveform_1, waveform_2, waveform_3))

    # obtain frequencies
    frequencies = frequency_waveform(waveform, window_size, filter_order, cutoff_frequency)

    # profile frequency_incident_classifier on simulated event
    pr.enable()
    incidents = frequency_incident_classifier(0, "", frequencies, 0, freq_ref, freq_var_high, freq_var_low,
                                              freq_interruption, window_size, max_lull)
    pr.disable()

    # open write profile to output file
    write_profile('Simulated Waveform Frequency Calculation: 100 cycles then 60.2 Hz for 10 cycles then 100 cycles',
                  out_file, pr)

    # add incident count and classification and start and end indices to profile
    out_file.write('Incident count: {} \n \n'.format(len(incidents)))
    out_file.write('Incident Classifications: {} \n \n'.format(str([i['incident_classifications'] for i in incidents])))
    window_duration = (window_size / constants.SAMPLE_RATE_HZ) * 1000
    start_indices = [i['incident_start_ts'] / window_duration for i in incidents]
    end_indices = [i['incident_end_ts'] / window_duration for i in incidents]
    out_file.write('Incident Start : End indices: {} : {} \n \n'.format(str(start_indices), str(end_indices)))
    out_file.write("Frequencies: {}".format(str(frequencies)))

    out_file.close()