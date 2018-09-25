import multiprocessing
import typing

import protobuf.mauka_pb2
from plugins.base_plugin import MaukaPlugin


class OutagePlugin(MaukaPlugin):
    NAME="OutagePlugin"
    def __init__(self, config: typing.Dict,
                 exit_event: multiprocessing.Event):
        super().__init__(config, [], OutagePlugin.NAME, exit_event)

    def on_message(self, topic: str, mauka_message: protobuf.mauka_pb2.MaukaMessage):
        pass