"""
This module provides facilities for managing (stopping, starting, loading, reloading) plugin subprocesses.
"""
import signal

import argparse
import importlib
import inspect
import json
import logging
import multiprocessing
import os
import readline
import sys
import typing

import zmq

_logger = logging.getLogger("app")
logging.basicConfig(
    format="[%(levelname)s][%(asctime)s][{} %(filename)s:%(lineno)s - %(funcName)s() ] %(message)s".format(
        os.getpid()))
_logger.setLevel(logging.DEBUG)

OK = "OK"


def ok(msg: str = "") -> str:
    """An ok response

    :return: An ok response
    """
    return OK if len(msg) == 0 else "{}. {}".format(OK, msg)


def error(msg: str = "N/A") -> str:
    """An error response

    :param msg: An optional error message
    :return: An error response
    """
    return "ERROR. {}".format(msg)


def is_error(response: str) -> bool:
    """Is the given response an error message?

    :param response: Response to test
    :return: Whether or not response is an error or not
    """
    return "ERROR" in response


class ArgumentParseError(Exception):
    pass


class ThrowingArgumentParser(argparse.ArgumentParser):
    def error(self, message):
        raise ArgumentParseError(message)

    def print_usage(self, file=None):
        raise ArgumentParseError(self.format_usage())

    def print_help(self, file=None):
        raise ArgumentParseError(self.format_help())


