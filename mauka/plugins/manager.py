import logging
import multiprocessing
import os
import typing

_logger = logging.getLogger("app")
logging.basicConfig(
    format="[%(levelname)s][%(asctime)s][{} %(filename)s:%(lineno)s - %(funcName)s() ] %(message)s".format(
        os.getpid()))
_logger.setLevel(logging.DEBUG)


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


class PluginManager:
    def __init__(self, plugins: typing.List, config: typing.Dict):
        self.plugins = plugins
        self.config = config
        self.processes = []

    def start_all_plugins(self):
        for plugin_run in self.plugins:
            plugin_class = plugin_run[0]
            should_run = plugin_run[1]
            if should_run:
                try:
                    self.processes.append(run_plugin(plugin_class, self.config))
                except KeyError as e:
                    _logger.error("Could not load plugin due to configuration error: {}".format(e))