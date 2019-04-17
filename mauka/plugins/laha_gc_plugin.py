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
        super().__init__(conf, ["laha_gc", "heartbeat"], LahaGcPlugin.NAME, exit_event)

    def handle_gc_trigger_measurements(self):
        self.debug("gc_trigger measurements")
        now = timestamp_s()
        delete_result = self.mongo_client.measurements_collection.delete_many({"expire_at": {"$lt": now}})
        self.produce("gc_stat", util_pb2.build_gc_stat(self.NAME, mauka_pb2.MEASUREMENTS, delete_result.deleted_count))
        self.debug("Garbage collected %d measurements" % delete_result.deleted_count)

    def handle_gc_trigger_trends(self):
        self.debug("gc_trigger trends")
        now = timestamp_s()
        delete_result = self.mongo_client.trends_collection.delete_many({"expire_at": {"$lt": now}})
        self.produce("gc_stat", util_pb2.build_gc_stat(self.NAME, mauka_pb2.TRENDS, delete_result.deleted_count))
        self.debug("Garbage collected %d trends" % delete_result.deleted_count)

    def handle_gc_trigger_events(self):
        self.debug("gc_trigger events")
        now = timestamp_s()
        events = self.mongo_client.events_collection.find({"expire_at": {"$lt": now}},
                                                          projection={"_id": True,
                                                                      "expire_at": True,
                                                                      "event_id": True,
                                                                      "boxes_received": True})

        # Find corresponding box events
        box_events = []
        for event in events:
            for box_triggered in event["boxes_received"]:
                box_event = self.mongo_client.box_events_collection.find_one({"event_id": event["event_id"],
                                                                              "box_id": box_triggered},
                                                                             projection={"_id": True,
                                                                                         "event_id": True,
                                                                                         "box_id": True,
                                                                                         "data_fs_filename": True})

                if box_event is not None:
                    box_events.append(box_event)

        # Cleanup gridfs files and box_events
        for box_event in box_events:
            self.mongo_client.delete_gridfs(box_event["data_fs_filename"])
            self.mongo_client.box_events_collection.delete_one({"_id": box_event["_id"]})

        self.debug("Garbage collected %d box_events and corresponding gridfs data")

        # Cleanup events
        delete_result = self.mongo_client.events_collection.delete_many({"expire_at": {"$lt": now}})
        self.produce("gc_stat", util_pb2.build_gc_stat(self.NAME, mauka_pb2.EVENTS, delete_result.deleted_count))
        self.debug("Garbage collected %d events" % delete_result.deleted_count)

    def handle_gc_trigger_incidents(self):
        self.debug("gc_trigger incidents")
        now = timestamp_s()
        incidents = self.mongo_client.incidents_collection.find({"expire_at": {"$lt": now}},
                                                                projection={"expire_at": True,
                                                                            "gridfs_filename": True})
        filenames = list(map(lambda incident: incident["gridfs_filename"], incidents))
        for filename in filenames:
            self.mongo_client.delete_gridfs(filename)

        delete_result = self.mongo_client.incidents_collection.delete_many({"expire_at": {"$lt": now}})
        self.produce("gc_stat", util_pb2.build_gc_stat(self.NAME, mauka_pb2.INCIDENTS, delete_result.deleted_count))
        self.debug("Garbage collected %d incidents and associated gridfs data" % delete_result.deleted_count)

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

    def handle_gc_update_from_phenomena(self, _id: str):
        self.debug("gc_update phenomena")
        pass

    def handle_gc_update_from_incident(self, _id: str):
        self.debug("gc_update incidents")
        incident = self.mongo_client.incidents_collection.find_one({"incident_id": _id},
                                                                   projection={"_id": True,
                                                                               "incident_id": True,
                                                                               "event_id": True,
                                                                               "expire_at": True})
        event = self.mongo_client.events_collection.find_one({"event_id": incident["event_id"]},
                                                             projection={"_id": True,
                                                                         "event_id": True})
        self.mongo_client.events_collection.update_one({"event_id": event["event_id"]},
                                                       {"$set": {"expire_at": incident["expire_at"]}})
        self.handle_gc_update_from_event(event["event_id"])

    def handle_gc_update_from_event(self, _id: str):
        self.debug("gc_update event")
        event = self.mongo_client.events_collection.find_one({"event_id": _id},
                                                             prjection={"_id": True,
                                                                        "event_id": True,
                                                                        "expire_at": True,
                                                                        "target_event_start_timestamp_ms": True,
                                                                        "target_event_end_timestamp_ms": True})

        query = {"timestamp_ms": {"$gte": event["target_event_start_timestamp_ms"],
                                  "$lte": event["target_event_end_timestamp_ms"]}}

        update = {"$set": {"expire_at": event["expire_at"]}}

        # Update trends
        update_trends_result = self.mongo_client.trends_collection.update_many(query, update)

        # Update measurements
        update_measurements_result = self.mongo_client.measurements_collection.update_many(query, update)

        self.debug("Updated expire_at=%d for %d trends and %d measurements" % (event["expire_at"],
                                                                               update_trends_result.modified_count,
                                                                               update_measurements_result.modified_count))

    def handle_gc_update_from_trend(self, _id: str):
        self.debug("gc_update trends")
        pass

    def handle_gc_update_from_measurement(self, _id: str):
        self.debug("gc_update measurements")
        pass

    def handle_gc_update(self, gc_update: mauka_pb2.GcUpdate):
        self.debug("Handling GC update")
        if gc_update.from_domain == mauka_pb2.PHENOMENA:
            self.handle_gc_update_from_phenomena(gc_update.id)
        elif gc_update.from_domain == mauka_pb2.INCIDENTS:
            self.handle_gc_update_from_incident(gc_update.id)
        elif gc_update.from_domain == mauka_pb2.EVENTS:
            self.handle_gc_update_from_event(gc_update.id)
        elif gc_update.from_domain == mauka_pb2.TRENDS:
            self.handle_gc_update_from_trend(gc_update.id)
        elif gc_update.from_domain == mauka_pb2.MEASUREMENTS:
            self.handle_gc_update_from_measurement(gc_update.id)
        else:
            pass

    def on_message(self, topic: str, mauka_message: mauka_pb2.MaukaMessage):
        self.debug("Received from %s %s" % (mauka_message.source, mauka_message))
        if util_pb2.is_heartbeat_message(mauka_message) and mauka_message.source == self.NAME:
            self.debug("Received heartbeat, producing GC trigger message")
            # For now, GC is triggered on heartbeats
            self.produce("laha_gc", util_pb2.build_gc_trigger(self.name, [
                mauka_pb2.MEASUREMENTS,
                mauka_pb2.TRENDS
                # mauka_pb2.EVENTS,
                # mauka_pb2.INCIDENTS,
                # mauka_pb2.PHENOMENA
            ]))
        elif util_pb2.is_gc_trigger(mauka_message):
            self.debug("Received GC trigger, calling trigger handler")
            self.handle_gc_trigger(mauka_message.laha.gc_trigger)
        elif util_pb2.is_gc_update(mauka_message):
            self.debug("Received GC update, calling update handler")
            self.handle_gc_update(mauka_message.gc_update)
        else:
            self.logger.error("Received incorrect type of MaukaMessage")