import cProfile
import pstats
import io
import os
import pandas as pd
import constants
from plugins.makai_event_plugin import frequency_waveform
from plugins.makai_event_plugin import frequency
from plugins.makai_event_plugin import smooth_waveform
from config import MaukaConfig
from opq_mauka import load_config


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


def profile_makai_event_plugin(data_file: str):
    if not os.path.exists(data_file):
        print('Data File provided: {} Not Found'.format(data_file))
        return

    # read file
    df = pd.read_table(data_file, header=None)

    # load configurations
    config_dict = load_config("mauka.config.json")
    config = MaukaConfig(config_dict)

    # create profiler
    pr = cProfile.Profile()

    # get entire waveform and single window of waveform
    waveform = df.values.flatten()

    # smooth waveform and profile
    pr.enable()
    smoothed_waveform = smooth_waveform(waveform)
    pr.disable()

    # open and write profile to output file
    file_name = data_file.split('/')[-1]
    output_file = "profilers/profile_results/profile_makai_event_plugin_{}".format(file_name)
    out_file = open(output_file, 'w')
    write_profile('Smoothing', out_file, pr)

    # profile single frequency calculation for a window
    # first obtain frequency window
    window_size = int(config.get("plugins.MakaiEventPlugin.frequencyWindowCycles") * constants.SAMPLES_PER_CYCLE)
    downsample_factor = int(config.get("plugins.MakaiEventPlugin.frequencyDownSampleRate"))
    waveform_window = smoothed_waveform[:window_size]
    # frequency on a single window
    pr.enable()
    frequency(waveform_window, downsample_factor)
    pr.disable()

    # write profile to output file
    write_profile('Single Window Frequency Calculation', out_file, pr)

    # profile frequency calculation for entire waveform
    # first obtain configuration
    filter_order = int(config.get("plugins.MakaiEventPlugin.filterOrder"))
    cutoff_frequency = float(config.get("plugins.MakaiEventPlugin.cutoffFrequency"))
    pr.enable()
    frequencies = frequency_waveform(waveform, window_size, filter_order, cutoff_frequency,
                                     down_sample_factor=downsample_factor)
    pr.disable()

    # write profile to output file
    write_profile('Waveform Frequency Calculation', out_file, pr)

    out_file.close()