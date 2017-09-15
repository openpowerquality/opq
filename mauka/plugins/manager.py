"""
This module provides facilities for managing (stopping, starting, loading, reloading) plugin subprocesses.
"""

import importlib
import inspect
import json
import logging
import multiprocessing
import os
import sys
import typing

import zmq

_logger = logging.getLogger("app")
logging.basicConfig(
    format="[%(levelname)s][%(asctime)s][{} %(filename)s:%(lineno)s - %(funcName)s() ] %(message)s".format(
        os.getpid()))
_logger.setLevel(logging.DEBUG)


class PluginManager:
    """
    This class provides facilities for managing (stopping, starting, loading, reloading) plugin subprocesses.
    """
    def __init__(self, config: typing.Dict):
        """Initializes the plugin manager

        :param config: Configuration dictionary

        """
        self.config = config
        """Configuration dictionary"""

        self.name_to_plugin_class = {}
        """Name of plugin to its corresponding Python class"""

        self.name_to_process = {}
        """Name of plugin to its corresponding process (if it has one)"""

        self.name_to_exit_event = {}
        """Name of plugin to its corresponding exit event object (if it has one)"""

        self.name_to_enabled = {}
        """Name of plugin to whether or not the plugin is enabled"""

        self.zmq_context = zmq.Context()
        """ZeroMQ context"""

        self.zmq_pub_socket = self.zmq_context.socket(zmq.PUB)
        """ZeroMQ publishing socket (allows publishing messages to plugins)"""

        self.zmq_pub_socket.connect(self.config["zmq.mauka.plugin.pub.interface"])

    def register_plugin(self, plugin_class, enabled: bool = True):
        """Registers a plugin with the manager

        :param plugin_class: Python class of plugin
        :param enabled: Whether or not this plugin is enabled when loaded
        """
        name = plugin_class.NAME
        self.name_to_plugin_class[name] = plugin_class
        self.name_to_enabled[name] = enabled

    def run_plugin(self, plugin_name: str):
        """Run the given plugin

        :param plugin_name: Name of the plugin
        """
        if plugin_name not in self.name_to_plugin_class:
            _logger.error("Plugin {} DNE".format(plugin_name))
            return

        if not self.name_to_enabled[plugin_name]:
            _logger.error("Can not run disabled plugin")

        def _run_plugin(plugin_class, config: typing.Dict, exit_event: multiprocessing.Event):
            """Inner function that acts as target to multiprocess constructor"""
            plugin_instance = plugin_class(config, exit_event)
            plugin_instance._run()

        plugin_class = self.name_to_plugin_class[plugin_name]
        exit_event = multiprocessing.Event()
        process = multiprocessing.Process(target=_run_plugin, args=(plugin_class, self.config, exit_event))
        process.start()
        self.name_to_process[plugin_name] = process
        self.name_to_exit_event[plugin_name] = exit_event

    def run_all_plugins(self):
        """Run all loaded and enabled plugins"""
        _logger.info("Starting all plugins")
        for name in self.name_to_plugin_class:
            if self.name_to_enabled[name]:
                self.run_plugin(name)

    def get_class(self, mod, class_name: str):
        """Given a module, return a class from that module with the given name

        :param mod: The module to search for the class in
        :param class_name: The class name we are attempting to retrieve
        :return: The class we are attempting to retrieve or None if the class DNE
        """
        for name_val in inspect.getmembers(mod, inspect.isclass):
            name = name_val[0]
            val = name_val[1]
            if name == class_name:
                return val
            return None

    def start_tcp_server(self):
        """Starts a TCP server backed by ZMQ. This server is connected to my out cli client"""
        _logger.info("Starting plugin manager TCP server")
        zmq_context = zmq.Context()
        zmq_reply_socket = zmq_context.socket(zmq.REP)
        zmq_reply_socket.bind(self.config["zmq.mauka.plugin.management.rep.interface"])

        while True:
            request = zmq_reply_socket.recv_string()
            zmq_reply_socket.send_string(self.handle_tcp_request(request))

    def handle_tcp_request(self, request: str) -> str:
        """Handle TCP request messages

        :param request: The message to handle
        :return: The response message
        """
        if request.startswith("disable-plugin"):
            plugin_name = request.split(" ")[1]
            return self.cli_disable_plugin(plugin_name)
        elif request.startswith("enable-plugin"):
            plugin_name = request.split(" ")[1]
            return self.cli_enable_plugin(plugin_name)
        elif request == "help":
            return self.cli_help()
        elif request.startswith("kill-plugin"):
            plugin_name = request.split(" ")[1]
            return self.cli_kill_plugin(plugin_name)
        elif request.startswith("load-config"):
            config_path = request.split(" ")[1]
            return self.cli_load_config(config_path)
        elif request.startswith("load-plugin"):
            plugin_name = request.split(" ")[1]
            return self.cli_load_plugin(plugin_name)
        elif request == "list-plugins":
            return self.cli_list_plugins()
        elif request.startswith("start-plugin"):
            plugin_name = request.strip().split(" ")[1]
            return self.cli_start_plugin(plugin_name)
        elif request.startswith("stop-plugin"):
            plugin_name = request.strip().split(" ")[1]
            return self.cli_stop_plugin(plugin_name)
        elif request.startswith("restart-plugin"):
            plugin_name = request.strip().split(" ")[1]
            return self.cli_restart_plugin(plugin_name)
        elif request.startswith("unload-plugin"):
            plugin_name = request.split(" ")[1]
            return self.cli_unload_plugin(plugin_name)
        else:
            return "Unknown cmd {}".format(request)

    def cli_disable_plugin(self, plugin_name: str) -> str:
        """Disables the given plugin

        :param plugin_name: Name of the plugin to disable
        :return: Server response
        """
        if plugin_name not in self.name_to_plugin_class:
            return "Plugin {} DNE".format(plugin_name)

        self.name_to_enabled[plugin_name] = False
        return "OK"

    def cli_enable_plugin(self, plugin_name: str) -> str:
        """Enables the given plugin

        :param plugin_name: Name of the plugin to enable
        :return: Server response
        """
        if plugin_name not in self.name_to_plugin_class:
            return "Plugin {} DNE".format(plugin_name)

        self.name_to_enabled[plugin_name] = True
        return "OK"

    def cli_help(self) -> str:
        """Returns the available usage for the cli"""
        return """
            disable-plugin [plugin name]
                Disables the named plugin.
            enable-plugin [plugin name]
                Enables the named plugin.
            exit
                Exits the opq-mauka cli.
            help
                Displays this message.
            kill-plugin [plugin name]
                Kills the named plugin
            load-config [configuration file path]
                Reloads the configuration file.
            load-plugin [plugin name]
                Loads (or reloads) the named plugin from disk.
            list-plugins
                Display status of all loaded plugins.
            start-plugin [plugin name]
                Start the named plugin.
            stop-plugin [plugin name]
                Stop the named plugin.
            restart-plugin [plugin name]
                Restarts the named plugin.
            unload-plugin [plugin name]
                Unload the named plugin.
            """

    def cli_kill_plugin(self, plugin_name: str) -> str:
        """Kills the named plugin

        :param plugin_name: The plugin to kill
        :return: Server response
        """

        if plugin_name not in self.name_to_plugin_class:
            return "Plugin {} DNE".format(plugin_name)

        if plugin_name not in self.name_to_process:
            return "Plugin {} does not have associated process".format(plugin_name)

        self.name_to_process[plugin_name].terminate()
        return "OK"

    def cli_load_config(self, config_path: str) -> str:
        """Loads new configuration values

        Plugins need to be restarted to take advantage of new values

        :param config_path: Path to configuration file
        :return: Server response
        """
        if not os.path.isfile(config_path):
            return "Path {} DNE".format(config_path)

        try:
            self.config = load_config(config_path)
            return "OK"
        except Exception as e:
            return "Exception occured while loading config: {}".format(e)

    def cli_load_plugin(self, plugin_name: str) -> str:
        """Attempts to load the given plugin from the plugins directory.

        The plugin must reside in a class with the same name as its module within the plugins directory.
        If the plugin is already in the namespace, we will reload the module. Otherwise, we load it fresh.

        :param plugin_name: Name of the plugin to load
        :return: Server response
        """
        current_dir = os.path.dirname(os.path.realpath(__file__))
        if not os.path.isfile("{}/{}.py".format(current_dir, plugin_name)):
            return "Plugin {} DNE".format(plugin_name)

        # First, let's see if this is already imported
        module_name = "plugins.{}".format(plugin_name)
        if module_name in sys.modules:
            self.cli_unload_plugin(plugin_name)
            mod = sys.modules[module_name]
            importlib.reload(mod)
            self.register_plugin(self.get_class(mod, plugin_name))
            return "RELOADED {}".format(plugin_name)

        importlib.invalidate_caches()
        mod = importlib.import_module(module_name)
        self.register_plugin(self.get_class(mod, plugin_name))
        return "LOADED {}".format(plugin_name)

    def cli_list_plugins(self) -> str:
        """Returns a list of loaded plugins"""
        resp = ""
        for name in sorted(self.name_to_plugin_class):
            enabled = self.name_to_enabled[name]
            process = self.name_to_process[name] if name in self.name_to_process else "N/A"
            process_pid = process.pid if process != "N/A" else "N/A"
            exit_event = self.name_to_exit_event[name].is_set() if name in self.name_to_exit_event else "N/A"

            resp += "name:{} enabled:{} process:{} pid:{} exit_event:{}\n".format(name, enabled, process, process_pid,
                                                                                   exit_event)

        return resp

    def cli_start_plugin(self, plugin_name: str) -> str:
        """Starts the given plugin if loaded and enabled

        :param plugin_name: Name of the plugin to start
        :return: Server response
        """
        if plugin_name not in self.name_to_plugin_class:
            return "Plugin {} DNE".format(plugin_name)

        if not self.name_to_enabled[plugin_name]:
            return "Plugin {} is not enabled".format(plugin_name)

        self.run_plugin(plugin_name)
        return "OK"

    def cli_stop_plugin(self, plugin_name: str) -> str:
        """Stops the given plugin

        :param plugin_name: Name of the plugin to stop
        :return: Server response
        """
        if plugin_name not in self.name_to_plugin_class:
            return "Plugin {} DNE".format(plugin_name)

        self.zmq_pub_socket.send_multipart((plugin_name.encode(), b"EXIT"))
        if plugin_name in self.name_to_exit_event:
            self.name_to_exit_event[plugin_name].set()

        return "OK"

    def cli_restart_plugin(self, plugin_name: str) -> str:
        """Restarts the given plugin

        :param plugin_name: Name of the plugin to restart
        :return: Server response
        """
        resp = self.cli_stop_plugin(plugin_name)
        if resp != "OK":
            return resp
        resp = self.cli_start_plugin(plugin_name)
        if resp != "OK":
            return resp

        return "OK"

    def cli_unload_plugin(self, plugin_name: str) -> str:
        """Unload the given plugin

        :param plugin_name: Plugin name to unload
        :return: Server response
        """
        if plugin_name not in self.name_to_plugin_class:
            return "Plugin {} DNE".format(plugin_name)

        if plugin_name in self.name_to_plugin_class:
            self.name_to_plugin_class.pop(plugin_name)

        if plugin_name in self.name_to_enabled:
            self.name_to_enabled.pop(plugin_name)

        if plugin_name in self.name_to_process:
            self.name_to_process.pop(plugin_name)

        if plugin_name in self.name_to_exit_event:
            self.name_to_exit_event.pop(plugin_name)

        return "OK"


