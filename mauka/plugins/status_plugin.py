"""
This module contains a plugin that reports and records the status of other plugins in the system

OPQ Health requires a JSON response that has the format of:

component = {
    "name": str,
    "ok": bool,
    "timestamp": int,
    "subcomponents": list[component]
}

"""

import http.server
import multiprocessing
import threading
import time
import typing

import config
import plugins.base_plugin
import protobuf.util


def fmt_list(l: typing.List) -> str:
    """
    Formats a list suitable for json.
    :param l: List to format.
    :return: A formatted list suitable for json.
    """
    return "[%s]" % ", ".join(l)


def fmt_bool(b: bool) -> str:
    """
    Formats a bool suitable for json.
    :param b: Bool to format.
    :return: A formatted bool suitable for json.
    """
    return str(b).lower()


def fmt_str(s: str) -> str:
    """
    Formats a str suitable for json.
    :param s: String to format.
    :return: A formatted string suitable for json.
    """
    return '"%s"' % s


def timestamp_s() -> int:
    """
    Returns a timestamp as the number of seconds since the epoch.
    :return: A timestamp as the number of seconds since the epoch.
    """
    return int(time.time())


class StateComponent:
    """
    This class provides encapsulates the data required by OPQ Health.
    """
    def __init__(self,
                 name: str,
                 ok: bool = True,
                 timestamp: int = timestamp_s()):
        self.name: str = name
        self.ok: bool = ok
        self.timestamp = timestamp
        self.subcomponents: typing.List['StateComponent'] = []

    def update(self, ok: bool = True):
        """
        Updates the state component with the latest timestamp and status.
        :param ok: An optional status (ok = True otherwise).
        """
        self.ok = ok
        self.timestamp = timestamp_s()

    def as_json(self) -> bytes:
        """
        Returns the recursive JSON representation of this object to feed to OPQ Health.
        :return: The recursive JSON representation of this object to feed to OPQ Health.
        """
        def as_json_rec(state_component: 'StateComponent') -> str:
            """
            Recursive helper method for building JSON.
            :param state_component: The state component to serialize.
            :return: JSON representation of the state component.
            """
            if len(state_component.subcomponents) == 0:
                return '{"name": %s, "ok": %s, "timestamp": %d, "subcomponents": []}' % (
                    fmt_str(state_component.name),
                    fmt_bool(state_component.ok),
                    state_component.timestamp)

            return '{"name": %s, "ok": %s, "timestamp": %d, "subcomponents": %s}' % (
                fmt_str(state_component.name),
                fmt_bool(state_component.ok),
                state_component.timestamp,
                fmt_list(list(map(as_json_rec, state_component.subcomponents))))

        return as_json_rec(self).encode()


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
            return self.state.as_json()

    def update(self, name: str, ok: bool = True):
        """
        Updates the health for a plugin at name.
        :param name: Name of the plugin.
        :param ok: Plugin status.
        """

        def subcomponent(name: str) -> typing.Optional[StateComponent]:
            """
            Returns a subcomponent in the first level of the state subcomponents.
            :param name: Name of the plugin subcomponent.
            :return: The subcomponent or None if it doesn't exist.
            """
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
