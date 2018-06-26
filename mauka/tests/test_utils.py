import signal
import sys
import threading
import typing

import plugins.base
import services


class MaukaService:
    def __init__(self, config: typing.Dict, plugins: typing.List[plugins.base.MaukaPlugin]):
        self.config = config
        self.plugins = plugins
        self.plugin_manager = services.PluginManager(config)
        self.broker_process = None
        self.makai_bridge_process = None
        self.makai_event_bridge_process = None
        self.plugin_manager_thread = None

        # start-stop-daemon sends a SIGTERM, we need to handle it to gracefully shutdown mauka
        def sigterm_handler_fn(signum, frame):
            # _logger.info("Received exit signal")
            self.stop_mauka_service()

        self.sigterm_handler = sigterm_handler_fn
        signal.signal(signal.SIGTERM, self.sigterm_handler)
        signal.signal(signal.SIGINT, self.sigterm_handler)

    def start_mauka_service(self):
        for plugin in self.plugins:
            self.plugin_manager.register_plugin(plugin)
        self.broker_process = services.start_mauka_pub_sub_broker(self.config)
        self.makai_bridge_process = services.start_makai_bridge(self.config)
        self.makai_event_bridge_process = services.start_makai_event_bridge(self.config)

        try:
            self.plugin_manager.run_all_plugins()
            self.plugin_manager_thread = self.plugin_manager.start_tcp_server(blocking=False)
        except KeyboardInterrupt:
            self.sigterm_handler(None, None)

    def stop_mauka_service(self):
        self.plugin_manager.exit()

        if self.broker_process is not None:
            self.broker_process.terminate()

        if self.makai_bridge_process is not None:
            self.makai_bridge_process.terminate()

        if self.makai_event_bridge_process is not None:
            self.makai_event_bridge_process.terminate()

        if self.plugin_manager_thread is not None:
            self.plugin_manager_thread.terminate()




def setup_mauka(config: typing.Dict, plugins: typing.List[plugins.base.MaukaPlugin]):
    """Setup a running, testable, mock version of Mauka."""
    mauka_service = MaukaService(config, plugins)
    mauka_service.start_mauka_service()
    return mauka_service


def tear_down_mauka(mauka_service: MaukaService):
    mauka_service.stop_mauka_service()

