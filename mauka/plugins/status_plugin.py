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

import enum
import http.server
import json
import multiprocessing
import threading
import time
import typing

import config
import plugins.base_plugin
import protobuf.pb_util
import protobuf.mauka_pb2 as mauka_pb2


def fmt_list(values: typing.List) -> str:
    """
    Formats a list suitable for json.
    :param l: List to format.
    :return: A formatted list suitable for json.
    """
    return "[%s]" % ", ".join(values)


def fmt_bool(boolean: bool) -> str:
    """
    Formats a bool suitable for json.
    :param b: Bool to format.
    :return: A formatted bool suitable for json.
    """
    return str(boolean).lower()


def fmt_str(string: str) -> str:
    """
    Formats a str suitable for json.
    :param s: String to format.
    :return: A formatted string suitable for json.
    """
    return '"%s"' % string


def timestamp_s() -> int:
    """
    Returns a timestamp as the number of seconds since the epoch.
    :return: A timestamp as the number of seconds since the epoch.
    """
    return int(time.time())


class StateComponent:
    """
    This class encapsulates the data required by OPQ Health.
    """

    def __init__(self,
                 name: str,
                 ok: bool = True,
                 timestamp: int = timestamp_s()):
        self.name: str = name
        # pylint: disable=C0103
        self.ok: bool = ok
        self.timestamp = timestamp
        self.subcomponents: typing.List['StateComponent'] = []

    # pylint: disable=C0103
    def update(self, ok: bool = True):
        """
        Updates the state component with the latest timestamp and status.
        :param ok: An optional status (ok = True otherwise).
        """
        # pylint: disable=C0103
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
                    timestamp_s())

            return '{"name": %s, "ok": %s, "timestamp": %d, "subcomponents": %s}' % (
                fmt_str(state_component.name),
                fmt_bool(state_component.ok),
                timestamp_s(),
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

    # pylint: disable=C0103
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

    def __str__(self):
        return self.as_json().decode()


# pylint: disable=C0103
health_state: HealthState = HealthState()


class PluginState(enum.Enum):
    """
    Enumeration of possible plugin states.
    """
    IDLE = "IDLE"
    BUSY = "BUSY"


class PluginStatus:
    """
    This class tracks the status of each Mauka plugin.
    """

    def __init__(self, mauka_message: mauka_pb2.MaukaMessage):
        self.plugin_name = mauka_message.source
        self.messages_recv = mauka_message.heartbeat.on_message_count
        self.bytes_recv = 0
        self.last_recv = mauka_message.heartbeat.last_received_timestamp_ms
        self.plugin_state = mauka_message.heartbeat.plugin_state

    def as_json(self):
        """
        :return: A JSON serialized instance of this class.
        """
        return json.dumps(self.as_dict())

    def as_dict(self) -> typing.Dict:
        """
        :return: Attributes of this class as a dictionary.
        """
        return {
            "plugin_name": self.plugin_name,
            "messages_recv": self.messages_recv,
            "bytes_recv": self.bytes_recv,
            "last_recv": self.last_recv,
            "plugin_state": self.plugin_state
        }

    def update(self, mauka_message: mauka_pb2.MaukaMessage):
        """
        Updates this plugin's status.
        :param mauka_message: Mauka message with status metrics.
        """
        self.messages_recv = mauka_message.heartbeat.on_message_count
        self.bytes_recv = 0
        self.last_recv = mauka_message.heartbeat.last_received_timestamp_ms
        self.plugin_state = mauka_message.heartbeat.plugin_state


class PluginStatuses:
    """
    This class encapsulates the status of all plugins.
    """

    def __init__(self):
        self.plugin_name_to_plugin_status: typing.Dict[str, PluginStatus] = {}
        self.lock = threading.RLock()

    def update(self, mauka_message: mauka_pb2.MaukaMessage):
        """
        Updates the plugin status.
        :param mauka_message: Mauka message to get metrics from.
        """
        with self.lock:
            plugin_name = mauka_message.source
            if plugin_name not in self.plugin_name_to_plugin_status:
                self.plugin_name_to_plugin_status[plugin_name] = PluginStatus(mauka_message)
            else:
                self.plugin_name_to_plugin_status[plugin_name].update(mauka_message)

    def as_json(self) -> str:
        """
        :return: PluginStatuses serialized as JSON.
        """
        statuses = list(map(PluginStatus.as_dict, self.plugin_name_to_plugin_status.values()))
        j = json.dumps(statuses)
        return j.encode()


# pylint: disable=C0103
plugin_statuses: PluginStatuses = PluginStatuses()


class HealthRequestHandler(http.server.BaseHTTPRequestHandler):
    """
    Custom HTTP handler for Mauka's health requests.
    """

    # pylint: disable=W0603
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
        if self.path == "/status":
            global plugin_statuses
            self._set_headers(200)
            self.wfile.write(plugin_statuses.as_json())
        else:
            global health_state
            self._set_headers(200)
            self.wfile.write(health_state.as_json())

    # pylint: disable=W0622
    def log_message(self, format, *args):
        """
        This overrides the default HTTP logging so it doesn't produce a log message everytime health the server is
        queried.
        :param format: Format.
        :param args: Args.
        :return: Nothing
        """
        return


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
        # pylint: disable=W0603
        global plugin_statuses
        """Subscribed messages occur async

        Messages are printed to stdout

        :param topic: The topic that this message is associated with
        :param message: The message
        """

        if protobuf.pb_util.is_heartbeat_message(mauka_message):
            health_state.update(mauka_message.source)
            plugin_statuses.update(mauka_message)
            self.debug(str(mauka_message))
        else:
            self.logger.error("Incorrect mauka message type [%s] for StatusPlugin",
                              protobuf.pb_util.which_message_oneof(mauka_message))
