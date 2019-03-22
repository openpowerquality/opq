import multiprocessing
import time

import config
import plugins.base_plugin as base_plugin
import protobuf.util as util_pb2
import protobuf.mauka_pb2 as mauka_pb2


def timestamp_s() -> int:
    return int(round(time.time()))


class LahaGcPlugin(base_plugin.MaukaPlugin):
    NAME = "LahaGcPlugin"

    def __init__(self,
                 conf: config.MaukaConfig,
                 exit_event: multiprocessing.Event):
        super().__init__(conf, ["laha_gc"], LahaGcPlugin.NAME, exit_event)

    def handle_gc_trigger_measurements(self):
        self.debug("gc_trigger measurements")
        now = timestamp_s()
        delete_result = self.mongo_client.measurements_collection.delete_many({"expires_at": {"$lt": now}})
        self.debug("Garbage collected %d measurements" % delete_result.deleted_count)

    def handle_gc_trigger_trends(self):
        self.debug("gc_trigger trends")
        now = timestamp_s()
        delete_result = self.mongo_client.trends_collection.delete_many({"expires_at": {"$lt": now}})
        self.debug("Garbage collected %d trends" % delete_result.deleted_count)

    def handle_gc_trigger_events(self):
        self.debug("gc_trigger events")
        now = timestamp_s()
        events = self.mongo_client.events_collection.find({"expires_at": {"$lt": now}}
                                                          )
        # Find corresponding box events

        # Cleanup gridfs files for each box event

        # Cleanup box events

        # Cleanup events
        delete_result = self.mongo_client.events_collection.delete_many({"expires_at": {"$lt": now}})
        self.debug("Garbage collected %d events" % delete_result.deleted_count)


    def handle_gc_trigger_incidents(self):
        self.debug("gc_trigger incidents")
        now = timestamp_s()
        delete_result = self.mongo_client.incidents_collection.delete_many({"expires_at": {"$lt": now}})
        self.debug("Garbage collected %d incidents" % delete_result.deleted_count)

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

    def handle_gc_from_phenomena(self, _id: str):
        self.debug("gc_update phenomena")
        pass

    def handle_gc_from_incident(self, _id: str):
        self.debug("gc_update incidents")
        pass

    def handle_gc_from_event(self, _id: str):
        self.debug("gc_from event")
        pass

    def handle_gc_from_trend(self, _id: str):
        self.debug("gc_update trends")
        pass

    def handle_gc_from_measurement(self, _id: str):
        self.debug("gc_update measurements")
        pass

    def handle_gc_update(self, gc_update: mauka_pb2.GcUpdate):
        if gc_update.from_domain == mauka_pb2.PHENOMENA:
            self.handle_gc_from_phenomena(gc_update.id)
        elif gc_update.from_domain == mauka_pb2.INCIDENTS:
            self.handle_gc_from_incident(gc_update.id)
        elif gc_update.from_domain == mauka_pb2.EVENTS:
            self.handle_gc_from_event(gc_update.id)
        elif gc_update.from_domain == mauka_pb2.TRENDS:
            self.handle_gc_from_trend(gc_update.id)
        elif gc_update.from_domain == mauka_pb2.MEASUREMENTS:
            self.handle_gc_from_measurement(gc_update.id)
        else:
            pass

    def on_message(self, topic: str, mauka_message: mauka_pb2.MaukaMessage):
        self.debug("Received from %s" % mauka_message.source)
        if util_pb2.is_gc_trigger(mauka_message):
            self.handle_gc_trigger(mauka_message.laha.gc_trigger)
        elif util_pb2.is_gc_update(mauka_message):
            self.handle_gc_update(mauka_message.gc_update)
        else:
            self.logger.error("Received incorrect type of MaukaMessage")