def run_cli(config: typing.Dict):
    """Starts the REPL and sends commands to the plugin manager over TCP using ZMQ

    :param config: Configuration dictionary
    """
    zmq_context = zmq.Context()
    zmq_request_socket = zmq_context.socket(zmq.REQ)
    zmq_request_socket.connect(config["zmq.mauka.plugin.management.req.interface"])
    prompt = "opq-mauka> "
    cmd = input(prompt)
    while cmd != "exit":
        zmq_request_socket.send_string(cmd)
        print(zmq_request_socket.recv_string())
        cmd = input(prompt)


def load_config(path: str) -> typing.Dict:
    """Loads a configuration file from the file system

    :param path: Path of configuration file
    :return: Configuration dictionary
    """
    _logger.info("Loading configuration from {}".format(path))
    try:
        with open(path, "r") as f:
            return json.load(f)
    except FileNotFoundError as e:
        _logger.error(e)
        _logger.error("usage: python3 -m plugins.manager config.json")
        exit(0)


if __name__ == "__main__":
    """Entry point to plugin manager repl/cli"""
    _logger.info("Starting OpqMauka CLI")
    if len(sys.argv) <= 1:
        _logger.error("Configuration file not supplied")
        _logger.error("usage: python3 -m plugins.manager config.json")
        exit(0)

    config_path = sys.argv[1]
    config = load_config(config_path)
    run_cli(config)
