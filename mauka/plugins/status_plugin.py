"""
This module contains a plugin that reports and records the status of other plugins in the system
"""

import json
import http.server
import multiprocessing
import threading
import time
import typing

import plugins.base_plugin
import protobuf.util


class HealthState:
    """Thread safe class for passing plugin state to HTTP server"""

    def __init__(self):
        self.lock = threading.RLock()
        self.state = {}

    def as_json(self) -> bytes:
        """
        :return: Thread safe method that returns the current state as encoded bytes.
        """
        with self.lock:
            return json.dumps(self.state).encode()

    def set_key(self, key, value):
        """
        Thread safe message for setting a key-pair value within this class.
        :param key: The key to set.
        :param value: The value to set.
        """
        with self.lock:
            self.state[key] = value


# pylint: disable=C0103
health_state = HealthState()


def request_handler_factory():
    """
    Factory method for creating HTTP request handler.
    :return:
    """
    class HealthRequestHandler(http.server.BaseHTTPRequestHandler):
        """
        Custom HTTP handler for Mauka's health requests.
        """

        def _set_headers(self, resp: int):
            """
            Custom heaser setting method.
            :param resp:  The response type.
            """
            self.send_response(resp)
            self.send_header('Content-type', 'application/json')
            self.end_headers()

        # noinspection PyPep8Naming
        # pylint: disable=C0103
        def do_GET(self):
            """
            Returns the health state as JSON to the requestee.
            :return: The health state as JSON
            """
            # pylint: disable=W0603
            global health_state
            self._set_headers(200)
            self.wfile.write(health_state.as_json())

    return HealthRequestHandler


def start_health_sate_httpd_server(port: int):
    """Helper function to start HTTP server in separate thread"""
    httpd = http.server.HTTPServer(("", port), request_handler_factory())
    httpd.serve_forever()


class StatusPlugin(plugins.base_plugin.MaukaPlugin):
    """
    This module contains a plugin that reports and records the status of other plugins in the system
    """

    NAME = "StatusPlugin"

    def __init__(self, config: typing.Dict, exit_event: multiprocessing.Event):
        """ Initializes this plugin

        :param config: Configuration dictionary
        """
        super().__init__(config, ["heartbeat"], StatusPlugin.NAME, exit_event)
        health_porth = int(config["plugins.StatusPlugin.port"])
        self.httpd_thread = threading.Thread(target=start_health_sate_httpd_server, args=(health_porth,))
        self.httpd_thread.start()

    def on_message(self, topic, mauka_message):
        # pylint: disable=W0603
        global health_state
        """Subscribed messages occur async

        Messages are printed to stdout

        :param topic: The topic that this message is associated with
        :param message: The message
        """

        if protobuf.util.is_heartbeat_message(mauka_message):
            self.debug(str(mauka_message))
            health_state.set_key(mauka_message.source, time.time())
        else:
            self.logger.error("Incorrect mauka message type [%s] for StatusPlugin",
                              protobuf.util.which_message_oneof(mauka_message))