class MaukaCli:
    def __init__(self):
        super().__init__()
        self.cli_parser = ThrowingArgumentParser(prog="mauka-cli", add_help=False)
        self.cli_subparsers = self.cli_parser.add_subparsers()
        self.cmd_names = []

    def add_cmd(self, name: str, help: str, cmd_fn: typing.Callable, arg: str = None, arg_help: str = None):
        self.cmd_names.append(name)
        cmd = self.cli_subparsers.add_parser(name, help=help)
        cmd.set_defaults(func=cmd_fn)
        if arg is not None:
            cmd.add_argument(arg, help=arg_help)

    def get_help(self):
        return self.cli_parser.format_help()

    def get_usage(self):
        return self.cli_parser.format_usage()

    def parse(self, args: typing.List[str]) -> str:
        try:
            args = self.cli_parser.parse_args(args)
            if len(vars(args)) == 1:
                return args.func()
            else:
                return args.func(args)
        except ArgumentParseError as e:
            return str(e)


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

        self.cli_parser = MaukaCli()

        self.zmq_pub_socket.connect(self.config["zmq.mauka.plugin.pub.interface"])
        self.init_cli()

    def init_cli(self):
        self.cli_parser.add_cmd("completions", "Return a list of completions for autocomplete",
                                self.cli_completions)

        self.cli_parser.add_cmd("disable-plugin", "Disable the named plugin",
                                self.cli_disable_plugin,
                                "plugin_name", "Name of plugin to disable")

        self.cli_parser.add_cmd("enable-plugin", "Enables the named plugin",
                                self.cli_enable_plugin,
                                "plugin_name", "Name of the plugin to enable")

        self.cli_parser.add_cmd("help", "Displays this message",
                                self.cli_parser.get_help)

        self.cli_parser.add_cmd("kill-plugin", "Kills the named plugin",
                                self.cli_kill_plugin,
                                "plugin_name", "Name of the plugin to kill")

        self.cli_parser.add_cmd("load-config", "Reloads a configuration from file",
                                self.cli_load_config,
                                "config_path", "Path of the configuration file")

        self.cli_parser.add_cmd("load-plugin", "Loads (or reloads) a plugin from disk",
                                self.cli_load_plugin,
                                "plugin_name", "Name of the plugin to load")

        self.cli_parser.add_cmd("list-plugins", "List all loaded plugins",
                                self.cli_list_plugins)

        self.cli_parser.add_cmd("start-plugin", "Start the named plugin",
                                self.cli_start_plugin,
                                "plugin_name", "Name of the plugin to start")

        self.cli_parser.add_cmd("stop-plugin", "Stop the named plugin",
                                self.cli_stop_plugin,
                                "plugin_name", "Name of the plugin to stop")

        self.cli_parser.add_cmd("stop-all-plugins", "Stop all plugins",
                                self.cli_stop_all_plugins)

        self.cli_parser.add_cmd("restart-plugin", "Restarts the named plugin",
                                self.cli_restart_plugin,
                                "plugin_name", "Name of the plugin to restart")

        self.cli_parser.add_cmd("unload-plugin", "Unloads the named plugin",
                                self.cli_unload_plugin,
                                "plugin_name", "Name of the plugin to unload")

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

            if request.strip() == "stop-tcp-server":
                zmq_reply_socket.send_string(ok("Stopping TCP server"))
                break

            zmq_reply_socket.send_string(self.handle_tcp_request(request))

        _logger.info("Stopping plugin manager TCP server")


    def handle_tcp_request(self, request: str) -> str:
        return self.cli_parser.parse(request.split(" "))

    def cli_completions(self) -> str:
        r = []
        for cmd_name in self.cli_parser.cmd_names:
            r.append(cmd_name)
        for plugin_name in self.name_to_plugin_class:
            r.append(plugin_name)

        return ",".join(r)

    def cli_disable_plugin(self, args) -> str:
        """Disables the given plugin

        :param plugin_name: Name of the plugin to disable
        :return: Server response
        """
        plugin_name = args.plugin_name
        if plugin_name not in self.name_to_plugin_class:
            return error("Plugin {} DNE".format(plugin_name))

        self.name_to_enabled[plugin_name] = False
        return ok("Plugin {} disabled".format(plugin_name))

    def cli_enable_plugin(self, args) -> str:
        """Enables the given plugin

        :param plugin_name: Name of the plugin to enable
        :return: Server response
        """
        plugin_name = args.plugin_name
        if plugin_name not in self.name_to_plugin_class:
            return error("Plugin {} DNE".format(plugin_name))

        self.name_to_enabled[plugin_name] = True
        return ok("Plugin {} enabled".format(plugin_name))

    def cli_kill_plugin(self, args) -> str:
        """Kills the named plugin

        :param plugin_name: The plugin to kill
        :return: Server response
        """

        plugin_name = args.plugin_name
        if plugin_name not in self.name_to_plugin_class:
            return error("Plugin {} DNE".format(plugin_name))

        if plugin_name not in self.name_to_process:
            return error("Plugin {} does not have associated process".format(plugin_name))

        self.name_to_process[plugin_name].terminate()
        return ok("Plugin {} killed".format(plugin_name))

    def cli_load_config(self, args) -> str:
        """Loads new configuration values

        Plugins need to be restarted to take advantage of new values

        :param config_path: Path to configuration file
        :return: Server response
        """
        config_path = args.config_path
        if not os.path.isfile(config_path):
            return error("Path {} DNE".format(config_path))

        try:
            self.config = load_config(config_path)
            return ok("Configuration loaded from {}".format(config_path))
        except Exception as e:
            return error("Exception occurred while loading config: {}".format(e))

    def cli_load_plugin(self, args) -> str:
        """Attempts to load the given plugin from the plugins directory.

        The plugin must reside in a class with the same name as its module within the plugins directory.
        If the plugin is already in the namespace, we will reload the module. Otherwise, we load it fresh.

        :param plugin_name: Name of the plugin to load
        :return: Server response
        """
        plugin_name = args.plugin_name
        current_dir = os.path.dirname(os.path.realpath(__file__))
        if not os.path.isfile("{}/{}.py".format(current_dir, plugin_name)):
            return error("Plugin {} DNE".format(plugin_name))

        # First, let's see if this is already imported
        module_name = "plugins.{}".format(plugin_name)
        if module_name in sys.modules:
            self.cli_unload_plugin(plugin_name)
            mod = sys.modules[module_name]
            importlib.reload(mod)
            self.register_plugin(self.get_class(mod, plugin_name))
            return ok("Plugin {} reloaded".format(plugin_name))

        importlib.invalidate_caches()
        mod = importlib.import_module(module_name)
        self.register_plugin(self.get_class(mod, plugin_name))
        return ok("Plugin {} loaded".format(plugin_name))

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

    def cli_start_plugin(self, args) -> str:
        """Starts the given plugin if loaded and enabled

        :param plugin_name: Name of the plugin to start
        :return: Server response
        """
        plugin_name = args.plugin_name
        if plugin_name not in self.name_to_plugin_class:
            return error("Plugin {} DNE".format(plugin_name))

        if not self.name_to_enabled[plugin_name]:
            return error("Plugin {} is not enabled".format(plugin_name))

        self.run_plugin(plugin_name)
        return ok("Plugin {} started".format(plugin_name))

    def cli_stop_plugin(self, args) -> str:
        """Stops the given plugin

        :param plugin_name: Name of the plugin to stop
        :return: Server response
        """
        plugin_name = args.plugin_name
        if plugin_name not in self.name_to_plugin_class:
            return error("Plugin {} DNE".format(plugin_name))

        self.zmq_pub_socket.send_multipart((plugin_name.encode(), b"EXIT"))
        if plugin_name in self.name_to_exit_event:
            self.name_to_exit_event[plugin_name].set()

        return ok("Plugin {} stopped".format(plugin_name))

    def cli_stop_all_plugins(self, args) -> str:
        results = []
        for name in self.name_to_plugin_class:
            results.append(self.cli_stop_plugin(name))

        return ok(str(results))

    def cli_restart_plugin(self, args) -> str:
        """Restarts the given plugin

        :param plugin_name: Name of the plugin to restart
        :return: Server response
        """
        plugin_name = args.plugin_name
        stop_resp = self.cli_stop_plugin(plugin_name)
        start_resp = self.cli_start_plugin(plugin_name)

        chained_resp = "{} {}".format(stop_resp, start_resp)

        if is_error(stop_resp) or is_error(start_resp):
            return error("{} ".format(plugin_name, chained_resp))
        else:
            return ok("Restarted {}. {}".format(plugin_name, chained_resp))

    def cli_unload_plugin(self, args) -> str:
        """Unload the given plugin

        :param plugin_name: Plugin name to unload
        :return: Server response
        """
        plugin_name = args.plugin_name
        if plugin_name not in self.name_to_plugin_class:
            return error("Plugin {} DNE".format(plugin_name))

        if plugin_name in self.name_to_plugin_class:
            self.name_to_plugin_class.pop(plugin_name)

        if plugin_name in self.name_to_enabled:
            self.name_to_enabled.pop(plugin_name)

        if plugin_name in self.name_to_process:
            self.name_to_process.pop(plugin_name)

        if plugin_name in self.name_to_exit_event:
            self.name_to_exit_event.pop(plugin_name)

        return ok("Unloaded plugin {}".format(plugin_name))

