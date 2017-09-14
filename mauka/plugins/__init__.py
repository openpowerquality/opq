"""
This module makes all plugin classes available globally from within their modules.
That is, when you import plugins, you can access all of the plugins from the plugins namespace instead of importing
plugins individually.
"""

import multiprocessing
import typing

from plugins import AcquisitionTriggerPlugin
from plugins import FrequencyThresholdPlugin
from plugins import MeasurementPlugin
from plugins import MeasurementShimPlugin
from plugins import PrintPlugin
from plugins import StatusPlugin
from plugins import VoltageThresholdPlugin


def run_plugin(plugin_class, config: typing.Dict) -> typing.Tuple[multiprocessing.Process, multiprocessing.Event]:
    """Runs the given plugin using the given configuration dictionary

    :param plugin_class: Name of the class of the plugin to be ran
    :param config: Configuration dictionary
    :return: Returns a tuple of process and exit event
    """

    def _run_plugin(config: typing.Dict, exit_event: multiprocessing.Event):
        """Inner function that acts as target to multiprocess constructor"""
        plugin_instance = plugin_class(config, exit_event)
        plugin_instance._run()

    exit_event = multiprocessing.Event()
    process = multiprocessing.Process(target=_run_plugin, args=(config, exit_event))
    process.start()

    return process, exit_event
