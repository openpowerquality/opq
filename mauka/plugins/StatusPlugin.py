"""
This module contains a plugin that reports and records the status of other plugins in the system
"""

import json
import http.server
import multiprocessing
import threading
import time
import typing

import plugins.base
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

    def set_key(self, k, v):
        """
        Thread safe message for setting a key-pair value within this class.
        :param k: The key to set.
        :param v: The value to set.
        """
        with self.lock:
            self.state[k] = v


health_state = HealthState()


def mauka_health_request_handler_factory():
    """
    Factory method for creating HTTP request handler.
    :return:
    """
    class HealthRequestHandler(http.server.BaseHTTPRequestHandler):
        """
        Custom HTTP handler for Mauka's health requests.
        """

        def __init__(self, request, client_address, server):
            super().__init__(request, client_address, server)

        def _set_headers(self, resp: int):
            """
            Custom heaser setting method.
            :param resp:  The response type.
            """
            self.send_response(resp)
            self.send_header('Content-type', 'application/json')
            self.end_headers()

        # noinspection PyPep8Naming
        def do_GET(self):
            """
            Returns the health state as JSON to the requestee.
            :return: The health state as JSON
            """
            global health_state
            self._set_headers(200)
            self.wfile.write(health_state.as_json())

    return HealthRequestHandler


def start_health_sate_httpd_server(port: int):
    """Helper function to start HTTP server in separate thread"""
    httpd = http.server.HTTPServer(("", port), mauka_health_request_handler_factory())
    httpd.serve_forever()


class StatusPlugin(plugins.base.MaukaPlugin):
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
            self.logger.error("Incorrect mauka message type [{}] for StatusPlugin".format(
                protobuf.util.which_message_oneof(mauka_message)
            ))
