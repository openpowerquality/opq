import plugins.threshold_optimization_plugin as threshold_optimization_plugin
import protobuf.pb_util as pb_util

import unittest

import bson

MAKAI_CONFIG = {
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


class ThresholdOptimizationPluginTests(unittest.TestCase):
    def setUp(self) -> None:
        self.makai_config_doc = MAKAI_CONFIG
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
        threshold_req = pb_util.build_threshold_optimization_request("test", ref_f=61).threshold_optimization_request
        override.modify_thresholds(threshold_req)
        self.assertEqual(override.as_dict(),
                         {
                             "box_id": "5000",
                             "ref_f": 61,
                             "ref_v": 120,
                             "threshold_percent_f_low": 0.5,
                             "threshold_percent_f_high": 0.5,
                             "threshold_percent_v_low": 2.5,
                             "threshold_percent_v_high": 2.5,
                             "threshold_percent_thd_high": 3
                         })

    def test_trigger_override_none(self):
        override = threshold_optimization_plugin._default_override(self.makai_config, "5000")
        threshold_req = pb_util.build_threshold_optimization_request("test").threshold_optimization_request
        override.modify_thresholds(threshold_req)
        self.assertEqual(override.as_dict(),
                         {
                             "box_id": "5000",
                             "ref_f": 60,
                             "ref_v": 120,
                             "threshold_percent_f_low": 0.5,
                             "threshold_percent_f_high": 0.5,
                             "threshold_percent_v_low": 2.5,
                             "threshold_percent_v_high": 2.5,
                             "threshold_percent_thd_high": 3
                         })

    def test_trigger_override_multi(self):
        override = threshold_optimization_plugin._default_override(self.makai_config, "5000")
        threshold_req = pb_util.build_threshold_optimization_request("test",
                                                                     ref_v=121,
                                                                     threshold_percent_f_low=20.5).threshold_optimization_request
        override.modify_thresholds(threshold_req)
        self.assertEqual(override.as_dict(),
                         {
                             "box_id": "5000",
                             "ref_f": 60,
                             "ref_v": 121,
                             "threshold_percent_f_low": 20.5,
                             "threshold_percent_f_high": 0.5,
                             "threshold_percent_v_low": 2.5,
                             "threshold_percent_v_high": 2.5,
                             "threshold_percent_thd_high": 3
                         })

    def test_makai_config_none(self):
        threshold_req = pb_util.build_threshold_optimization_request("test").threshold_optimization_request
        self.makai_config.modify_thresholds(threshold_req)
        self.assertEqual(self.makai_config.as_dict(), MAKAI_CONFIG)

    def test_makai_config_default_single(self):
        threshold_req = pb_util.build_threshold_optimization_request("test",
                                                                     default_ref_f=61).threshold_optimization_request
        self.makai_config.modify_thresholds(threshold_req)

        self.assertEqual(self.makai_config.as_dict(), {
            "_id": bson.ObjectId("5cd2152d49de19d1ea2b7a25"),
            "triggering": {
                "default_ref_f": 61,
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
                         )

    def test_makai_config_default_multi(self):
        threshold_req = pb_util.build_threshold_optimization_request("test",
                                                                     default_ref_f=61,
                                                                     default_threshold_percent_f_low=20).threshold_optimization_request
        self.makai_config.modify_thresholds(threshold_req)

        self.assertEqual(self.makai_config.as_dict(), {
            "_id": bson.ObjectId("5cd2152d49de19d1ea2b7a25"),
            "triggering": {
                "default_ref_f": 61,
                "default_ref_v": 120,
                "default_threshold_percent_f_low": 20,
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
                         )


    def test_makai_config_default_new_override(self):
        threshold_req = pb_util.build_threshold_optimization_request("test",
                                                                     box_id="6000",
                                                                     ref_f=61).threshold_optimization_request
        self.makai_config.modify_thresholds(threshold_req)

        self.assertEqual(self.makai_config.as_dict(), {
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
                    },
                    {
                        "box_id": "6000",
                        "ref_f": 61.0,
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
                         )


    def test_makai_config_default_override(self):
        threshold_req = pb_util.build_threshold_optimization_request("test",
                                                                     box_id="0",
                                                                     ref_f=61).threshold_optimization_request
        self.makai_config.modify_thresholds(threshold_req)

        self.assertEqual(self.makai_config.as_dict(), {
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
                        "ref_f": 61.0,
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
                         )

    def test_makai_config_all(self):
        threshold_req = pb_util.build_threshold_optimization_request("test",
                                                                     default_ref_f=1,
                                                                     default_ref_v=1,
                                                                     default_threshold_percent_f_low=1,
                                                                     default_threshold_percent_f_high=1,
                                                                     default_threshold_percent_v_low=1,
                                                                     default_threshold_percent_v_high=1,
                                                                     default_threshold_percent_thd_high=1,
                                                                     ref_f=2,
                                                                     ref_v=2,
                                                                     threshold_percent_f_low=2,
                                                                     threshold_percent_f_high=2,
                                                                     threshold_percent_v_low=2,
                                                                     threshold_percent_v_high=2,
                                                                     threshold_percent_thd_high=2,
                                                                     box_id="0",
                                                                     ).threshold_optimization_request
        self.makai_config.modify_thresholds(threshold_req)

        self.assertEqual(self.makai_config.as_dict(), {
            "_id": bson.ObjectId("5cd2152d49de19d1ea2b7a25"),
            "triggering": {
                "default_ref_f": 1.0,
                "default_ref_v": 1.0,
                "default_threshold_percent_f_low": 1.0,
                "default_threshold_percent_f_high": 1.0,
                "default_threshold_percent_v_low": 1.0,
                "default_threshold_percent_v_high": 1.0,
                "default_threshold_percent_thd_high": 1.0,
                "triggering_overrides": [
                    {
                        "box_id": "0",
                        "ref_f": 2.0,
                        "ref_v": 2.0,
                        "threshold_percent_f_low": 2.0,
                        "threshold_percent_f_high": 2.0,
                        "threshold_percent_v_low": 2.0,
                        "threshold_percent_v_high": 2.0,
                        "threshold_percent_thd_high": 2.0
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
                         )
