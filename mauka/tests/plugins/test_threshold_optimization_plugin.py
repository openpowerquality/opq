import plugins.threshold_optimization_plugin as threshold_optimization_plugin
import protobuf.pb_util as pb_util

import unittest

import bson


class ThresholdOptimizationPluginTests(unittest.TestCase):
    def setUp(self) -> None:
        self.makai_config_doc = {
            "_id": bson.ObjectId("5cd2152d49de19d1ea2b7a25"),
            "triggering": {
                "default_ref_f": 60,
                "default_ref_v": 120,
                "default_threshold_percent_f_low": 0.5,
                "default_threshold_percent_f_high": 0.5,
                "default_threshold_percent_v_low": 2.5,
                "default_threshold_percent_v_high": 2.5,
                "default_threshold_percent_thd_high": 3,
                "triggering_overrides": [
                    {
                        "box_id": "0",
                        "ref_f": 60,
                        "ref_v": 120,
                        "threshold_percent_f_low": 1,
                        "threshold_percent_f_high": 1,
                        "threshold_percent_v_low": 5,
                        "threshold_percent_v_high": 5,
                        "threshold_percent_thd_high": 5
                    },
                    {
                        "box_id": "1003",
                        "ref_f": 60,
                        "ref_v": 120,
                        "threshold_percent_f_low": 0.5,
                        "threshold_percent_f_high": 0.5,
                        "threshold_percent_v_low": 2.5,
                        "threshold_percent_v_high": 2.5,
                        "threshold_percent_thd_high": 3
                    },
                    {
                        "box_id": "2001",
                        "ref_f": 60,
                        "ref_v": 120,
                        "threshold_percent_f_low": 0.5,
                        "threshold_percent_f_high": 0.5,
                        "threshold_percent_v_low": 2.5,
                        "threshold_percent_v_high": 2.5,
                        "threshold_percent_thd_high": 3
                    }
                ]
            }
        }
        self.makai_config = threshold_optimization_plugin.MakaiConfig(self.makai_config_doc)

    def test_default_override(self):
        override = threshold_optimization_plugin._default_override(self.makai_config, "5000")
        self.assertEqual(override.as_dict(), {
            "box_id": "5000",
            "ref_f": 60,
            "ref_v": 120,
            "threshold_percent_f_low": 0.5,
            "threshold_percent_f_high": 0.5,
            "threshold_percent_v_low": 2.5,
            "threshold_percent_v_high": 2.5,
            "threshold_percent_thd_high": 3
        })

    def test_trigger_override_single(self):
        override = threshold_optimization_plugin._default_override(self.makai_config, "5000")
        threshold_req = pb_util.build_threshold_optimization_request("test", ref_f=61)
