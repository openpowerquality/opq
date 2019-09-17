import unittest

import numpy as np

import protobuf.pb_util as pb_util


class PbUtilsTests(unittest.TestCase):
    def test_build_mauka_message(self):
        mauka_message = pb_util.build_mauka_message("test")
        self.assertTrue(isinstance(mauka_message, pb_util.mauka_pb2.MaukaMessage))
        self.assertEqual(mauka_message.source, "test")
        self.assertTrue(mauka_message.timestamp_ms > 0)

    def test_build_mauka_message_ts(self):
        mauka_message = pb_util.build_mauka_message("test", 1)
        self.assertEqual(mauka_message.source, "test")
        self.assertEqual(mauka_message.timestamp_ms, 1)

    def test_build_payload(self):
        mauka_message = pb_util.build_payload("test",
                                              1,
                                              "2",
                                              pb_util.mauka_pb2.ADC_SAMPLES,
                                              [1, 2, 3],
                                              5,
                                              10)
        self.assertTrue(isinstance(mauka_message, pb_util.mauka_pb2.MaukaMessage))
        self.assertTrue(pb_util.is_payload(mauka_message, pb_util.mauka_pb2.ADC_SAMPLES))
        self.assertEqual(mauka_message.source, "test")
        self.assertEqual(mauka_message.payload.event_id, 1)
        self.assertEqual(mauka_message.payload.box_id, "2")
        self.assertEqual(mauka_message.payload.payload_type, pb_util.mauka_pb2.ADC_SAMPLES)
        self.assertEqual(mauka_message.payload.data, [1, 2, 3])
        self.assertEqual(mauka_message.payload.start_timestamp_ms, 5)
        self.assertEqual(mauka_message.payload.end_timestamp_ms, 10)

    def test_build_payload_np(self):
        mauka_message = pb_util.build_payload("test",
                                              1,
                                              "2",
                                              pb_util.mauka_pb2.MEASUREMENTS,
                                              np.array([1, 2, 3]),
                                              5,
                                              10)
        self.assertTrue(isinstance(mauka_message, pb_util.mauka_pb2.MaukaMessage))
        self.assertTrue(pb_util.is_payload(mauka_message, pb_util.mauka_pb2.MEASUREMENTS))
        self.assertTrue(np.array_equal(mauka_message.payload.data, np.array([1, 2, 3])))

    def test_build_heartbeat(self):
        mauka_message = pb_util.build_heartbeat("test",
                                                1,
                                                2,
                                                "status",
                                                "state")
        self.assertTrue(isinstance(mauka_message, pb_util.mauka_pb2.MaukaMessage))
        self.assertTrue(pb_util.is_heartbeat_message(mauka_message))
        self.assertEqual(mauka_message.source, "test")
        self.assertEqual(mauka_message.heartbeat.last_received_timestamp_ms, 1)
        self.assertEqual(mauka_message.heartbeat.on_message_count, 2)
        self.assertEqual(mauka_message.heartbeat.status, "status")
        self.assertEqual(mauka_message.heartbeat.plugin_state, "state")

    def test_build_makai_event(self):
        mauka_message = pb_util.build_makai_event("test", 1)
        self.assertTrue(isinstance(mauka_message, pb_util.mauka_pb2.MaukaMessage))
        self.assertTrue(pb_util.is_makai_event_message(mauka_message))
        self.assertEqual(mauka_message.source, "test")
        self.assertEqual(mauka_message.makai_event.event_id, 1)

    def test_build_makai_trigger(self):
        mauka_message = pb_util.build_makai_trigger("test",
                                                    1,
                                                    2,
                                                    "event_type",
                                                    10.0,
                                                    "3")
        self.assertTrue(isinstance(mauka_message, pb_util.mauka_pb2.MaukaMessage))
        self.assertTrue(pb_util.is_makai_trigger(mauka_message))
        self.assertEqual(mauka_message.source, "test")
        self.assertEqual(mauka_message.makai_trigger.event_start_timestamp_ms, 1)
        self.assertEqual(mauka_message.makai_trigger.event_end_timestamp_ms, 2)
        self.assertEqual(mauka_message.makai_trigger.event_type, "event_type")
        self.assertEqual(mauka_message.makai_trigger.max_value, 10.0)
        self.assertEqual(mauka_message.makai_trigger.box_id, "3")

    def test_build_measurement(self):
        mauka_message = pb_util.build_measurement("test",
                                                  "3",
                                                  1,
                                                  60.0,
                                                  120.0,
                                                  1.0)
        self.assertTrue(isinstance(mauka_message, pb_util.mauka_pb2.MaukaMessage))
        self.assertTrue(pb_util.is_measurement(mauka_message))
        self.assertEqual(mauka_message.source, "test")
        self.assertEqual(mauka_message.measurement.box_id, "3")
        self.assertEqual(mauka_message.measurement.timestamp_ms, 1)
        self.assertEqual(mauka_message.measurement.frequency, 60.0)
        self.assertEqual(mauka_message.measurement.voltage_rms, 120.0)
        self.assertEqual(mauka_message.measurement.thd, 1.0)

    def test_build_ttl(self):
        mauka_message = pb_util.build_ttl("test",
                                          "collection",
                                          1)
        self.assertTrue(isinstance(mauka_message, pb_util.mauka_pb2.MaukaMessage))
        self.assertTrue(pb_util.is_ttl(mauka_message))
        self.assertEqual(mauka_message.source, "test")
        self.assertEqual(mauka_message.laha.ttl.collection, "collection")
        self.assertEqual(mauka_message.laha.ttl.ttl_s, 1)

    def test_build_gc_trigger_single(self):
        mauka_message = pb_util.build_gc_trigger("test",
                                                 [pb_util.mauka_pb2.TRENDS])
        self.assertTrue(isinstance(mauka_message, pb_util.mauka_pb2.MaukaMessage))
        self.assertTrue(pb_util.is_gc_trigger(mauka_message))
        self.assertEqual(mauka_message.source, "test")
        self.assertEqual(mauka_message.laha.gc_trigger.gc_domains, [pb_util.mauka_pb2.TRENDS])

    def test_build_gc_trigger_multi(self):
        mauka_message = pb_util.build_gc_trigger("test",
                                                 [pb_util.mauka_pb2.TRENDS,
                                                  pb_util.mauka_pb2.EVENTS])
        self.assertTrue(isinstance(mauka_message, pb_util.mauka_pb2.MaukaMessage))
        self.assertTrue(pb_util.is_gc_trigger(mauka_message))
        self.assertEqual(mauka_message.source, "test")
        self.assertEqual(mauka_message.laha.gc_trigger.gc_domains, [pb_util.mauka_pb2.TRENDS,
                                                                    pb_util.mauka_pb2.EVENTS])

    def test_build_gc_update(self):
        mauka_message = pb_util.build_gc_update("test",
                                                pb_util.mauka_pb2.TRENDS,
                                                1)
        self.assertTrue(isinstance(mauka_message, pb_util.mauka_pb2.MaukaMessage))
        self.assertTrue(pb_util.is_gc_update(mauka_message))
        self.assertEqual(mauka_message.source, "test")
        self.assertEqual(mauka_message.laha.gc_update.from_domain, pb_util.mauka_pb2.TRENDS)
        self.assertEqual(mauka_message.laha.gc_update.id, 1)

    def test_build_gc_stat(self):
        mauka_message = pb_util.build_gc_stat("test",
                                              pb_util.mauka_pb2.TRENDS,
                                              1)
        self.assertTrue(isinstance(mauka_message, pb_util.mauka_pb2.MaukaMessage))
        self.assertTrue(pb_util.is_gc_stat(mauka_message))
        self.assertEqual(mauka_message.source, "test")
        self.assertEqual(mauka_message.laha.gc_stat.gc_domain, pb_util.mauka_pb2.TRENDS)
        self.assertEqual(mauka_message.laha.gc_stat.gc_cnt, 1)

    def test_build_trigger_request(self):
        mauka_message = pb_util.build_trigger_request("test",
                                                      1,
                                                      2,
                                                      ["1", "2"],
                                                      3)
        self.assertTrue(isinstance(mauka_message, pb_util.mauka_pb2.MaukaMessage))
        self.assertTrue(pb_util.is_trigger_request(mauka_message))
        self.assertEqual(mauka_message.source, "test")
        self.assertEqual(mauka_message.trigger_request.start_timestamp_ms, 1)
        self.assertEqual(mauka_message.trigger_request.end_timestamp_ms, 2)
        self.assertEqual(mauka_message.trigger_request.box_ids, ["1", "2"])
        self.assertEqual(mauka_message.trigger_request.incident_id, 3)

    def test_build_triggered_event(self):
        mauka_message = pb_util.build_triggered_event("test",
                                                      [1, 2, 3],
                                                      1,
                                                      "2",
                                                      3,
                                                      4)
        self.assertTrue(isinstance(mauka_message, pb_util.mauka_pb2.MaukaMessage))
        self.assertTrue(pb_util.is_triggered_event(mauka_message))
        self.assertEqual(mauka_message.source, "test")
        self.assertEqual(mauka_message.triggered_event.data, [1, 2, 3])
        self.assertEqual(mauka_message.triggered_event.incident_id, 1)
        self.assertEqual(mauka_message.triggered_event.box_id, "2")
        self.assertEqual(mauka_message.triggered_event.start_timestamp_ms, 3)
        self.assertEqual(mauka_message.triggered_event.end_timestamp_ms, 4)

    def test_format_makai_triggering_identity(self):
        identity = pb_util.format_makai_triggering_identity("token", "uuid")
        self.assertEqual(identity, "mauka_token_uuid")

    def test_build_makai_trigger_commands_single(self):
        commands = pb_util.build_makai_trigger_commands(1, 2, ["1"], "token")
        self.assertEqual(len(commands), 1)
        command = commands[0]
        self.assertEqual(command.box_id, 1)
        self.assertTrue(command.timestamp_ms > 0)
        self.assertEqual(command.identity, "mauka_token_1")
        self.assertEqual(command.data_command.start_ms, 1)
        self.assertEqual(command.data_command.end_ms, 2)
        self.assertFalse(command.data_command.wait)

    def test_build_makai_trigger_commands_multi(self):
        commands = pb_util.build_makai_trigger_commands(1, 2, ["1", "2"], "token")
        self.assertEqual(len(commands), 2)

        command = commands[0]
        self.assertEqual(command.box_id, 1)
        self.assertTrue(command.timestamp_ms > 0)
        self.assertEqual(command.identity, "mauka_token_1")
        self.assertEqual(command.data_command.start_ms, 1)
        self.assertEqual(command.data_command.end_ms, 2)
        self.assertFalse(command.data_command.wait)

        command = commands[1]
        self.assertEqual(command.box_id, 2)
        self.assertTrue(command.timestamp_ms > 0)
        self.assertEqual(command.identity, "mauka_token_2")
        self.assertEqual(command.data_command.start_ms, 1)
        self.assertEqual(command.data_command.end_ms, 2)
        self.assertFalse(command.data_command.wait)
