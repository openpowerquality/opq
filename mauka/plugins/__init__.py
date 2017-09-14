"""
This module makes all plugin classes available globally from within their modules.
That is, when you import plugins, you can access all of the plugins from the plugins namespace instead of importing
plugins individually.
"""

import multiprocessing
import typing

from plugins.AcquisitionTriggerPlugin import AcquisitionTriggerPlugin
from plugins.FrequencyThresholdPlugin import FrequencyThresholdPlugin
from plugins.MeasurementPlugin import MeasurementPlugin
from plugins.MeasurementShimPlugin import MeasurementShimPlugin
from plugins.PrintPlugin import PrintPlugin
from plugins.StatusPlugin import StatusPlugin
from plugins.VoltageThresholdPlugin import VoltageThresholdPlugin


def run_plugin(plugin_class, config: typing.Dict) -> typing.Tuple[str, multiprocessing.Process, multiprocessing.Event]:
    """Runs the given plugin using the given configuration dictionary

    :param plugin_class: Name of the class of the plugin to be ran
    :param config: Configuration dictionary
    :return: Returns a tuple of plugin name, process, and exit event
    """

    def _run_plugin(config: typing.Dict, exit_event: multiprocessing.Event):
        """Inner function that acts as target to multiprocess constructor"""
        plugin_instance = plugin_class(config, exit_event)
        plugin_instance._run()

    exit_event = multiprocessing.Event()
    process = multiprocessing.Process(target=_run_plugin, args=(config, exit_event))
    process.start()

    return plugin_class.NAME, process, exit_event
