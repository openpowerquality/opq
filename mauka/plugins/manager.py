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
    def __init__(self, config: typing.Dict):
        self.config = config
        self.name_to_plugin_class = {}

        self.name_to_process = {}
        self.name_to_exit_event = {}
        self.name_to_enabled = {}

        self.zmq_context = zmq.Context()
        self.zmq_pub_socket = self.zmq_context.socket(zmq.PUB)
        self.zmq_pub_socket.connect(self.config["zmq.mauka.plugin.pub.interface"])

    def register_plugin(self, plugin_class, enabled: bool = True):
        name = plugin_class.NAME
        self.name_to_plugin_class[name] = plugin_class
        self.name_to_enabled[name] = enabled

    def run_plugin(self, plugin_name: str):
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

    def cli_help(self) -> str:
        return """
            disable [pluginName]
                Disables the named plugin.
            
            enable [pluginName]
                Enables the named plugin.
                
            exit
                Exits the opq-mauka cli.
                
            help
                Displays this message.
                
            load [pluginName]
                Loads the named plugin from disk. 
                Note: The plugin should be in the plugins directory.
                Note: The plugin module and class must be the same name.
                
            ls
                Display status of all loaded plugins.
                
            start [pluginName]
                Start the named plugin.
                
            stop [pluginName]
                Stop the named plugin.
                
            unload [pluginName]
                Unload the named plugin.
            """

    def cli_ls(self) -> str:
        resp = ""
        for name in sorted(self.name_to_plugin_class):
            enabled = self.name_to_enabled[name]
            process = self.name_to_process[name] if name in self.name_to_process else "N/A"
            process_pid = process.pid if process != "N/A" else "N/A"
            exit_event = self.name_to_exit_event[name].is_set() if name in self.name_to_exit_event else "N/A"

            resp += "name: {} enabled: {} process: {}[{}] exit_event: {}\n".format(name, enabled, process, process_pid,
                                                                                   exit_event)

        return resp

    def cli_start(self, plugin_name: str) -> str:
        if plugin_name not in self.name_to_plugin_class:
            return "Plugin {} DNE".format(plugin_name)

        if not self.name_to_enabled[plugin_name]:
            return "Plugin {} is not enabled".format(plugin_name)

        self.run_plugin(plugin_name)
        return "OK"

    def cli_stop(self, plugin_name: str) -> str:
        if plugin_name not in self.name_to_plugin_class:
            return "Plugin {} DNE".format(plugin_name)

        self.zmq_pub_socket.send_multipart((plugin_name.encode(), b"EXIT"))
        if plugin_name in self.name_to_exit_event:
            self.name_to_exit_event[plugin_name].set()

        return "OK"

    def cli_enable(self, plugin_name: str) -> str:
        if plugin_name not in self.name_to_plugin_class:
            return "Plugin {} DNE".format(plugin_name)

        self.name_to_enabled[plugin_name] = True
        return "OK"

    def cli_disable(self, plugin_name: str) -> str:
        if plugin_name not in self.name_to_plugin_class:
            return "Plugin {} DNE".format(plugin_name)

        self.name_to_enabled[plugin_name] = False
        return "OK"
    
    def get_class(self, mod, class_name: str):
        for name_val in inspect.getmembers(mod, inspect.isclass):
            name = name_val[0]
            val = name_val[1]
            if name == class_name:
                return val
            return None

    def cli_load(self, plugin_name: str) -> str:
        current_dir = os.path.dirname(os.path.realpath(__file__))
        if not os.path.isfile("{}/{}.py".format(current_dir, plugin_name)):
            return "Plugin {} DNE".format(plugin_name)

        # First, let's see if this is already imported
        module_name = "plugins.{}".format(plugin_name)
        if module_name in sys.modules:
            self.cli_unload(plugin_name)
            mod = sys.modules[module_name]
            importlib.reload(mod)
            self.register_plugin(self.get_class(mod, plugin_name))
            return "RELOADED {}".format(plugin_name)

        importlib.invalidate_caches()
        mod = importlib.import_module(module_name)
        self.register_plugin(self.get_class(mod, plugin_name))
        return "LOADED {}".format(plugin_name)


    def cli_unload(self, plugin_name: str) -> str:
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

    def run_all_plugins(self):
        _logger.info("Starting all plugins")
        for name in self.name_to_plugin_class:
            if self.name_to_enabled[name]:
                self.run_plugin(name)

    def handle_tcp_request(self, request: str) -> str:
        if request.startswith("disable"):
            plugin_name = request.split(" ")[1]
            return self.cli_disable(plugin_name)
        elif request.startswith("enable"):
            plugin_name = request.split(" ")[1]
            return self.cli_enable(plugin_name)
        elif request.startswith("load"):
            plugin_name = request.split(" ")[1]
            return self.cli_load(plugin_name)
        elif request == "ls":
            return self.cli_ls()
        elif request == "help":
            return self.cli_help()
        elif request.startswith("start"):
            plugin_name = request.strip().split(" ")[1]
            return self.cli_start(plugin_name)
        elif request.startswith("stop"):
            plugin_name = request.strip().split(" ")[1]
            return self.cli_stop(plugin_name)
        elif request.startswith("unload"):
            plugin_name = request.split(" ")[1]
            return self.cli_unload(plugin_name)
        else:
            return "Unknown cmd {}".format(request)

    def start_tcp_server(self):
        _logger.info("Starting plugin manager TCP server")
        zmq_context = zmq.Context()
        zmq_reply_socket = zmq_context.socket(zmq.REP)
        zmq_reply_socket.bind(self.config["zmq.mauka.plugin.management.rep.interface"])

        while True:
            request = zmq_reply_socket.recv_string()
            zmq_reply_socket.send_string(self.handle_tcp_request(request))


def run_cli(config: typing.Dict):
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
    _logger.info("Starting OpqMauka CLI")
    if len(sys.argv) <= 1:
        _logger.error("Configuration file not supplied")
        _logger.error("usage: python3 -m plugins.manager config.json")
        exit(0)

    config_path = sys.argv[1]
    config = load_config(config_path)
    run_cli(config)