# http://eli.thegreenplace.net/2016/basics-of-using-the-readline-library/
def make_completer(vocabulary):
    def custom_complete(text, state):
        # None is returned for the end of the completion session.
        results = [x for x in vocabulary if x.startswith(text)] + [None]
        # A space is added to the completion since the Python readline doesn't
        # do this on its own. When a word is fully completed we want to mimic
        # the default readline library behavior of adding a space after it.
        return results[state] + " "
    return custom_complete

def run_cli(config: typing.Dict):
    """Starts the REPL and sends commands to the plugin manager over TCP using ZMQ

    :param config: Configuration dictionary
    """
    zmq_context = zmq.Context()
    zmq_request_socket = zmq_context.socket(zmq.REQ)
    zmq_request_socket.connect(config["zmq.mauka.plugin.management.req.interface"])
    prompt = "opq-mauka> "

    try:
        zmq_request_socket.send_string("completions")
        completions = zmq_request_socket.recv_string()
        vocabulary = set(completions.split(","))
        readline.parse_and_bind("tab: complete")
        readline.set_completer(make_completer(vocabulary))
        while True:
            cmd = input(prompt).strip()

            if cmd == "exit":
                _logger.info("Exiting mauka-cli")
                sys.exit(0)

            if cmd == "completions":
                zmq_request_socket.send_string("completions")
                completions = zmq_request_socket.recv_string()
                vocabulary = set(completions.split(","))
                readline.set_completer(make_completer(vocabulary))
                print(ok("Completions updated"))
                continue

            zmq_request_socket.send_string(cmd.strip())
            print(zmq_request_socket.recv_string())
    except (EOFError, KeyboardInterrupt) as e:
        _logger.info("Exiting mauka-cli")
        sys.exit(0)


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
