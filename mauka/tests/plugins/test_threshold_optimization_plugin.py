import plugins.threshold_optimization_plugin as threshold_optimization_plugin
import protobuf.pb_util as pb_util

import unittest

import bson


class ThresholdOptimizationPluginTests(unittest.TestCase):
    def setUp(self) -> None:
        self.makai_config = {
            "_id" : bson.ObjectId("5cd2152d49de19d1ea2b7a25"),
            "triggering" : {
                "default_ref_f" : 61,
                "default_ref_v" : 121,
                "default_threshold_percent_f_low" : 0.6,
                "default_threshold_percent_f_high" : 0.6,
                "default_threshold_percent_v_low" : 2.6,
                "default_threshold_percent_v_high" : 2.6,
                "default_threshold_percent_thd_high" : 6,
                "triggering_overrides" : [
                    {
                        "box_id" : "0",
                        "ref_f" : 60,
                        "ref_v" : 120,
                        "threshold_percent_f_low" : 1,
                        "threshold_percent_f_high" : 1,
                        "threshold_percent_v_low" : 5,
                        "threshold_percent_v_high" : 5,
                        "threshold_percent_thd_high" : 5
                    },
                    {
                        "box_id" : "1003",
                        "ref_f" : 60,
                        "ref_v" : 120,
                        "threshold_percent_f_low" : 0.5,
                        "threshold_percent_f_high" : 0.5,
                        "threshold_percent_v_low" : 2.5,
                        "threshold_percent_v_high" : 2.5,
                        "threshold_percent_thd_high" : 3
                    },
                    {
                        "box_id" : "2001",
                        "ref_f" : 60,
                        "ref_v" : 120,
                        "threshold_percent_f_low" : 0.5,
                        "threshold_percent_f_high" : 0.5,
                        "threshold_percent_v_low" : 2.5,
                        "threshold_percent_v_high" : 2.5,
                        "threshold_percent_thd_high" : 3
                    }
                ]
            }
        }

    def test_find_override_or_default_found(self):
        self.assertEqual(threshold_optimization_plugin.find_override_or_default("0", self.makai_config),
                         {
                             "box_id" : "0",
                             "ref_f" : 60,
                             "ref_v" : 120,
                             "threshold_percent_f_low" : 1,
                             "threshold_percent_f_high" : 1,
                             "threshold_percent_v_low" : 5,
                             "threshold_percent_v_high" : 5,
                             "threshold_percent_thd_high" : 5
                         })
        self.assertEqual(threshold_optimization_plugin.find_override_or_default("1003", self.makai_config),
                         {
                             "box_id" : "1003",
                             "ref_f" : 60,
                             "ref_v" : 120,
                             "threshold_percent_f_low" : 0.5,
                             "threshold_percent_f_high" : 0.5,
                             "threshold_percent_v_low" : 2.5,
                             "threshold_percent_v_high" : 2.5,
                             "threshold_percent_thd_high" : 3
                         })
        self.assertEqual(threshold_optimization_plugin.find_override_or_default("2001", self.makai_config),
                         {
                             "box_id" : "2001",
                             "ref_f" : 60,
                             "ref_v" : 120,
                             "threshold_percent_f_low" : 0.5,
                             "threshold_percent_f_high" : 0.5,
                             "threshold_percent_v_low" : 2.5,
                             "threshold_percent_v_high" : 2.5,
                             "threshold_percent_thd_high" : 3
                         })

    def test_find_override_or_default_not_found(self):
        self.assertEqual(threshold_optimization_plugin.find_override_or_default("5000", self.makai_config),
                         {
                             "box_id" : "5000",
                             "ref_f" : 61,
                             "ref_v" : 121,
                             "threshold_percent_f_low" : 0.6,
                             "threshold_percent_f_high" : 0.6,
                             "threshold_percent_v_low" : 2.6,
                             "threshold_percent_v_high" : 2.6,
                             "threshold_percent_thd_high" : 6
                         })

    def test_get_default_threshold_defaults(self):
        threshold_optimization_request = pb_util.build_threshold_optimization_request("test")
        self.assertEqual(threshold_optimization_plugin.get_default_threshold(self.makai_config,
                                                                             threshold_optimization_request,
                                                                             "ref_f"),
                         61)


    def test_modify_thresholds_single_default(self):
        threshold_optimization_request = pb_util.build_threshold_optimization_request("test", default_ref_v=120.0)
        updated_config = threshold_optimization_plugin.modify_thresholds(threshold_optimization_request, self.makai_config)
        self.assertEqual(updated_config, {
            "_id" : bson.ObjectId("5cd2152d49de19d1ea2b7a25"),
            "triggering" : {
                "default_ref_f" : 61,
                "default_ref_v" : 120.0,
                "default_threshold_percent_f_low" : 0.6,
                "default_threshold_percent_f_high" : 0.6,
                "default_threshold_percent_v_low" : 2.6,
                "default_threshold_percent_v_high" : 2.6,
                "default_threshold_percent_thd_high" : 6,
                "triggering_overrides" : [
                    {
                        "box_id" : "0",
                        "ref_f" : 60,
                        "ref_v" : 120,
                        "threshold_percent_f_low" : 1,
                        "threshold_percent_f_high" : 1,
                        "threshold_percent_v_low" : 5,
                        "threshold_percent_v_high" : 5,
                        "threshold_percent_thd_high" : 5
                    },
                    {
                        "box_id" : "1003",
                        "ref_f" : 60,
                        "ref_v" : 120,
                        "threshold_percent_f_low" : 0.5,
                        "threshold_percent_f_high" : 0.5,
                        "threshold_percent_v_low" : 2.5,
                        "threshold_percent_v_high" : 2.5,
                        "threshold_percent_thd_high" : 3
                    },
                    {
                        "box_id" : "2001",
                        "ref_f" : 60,
                        "ref_v" : 120,
                        "threshold_percent_f_low" : 0.5,
                        "threshold_percent_f_high" : 0.5,
                        "threshold_percent_v_low" : 2.5,
                        "threshold_percent_v_high" : 2.5,
                        "threshold_percent_thd_high" : 3
                    }
                ]
            }
        }
                         )