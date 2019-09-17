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

    def test_build_makai_rate_change_commands_single(self):
        commands = pb_util.build_makai_rate_change_commands(["1"],
                                                            60)
        self.assertEqual(len(commands), 1)
        command, identity = commands[0]
        identity_parts = identity.split("_")
        self.assertEqual(identity_parts[0], "maukarate")
        self.assertEqual(identity_parts[2], "0")
        self.assertEqual(command.box_id, 1)
        self.assertEqual(command.identity, identity)
        self.assertTrue(command.timestamp_ms > 0)
        self.assertEqual(command.sampling_rate_command.measurement_window_cycles, 60)

    def test_build_makai_rate_change_commands_multi(self):
        commands = pb_util.build_makai_rate_change_commands(["1", "2"],
                                                            60)
        self.assertEqual(len(commands), 2)
        command, identity = commands[0]
        identity_parts = identity.split("_")
        self.assertEqual(identity_parts[0], "maukarate")
        self.assertEqual(identity_parts[2], "0")
        self.assertEqual(command.box_id, 1)
        self.assertEqual(command.identity, identity)
        self.assertTrue(command.timestamp_ms > 0)
        self.assertEqual(command.sampling_rate_command.measurement_window_cycles, 60)

        command, identity = commands[1]
        identity_parts = identity.split("_")
        self.assertEqual(identity_parts[0], "maukarate")
        self.assertEqual(identity_parts[2], "1")
        self.assertEqual(command.box_id, 2)
        self.assertEqual(command.identity, identity)
        self.assertTrue(command.timestamp_ms > 0)
        self.assertEqual(command.sampling_rate_command.measurement_window_cycles, 60)

    def test_build_makai_get_info_cmd(self):
        command, identity = pb_util.build_makai_get_info_command("1")
        identity_parts = identity.split("_")
        self.assertEqual(identity_parts[0], "maukainfo")
        self.assertEqual(identity_parts[2], "0")
        self.assertEqual(command.box_id, 1)
        self.assertEqual(command.identity, identity)
        self.assertTrue(command.timestamp_ms > 0)

    def test_build_threshold_optimization_request_defaults(self):
        mauka_message = pb_util.build_threshold_optimization_request("test")
        self.assertTrue(isinstance(mauka_message, pb_util.mauka_pb2.MaukaMessage))
        self.assertTrue(pb_util.is_threshold_optimization_request(mauka_message))
        self.assertEqual(mauka_message.source, "test")
        self.assertEqual(mauka_message.threshold_optimization_request.default_ref_f, 0.0)
        self.assertEqual(mauka_message.threshold_optimization_request.default_ref_v, 0.0)
        self.assertEqual(mauka_message.threshold_optimization_request.default_threshold_percent_f_low, 0.0)
        self.assertEqual(mauka_message.threshold_optimization_request.default_threshold_percent_f_high, 0.0)
        self.assertEqual(mauka_message.threshold_optimization_request.default_threshold_percent_v_low, 0.0)
        self.assertEqual(mauka_message.threshold_optimization_request.default_threshold_percent_v_high, 0.0)
        self.assertEqual(mauka_message.threshold_optimization_request.default_threshold_percent_thd_high, 0.0)
        self.assertEqual(mauka_message.threshold_optimization_request.default_threshold_percent_thd_high, 0.0)

        self.assertEqual(mauka_message.threshold_optimization_request.box_id, "")
        self.assertEqual(mauka_message.threshold_optimization_request.ref_f, 0.0)
        self.assertEqual(mauka_message.threshold_optimization_request.ref_v, 0.0)
        self.assertEqual(mauka_message.threshold_optimization_request.threshold_percent_f_low, 0.0)
        self.assertEqual(mauka_message.threshold_optimization_request.threshold_percent_f_high, 0.0)
        self.assertEqual(mauka_message.threshold_optimization_request.threshold_percent_v_low, 0.0)
        self.assertEqual(mauka_message.threshold_optimization_request.threshold_percent_v_high, 0.0)
        self.assertEqual(mauka_message.threshold_optimization_request.threshold_percent_thd_high, 0.0)
        self.assertEqual(mauka_message.threshold_optimization_request.threshold_percent_thd_high, 0.0)

    def test_build_threshold_optimization_request(self):
        mauka_message = pb_util.build_threshold_optimization_request("test",
                                                                     1, 2, 3, 4, 5, 6, 7,
                                                                     "1000",
                                                                     8, 9, 10, 11, 12, 13, 14)
        self.assertTrue(isinstance(mauka_message, pb_util.mauka_pb2.MaukaMessage))
        self.assertTrue(pb_util.is_threshold_optimization_request(mauka_message))
        self.assertEqual(mauka_message.source, "test")
        self.assertEqual(mauka_message.threshold_optimization_request.default_ref_f, 1.0)
        self.assertEqual(mauka_message.threshold_optimization_request.default_ref_v, 2.0)
        self.assertEqual(mauka_message.threshold_optimization_request.default_threshold_percent_f_low, 3.0)
        self.assertEqual(mauka_message.threshold_optimization_request.default_threshold_percent_f_high, 4.0)
        self.assertEqual(mauka_message.threshold_optimization_request.default_threshold_percent_v_low, 5.0)
        self.assertEqual(mauka_message.threshold_optimization_request.default_threshold_percent_v_high, 6.0)
        self.assertEqual(mauka_message.threshold_optimization_request.default_threshold_percent_thd_high, 7.0)

        self.assertEqual(mauka_message.threshold_optimization_request.box_id, "1000")
        self.assertEqual(mauka_message.threshold_optimization_request.ref_f, 8.0)
        self.assertEqual(mauka_message.threshold_optimization_request.ref_v, 9.0)
        self.assertEqual(mauka_message.threshold_optimization_request.threshold_percent_f_low, 10.0)
        self.assertEqual(mauka_message.threshold_optimization_request.threshold_percent_f_high, 11.0)
        self.assertEqual(mauka_message.threshold_optimization_request.threshold_percent_v_low, 12.0)
        self.assertEqual(mauka_message.threshold_optimization_request.threshold_percent_v_high, 13.0)
        self.assertEqual(mauka_message.threshold_optimization_request.threshold_percent_thd_high, 14.0)

    def test_build_box_optimization_request(self):
        mauka_message = pb_util.build_box_optimization_request("test",
                                                               ["1", "2"],
                                                               60)
        self.assertTrue(isinstance(mauka_message, pb_util.mauka_pb2.MaukaMessage))
        self.assertTrue(pb_util.is_box_optimization_request(mauka_message))
        self.assertEqual(mauka_message.source, "test")
        self.assertEqual(mauka_message.box_optimization_request.box_ids, ["1", "2"])
        self.assertEqual(mauka_message.box_optimization_request.measurement_window_cycles, 60)

    def test_serialize_deserialize_message(self):
        mauka_message = pb_util.build_mauka_message("test")
        serialized = pb_util.serialize_message(mauka_message)
        self.assertTrue(isinstance(serialized, bytes))
        deserialized = pb_util.deserialize_mauka_message(serialized)
        self.assertTrue(isinstance(deserialized, pb_util.mauka_pb2.MaukaMessage))
        self.assertTrue(mauka_message.source, "test")

    def test_deserialize_makai_response(self):
        response = pb_util.opqbox3_pb2.Response()
        response.box_id = 1
        response.seq = 2
        response.timestamp_ms = 3
        response.message_rate_reponse.old_rate_cycles = 60
        serialized = pb_util.serialize_message(response)
        deserialized = pb_util.deserialize_makai_response(serialized)
        self.assertTrue(isinstance(deserialized, pb_util.opqbox3_pb2.Response))
        self.assertEqual(deserialized.box_id, 1)
        self.assertEqual(deserialized.seq, 2)
        self.assertEqual(deserialized.timestamp_ms, 3)
        self.assertEqual(deserialized.message_rate_reponse.old_rate_cycles, 60)

    def test_deserialize_makai_cycle(self):
        cycle = pb_util.opqbox3_pb2.Cycle()
        cycle.datapoints[:] = [1, 2, 3]
        cycle.timestamp_ms = 4
        serialized = pb_util.serialize_message(cycle)
        deserialized = pb_util.deserialize_makai_cycle(serialized)
        self.assertTrue(isinstance(deserialized, pb_util.opqbox3_pb2.Cycle))
        self.assertEqual(deserialized.datapoints, [1, 2, 3])
        self.assertEqual(deserialized.timestamp_ms, 4)

    def test_which_message_oneof(self):
        payload = pb_util.build_payload("", 0, "", pb_util.mauka_pb2.MEASUREMENTS, [], 0, 0)
        self.assertEqual(pb_util.which_message_oneof(payload), pb_util.PAYLOAD)
        heartbeat = pb_util.build_heartbeat("", 0, 0, "", "")
        self.assertEqual(pb_util.which_message_oneof(heartbeat), pb_util.HEARTBEAT)
        makai_event = pb_util.build_makai_event("", 0)
        self.assertEqual(pb_util.which_message_oneof(makai_event), pb_util.MAKAI_EVENT)
        measurement = pb_util.build_measurement("", "", 0, 0, 0, 0)
        self.assertEqual(pb_util.which_message_oneof(measurement), pb_util.MEASUREMENT)
        makai_trigger = pb_util.build_makai_trigger("", 0, 0, "", 0, "")
        self.assertEqual(pb_util.which_message_oneof(makai_trigger), pb_util.MAKAI_TRIGGER)
        laha_ttl = pb_util.build_ttl("", "", 0)
        self.assertEqual(pb_util.which_message_oneof(laha_ttl), pb_util.LAHA)
        laha_gc_trigger = pb_util.build_gc_trigger("", [])
        self.assertEqual(pb_util.which_message_oneof(laha_gc_trigger), pb_util.LAHA)
        laha_gc_update = pb_util.build_gc_update("", pb_util.mauka_pb2.MEASUREMENTS, 0)
        self.assertEqual(pb_util.which_message_oneof(laha_gc_update), pb_util.LAHA)
        laha_gc_stat = pb_util.build_gc_stat("", pb_util.mauka_pb2.MEASUREMENTS, 0)
        self.assertEqual(pb_util.which_message_oneof(laha_gc_stat), pb_util.LAHA)
        trigger_request = pb_util.build_trigger_request("", 0, 0, [], 0)
        self.assertEqual(pb_util.which_message_oneof(trigger_request), pb_util.TRIGGER_REQUEST)
        triggered_event = pb_util.build_triggered_event("", [], 0, "", 0, 0)
        self.assertEqual(pb_util.which_message_oneof(triggered_event), pb_util.TRIGGERED_EVENT)
        threshold_optimization_request = pb_util.build_threshold_optimization_request("")
        self.assertEqual(pb_util.which_message_oneof(threshold_optimization_request), pb_util.THRESHOLD_OPTIMIZATION_REQUEST)
        box_optimization_request = pb_util.build_box_optimization_request("", [], 0)
        self.assertEqual(pb_util.which_message_oneof(box_optimization_request), pb_util.BOX_OPTIMIZATION_REQUEST)

    def test_which_response_oneof(self):
        def _build_response() -> pb_util.opqbox3_pb2.Response:
            response = pb_util.opqbox3_pb2.Response()
            response.box_id = 1
            response.seq = 2
            response.timestamp_ms = 3
            return response

        info_response = _build_response()
        info_response.info_response.mac_addr = ""
        info_response.info_response.wifi_network = ""
        info_response.info_response.ip = ""
        info_response.info_response.uptime = 0
        info_response.info_response.calibration_constant = 0
        info_response.info_response.pub_key = ""
        info_response.info_response.measurement_rate = 0
        self.assertEqual(pb_util.which_response_oneof(info_response), pb_util.MAKAI_INFO_RESPONSE)

        message_rate_response = _build_response()
        message_rate_response.message_rate_reponse.old_rate_cycles = 60
        self.assertEqual(pb_util.which_response_oneof(message_rate_response), pb_util.MAKAI_MESSAGE_RATE_RESPONSE)

        data_response = _build_response()
        data_response.get_data_response.start_ts = 0
        data_response.get_data_response.end_ts = 1
        self.assertEqual(pb_util.which_response_oneof(data_response), pb_util.MAKAI_DATA_RESPONSE)

        command_to_plugin_response = _build_response()
        command_to_plugin_response.command_to_plugin_response.ok = False
        self.assertEqual(pb_util.which_response_oneof(command_to_plugin_response), pb_util.MAKAI_COMMAND_TO_PLUGIN_RESPONSE)

    def test_is_payload(self):
        def _build_payload() -> pb_util.mauka_pb2.Payload:
            return pb_util.build_payload("", 0, "", pb_util.mauka_pb2.ADC_SAMPLES, [], 0, 0)

        payload_types = [
            pb_util.mauka_pb2.ADC_SAMPLES,
            pb_util.mauka_pb2.VOLTAGE_RAW,
            pb_util.mauka_pb2.VOLTAGE_RMS,
            pb_util.mauka_pb2.VOLTAGE_RMS_WINDOWED,
            pb_util.mauka_pb2.FREQUENCY_WINDOWED
        ]

        for payload_type in payload_types:
            payload = _build_payload()
            payload.payload.payload_type = payload_type
            self.assertTrue(pb_util.is_payload(payload, payload_type))

    def test_is_heartbeat_message(self):
        mauka_message = pb_util.build_heartbeat("", 0, 0, "", "")
        other_message = pb_util.build_makai_event("", 0)
        self.assertTrue(pb_util.is_heartbeat_message(mauka_message))
        self.assertFalse(pb_util.is_heartbeat_message(other_message))

    def test_is_makai_event_message(self):
        mauka_message = pb_util.build_makai_event("", 0)
        other_message = pb_util.build_heartbeat("", 0, 0, "", "")
        self.assertTrue(pb_util.is_makai_event_message(mauka_message))
        self.assertFalse(pb_util.is_makai_event_message(other_message))

    def test_is_makai_trigger(self):
        mauka_message = pb_util.build_makai_trigger("", 0, 0, "", 0, "")
        other_message = pb_util.build_makai_event("", 0)
        self.assertTrue(pb_util.is_makai_trigger(mauka_message))
        self.assertFalse(pb_util.is_makai_trigger(other_message))

    def test_is_measurement(self):
        mauka_message = pb_util.build_measurement("", "", 0, 0, 0, 0)
        other_message = pb_util.build_makai_event("", 0)
        self.assertTrue(pb_util.is_measurement(mauka_message))
        self.assertFalse(pb_util.is_measurement(other_message))

    def test_is_laha_and_related(self):
        laha_ttl = pb_util.build_ttl("", "", 0)
        laha_gc_trigger = pb_util.build_gc_trigger("", [])
        laha_gc_update = pb_util.build_gc_update("", pb_util.mauka_pb2.MEASUREMENTS, 0)
        laha_gc_stat = pb_util.build_gc_stat("", pb_util.mauka_pb2.MEASUREMENTS, 0)

        laha_messages = [laha_ttl, laha_gc_trigger, laha_gc_update, laha_gc_stat]
        for message in laha_messages:
            self.assertTrue(pb_util.is_laha(message))

        self.assertTrue(pb_util.is_ttl(laha_ttl))
        self.assertFalse(pb_util.is_ttl(laha_gc_stat))
        self.assertTrue(pb_util.is_gc_trigger(laha_gc_trigger))
        self.assertTrue(pb_util.is_gc_update(laha_gc_update))
        self.assertTrue(pb_util.is_gc_stat(laha_gc_stat))

    def test_is_trigger_request(self):
        mauka_message = pb_util.build_trigger_request("", 0, 0, [], 0)
        other_message = pb_util.build_makai_event("", 0)
        self.assertTrue(pb_util.is_trigger_request(mauka_message))
        self.assertFalse(pb_util.is_trigger_request(other_message))

    def test_is_triggered_event(self):
        mauka_message = pb_util.build_triggered_event("", [], 0, "", 0, 0)
        other_message = pb_util.build_makai_event("", 0)
        self.assertTrue(pb_util.is_triggered_event(mauka_message))
        self.assertFalse(pb_util.is_triggered_event(other_message))

    def test_is_threshold_optimization_request(self):
        mauka_message = pb_util.build_threshold_optimization_request("")
        other_message = pb_util.build_makai_event("", 0)
        self.assertTrue(pb_util.is_threshold_optimization_request(mauka_message))
        self.assertFalse(pb_util.is_threshold_optimization_request(other_message))

    def test_is_box_optimization_request(self):
        mauka_message = pb_util.build_box_optimization_request("", [], 0)
        other_message = pb_util.build_makai_event("", 0)
        self.assertTrue(pb_util.is_box_optimization_request(mauka_message))
        self.assertFalse(pb_util.is_box_optimization_request(other_message))

    def test_is_makai_info_response(self):
        def _build_response() -> pb_util.opqbox3_pb2.Response:
            response = pb_util.opqbox3_pb2.Response()
            response.box_id = 1
            response.seq = 2
            response.timestamp_ms = 3
            return response

        info_response = _build_response()
        info_response.info_response.mac_addr = ""
        info_response.info_response.wifi_network = ""
        info_response.info_response.ip = ""
        info_response.info_response.uptime = 0
        info_response.info_response.calibration_constant = 0
        info_response.info_response.pub_key = ""
        info_response.info_response.measurement_rate = 0

        self.assertTrue(pb_util.is_makai_info_response(info_response))

    def test_is_makai_data_response(self):
        def _build_response() -> pb_util.opqbox3_pb2.Response:
            response = pb_util.opqbox3_pb2.Response()
            response.box_id = 1
            response.seq = 2
            response.timestamp_ms = 3
            return response

        data_response = _build_response()
        data_response.get_data_response.start_ts = 0
        data_response.get_data_response.end_ts = 1

        self.assertTrue(pb_util.is_makai_data_response(data_response))

    def test_is_makai_rate_response(self):
        def _build_response() -> pb_util.opqbox3_pb2.Response:
            response = pb_util.opqbox3_pb2.Response()
            response.box_id = 1
            response.seq = 2
            response.timestamp_ms = 3
            return response


        message_rate_response = _build_response()
        message_rate_response.message_rate_reponse.old_rate_cycles = 60

        self.assertTrue(pb_util.is_makai_message_rate_response(message_rate_response))

    def test_is_makai_command_to_plugin_response(self):
        def _build_response() -> pb_util.opqbox3_pb2.Response:
            response = pb_util.opqbox3_pb2.Response()
            response.box_id = 1
            response.seq = 2
            response.timestamp_ms = 3
            return response

        command_to_plugin_response = _build_response()
        command_to_plugin_response.command_to_plugin_response.ok = False
        self.assertTrue(pb_util.is_makai_command_to_plugin_response(command_to_plugin_response))

    def test_repeated_as_ndarray(self):
        cycle = pb_util.opqbox3_pb2.Cycle()
        cycle.datapoints[:] = [1, 2, 3]

        self.assertTrue(np.array_equal(cycle.datapoints, np.array([1, 2, 3])))
