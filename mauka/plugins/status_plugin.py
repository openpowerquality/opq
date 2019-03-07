"""
This module contains a plugin that reports and records the status of other plugins in the system
"""

import json
import http.server
import multiprocessing
import threading
import time
import typing

import config
import plugins.base_plugin
import protobuf.util


def timestamp_s() -> int:
    return int(time.time())


class StateComponent(object):
    def __init__(self,
                 name: str,
                 ok: bool = True,
                 timestamp: int = timestamp_s(),
                 subcomponents: typing.List['StateComponent'] = []):
        self.name: str = name
        self.ok: bool = ok
        self.timestamp = timestamp
        self.subcomponents: typing.List['StateComponent'] = subcomponents

    def update(self, ok: bool = True) -> 'StateComponent':
        self.ok = ok
        self.timestamp = timestamp_s()
        return self

    def as_dict(self) -> typing.Dict:
        subcomponents = []
        for component in self.subcomponents:
            subcomponents.append({
                "name": component.name,
                "ok": component.ok,
                "timestamp": component.timestamp,
                "subcomponents": []
            })
        return {
            "name": self.name,
            "ok": self.ok,
            "timestamp": self.timestamp,
            "subcomponents": subcomponents
        }


class HealthState:
    """Thread safe class for passing plugin state to HTTP server"""

    def __init__(self):
        self.lock = threading.RLock()
        self.state = StateComponent("mauka")

    def as_json(self) -> bytes:
        """
        :return: Thread safe method that returns the current state as encoded bytes.
        """
        with self.lock:
            return json.dumps(self.state.as_dict())

    def update(self, name: str, ok: bool = True):
        def subcomponent(name: str) -> typing.Optional[StateComponent]:
            with self.lock:
                for comp in self.state.subcomponents:
                    if comp.name == name:
                        return comp

                return None

        with self.lock:
            self.state.update()
            component = subcomponent(name)
            if component is not None:
                component.update(ok)
            else:
                self.state.subcomponents.append(StateComponent(name, ok))

    def __str__(self):
        return self.as_json()


# pylint: disable=C0103
health_state: HealthState = HealthState()


class HealthRequestHandler(http.server.BaseHTTPRequestHandler):
    """
    Custom HTTP handler for Mauka's health requests.
    """

    def _set_headers(self, resp: int):
        """
        Custom header setting method.
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


def start_health_sate_httpd_server(port: int):
    """Helper function to start HTTP server in separate thread"""
    httpd = http.server.HTTPServer(("", port), HealthRequestHandler)
    httpd.serve_forever()


class StatusPlugin(plugins.base_plugin.MaukaPlugin):
    """
    This module contains a plugin that reports and records the status of other plugins in the system
    """

    NAME = "StatusPlugin"

    def __init__(self, conf: config.MaukaConfig, exit_event: multiprocessing.Event):
        """ Initializes this plugin

        :param conf: Configuration dictionary
        """
        super().__init__(conf, ["heartbeat"], StatusPlugin.NAME, exit_event)
        health_port = int(conf.get("plugins.StatusPlugin.port"))
        self.httpd_thread = threading.Thread(target=start_health_sate_httpd_server, args=(health_port,))
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
            health_state.update(mauka_message.source)
            self.debug(str(mauka_message))
            self.debug(str(health_state))
        else:
            self.logger.error("Incorrect mauka message type [%s] for StatusPlugin",
                              protobuf.util.which_message_oneof(mauka_message))


if __name__ == "__main__":
    health_state = HealthState()
    print(health_state.as_json())
    health_state.update("foo")
    print(health_state.as_json())
