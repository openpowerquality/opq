import multiprocessing

import config
import plugins.base_plugin as base_plugin
import protobuf.util as util_pb2
import protobuf.mauka_pb2 as mauka_pb2


class LahaGcPlugin(base_plugin.MaukaPlugin):
    NAME = "LahaGcPlugin"

    def __init__(self,
                 conf: config.MaukaConfig,
                 exit_event: multiprocessing.Event):
        super().__init__(conf, ["laha_gc"], LahaGcPlugin.NAME, exit_event)

    def handle_gc_trigger_measurements(self):
        self.debug("gc_trigger measurements")
    

    def handle_gc_trigger_trends(self):
        self.debug("gc_trigger trends")
        pass

    def handle_gc_trigger_events(self):
        self.debug("gc_trigger events")
        pass

    def handle_gc_trigger_incidents(self):
        self.debug("gc_trigger incidents")
        pass

    def handle_gc_trigger_phenomena(self):
        self.debug("gc_trigger phenomena")
        pass

    def handle_gc_trigger(self, gc_trigger: mauka_pb2.GcTrigger):
        self.debug("Handling gc_trigger %s" % str(gc_trigger))
        domains = set(gc_trigger.gc_domains)

        if mauka_pb2.MEASUREMENTS in domains:
            self.handle_gc_trigger_measurements()

        if mauka_pb2.TRENDS in domains:
            self.handle_gc_trigger_trends()

        if mauka_pb2.EVENTS in domains:
            self.handle_gc_trigger_events()

        if mauka_pb2.INCIDENTS in domains:
            self.handle_gc_trigger_incidents()

        if mauka_pb2.PHENOMENA in domains:
            self.handle_gc_trigger_phenomena()

    def handle_gc_update(self, gc_update: mauka_pb2.GcUpdate):
        pass

    def on_message(self, topic: str, mauka_message: mauka_pb2.MaukaMessage):
        self.debug("Received from %s" % mauka_message.source)

        if util_pb2.is_gc_trigger(mauka_message):
            self.handle_gc_trigger(mauka_message.laha.gc_trigger)
        elif util_pb2.is_gc_update(mauka_message):
            pass
        else:
            self.logger.error("Received incorrect type of MaukaMessage")
