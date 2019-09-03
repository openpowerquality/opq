import multiprocessing
import plugins.base_plugin
import protobuf.pb_util as pb_util
import typing

import config

import bson

# Types used when discussing type unsafe data (essentially mongo docs as dicts)
TriggeringOverrideType = typing.Dict[str, typing.Union[str, float]]
TriggeringType = typing.Dict[str, typing.Union[float, typing.List[TriggeringOverrideType]]]
MakaiConfigType = typing.Dict[str, typing.Union[bson.ObjectId, TriggeringType]]

# Constants used when converting data between type safe and type unsafe formats
ID = "_id"
TRIGGERING = "triggering"
TRIGGERING_OVERRIDES = "triggering_overrides"
BOX_ID = "box_id"
REF_F = "ref_f"
REF_V = "ref_v"
THRESHOLD_PERCENT_F_LOW = "threshold_percent_f_low"
THRESHOLD_PERCENT_F_HIGH = "threshold_percent_f_high"
THRESHOLD_PERCENT_V_LOW = "threshold_percent_v_low"
THRESHOLD_PERCENT_V_HIGH = "threshold_percent_v_high"
THRESHOLD_PERCENT_THD_HIGH = "threshold_percent_thd_high"
DEFAULT_REF_F = "default_ref_f"
DEFAULT_REF_V = "default_ref_v"
DEFAULT_THRESHOLD_PERCENT_F_LOW = "default_threshold_percent_f_low"
DEFAULT_THRESHOLD_PERCENT_F_HIGH = "default_threshold_percent_f_high"
DEFAULT_THRESHOLD_PERCENT_V_LOW = "default_threshold_percent_v_low"
DEFAULT_THRESHOLD_PERCENT_V_HIGH = "default_threshold_percent_v_high"
DEFAULT_THRESHOLD_PERCENT_THD_HIGH = "default_threshold_percent_thd_high"


class TriggeringOverride:
    def __init__(self,
                 trigger_override_dict: TriggeringOverrideType):
        self.box_id = trigger_override_dict[BOX_ID]
        self.ref_f = trigger_override_dict[REF_F]
        self.ref_v = trigger_override_dict[REF_V]
        self.threshold_percent_f_low = trigger_override_dict[THRESHOLD_PERCENT_F_LOW]
        self.threshold_percent_f_high = trigger_override_dict[THRESHOLD_PERCENT_F_HIGH]
        self.threshold_percent_v_low = trigger_override_dict[THRESHOLD_PERCENT_V_LOW]
        self.threshold_percent_v_high = trigger_override_dict[THRESHOLD_PERCENT_V_HIGH]
        self.threshold_percent_thd_high = trigger_override_dict[THRESHOLD_PERCENT_THD_HIGH]

    def __modify_threshold(self,
                           field_name: str,
                           threshold_optimization_request: pb_util.mauka_pb2.ThresholdOptimizationRequest):
        val = getattr(threshold_optimization_request, field_name)
        if val > 0.0:
            setattr(self, field_name, val)

    def modify_thresholds(self, threshold_optimization_request: pb_util.mauka_pb2.ThresholdOptimizationRequest):
        self.__modify_threshold(REF_F, threshold_optimization_request)
        self.__modify_threshold(REF_V, threshold_optimization_request)
        self.__modify_threshold(THRESHOLD_PERCENT_F_LOW, threshold_optimization_request)
        self.__modify_threshold(THRESHOLD_PERCENT_F_HIGH, threshold_optimization_request)
        self.__modify_threshold(THRESHOLD_PERCENT_V_LOW, threshold_optimization_request)
        self.__modify_threshold(THRESHOLD_PERCENT_V_HIGH, threshold_optimization_request)
        self.__modify_threshold(THRESHOLD_PERCENT_THD_HIGH, threshold_optimization_request)

    def as_dict(self) -> TriggeringOverrideType:
        return {
            BOX_ID: self.box_id,
            REF_F: self.ref_f,
            REF_V: self.ref_v,
            THRESHOLD_PERCENT_F_LOW: self.threshold_percent_f_low,
            THRESHOLD_PERCENT_F_HIGH: self.threshold_percent_f_high,
            THRESHOLD_PERCENT_V_LOW: self.threshold_percent_v_low,
            THRESHOLD_PERCENT_V_HIGH: self.threshold_percent_v_high,
            THRESHOLD_PERCENT_THD_HIGH: self.threshold_percent_thd_high
        }


def _default_override(makai_config: 'MakaiConfig', box_id: str) -> TriggeringOverride:
    return TriggeringOverride({
        BOX_ID: box_id,
        REF_F: makai_config.default_ref_f,
        REF_V: makai_config.default_ref_v,
        THRESHOLD_PERCENT_F_LOW: makai_config.default_threshold_percent_f_low,
        THRESHOLD_PERCENT_F_HIGH: makai_config.default_threshold_percent_f_high,
        THRESHOLD_PERCENT_V_LOW: makai_config.default_threshold_percent_v_low,
        THRESHOLD_PERCENT_V_HIGH: makai_config.default_threshold_percent_v_high,
        THRESHOLD_PERCENT_THD_HIGH: makai_config.default_threshold_percent_thd_high,
    })


class MakaiConfig:
    def __init__(self, makai_config_dict: MakaiConfigType):
        self.id = makai_config_dict[ID]
        self.default_ref_f = makai_config_dict[TRIGGERING]["default_ref_f"]
        self.default_ref_v = makai_config_dict[TRIGGERING]["default_ref_v"]
        self.default_threshold_percent_f_low = makai_config_dict[TRIGGERING]["default_threshold_percent_f_low"]
        self.default_threshold_percent_f_high = makai_config_dict[TRIGGERING]["default_threshold_percent_f_high"]
        self.default_threshold_percent_v_low = makai_config_dict[TRIGGERING]["default_threshold_percent_v_low"]
        self.default_threshold_percent_v_high = makai_config_dict[TRIGGERING]["default_threshold_percent_v_high"]
        self.default_threshold_percent_thd_high = makai_config_dict[TRIGGERING]["default_threshold_percent_thd_high"]
        self.box_id_to_triggering_override = {}

        for override in makai_config_dict[TRIGGERING][TRIGGERING_OVERRIDES]:
            self.box_id_to_triggering_override[override[BOX_ID]] = TriggeringOverride(override)

    def __modify_default_value(self,
                               field_name: str,
                               threshold_optimization_request: pb_util.mauka_pb2.ThresholdOptimizationRequest):
        val = getattr(threshold_optimization_request, field_name)
        if val > 0.0:
            setattr(self, field_name, val)

    def __modify_default_thresholds(self,
                                    threshold_optimization_request: pb_util.mauka_pb2.ThresholdOptimizationRequest):
        self.__modify_default_value(DEFAULT_REF_F, threshold_optimization_request)
        self.__modify_default_value(DEFAULT_REF_V, threshold_optimization_request)
        self.__modify_default_value(DEFAULT_THRESHOLD_PERCENT_F_LOW, threshold_optimization_request)
        self.__modify_default_value(DEFAULT_THRESHOLD_PERCENT_F_HIGH, threshold_optimization_request)
        self.__modify_default_value(DEFAULT_THRESHOLD_PERCENT_V_LOW, threshold_optimization_request)
        self.__modify_default_value(DEFAULT_THRESHOLD_PERCENT_V_HIGH, threshold_optimization_request)
        self.__modify_default_value(DEFAULT_THRESHOLD_PERCENT_THD_HIGH, threshold_optimization_request)

    def __modify_override_thresholds(self,
                                     threshold_optimization_request: pb_util.mauka_pb2.ThresholdOptimizationRequest):
        # If an override doesn't already exist, we need to create one based off of defaults
        box_id = threshold_optimization_request.box_id
        if box_id not in self.box_id_to_triggering_override:
            self.box_id_to_triggering_override[box_id] = _default_override(self, box_id)
        self.box_id_to_triggering_override[box_id].modify_thresholds(threshold_optimization_request)

    def modify_thresholds(self, threshold_optimization_request: pb_util.mauka_pb2.ThresholdOptimizationRequest):
        self.__modify_default_thresholds(threshold_optimization_request)
        self.__modify_override_thresholds(threshold_optimization_request)

    def as_dict(self) -> MakaiConfigType:
        return {
            ID: bson.ObjectId(self.id),
            TRIGGERING: {
                DEFAULT_REF_F: self.default_ref_f,
                DEFAULT_REF_V: self.default_ref_v,
                DEFAULT_THRESHOLD_PERCENT_F_LOW: self.default_threshold_percent_f_low,
                DEFAULT_THRESHOLD_PERCENT_F_HIGH: self.default_threshold_percent_f_high,
                DEFAULT_THRESHOLD_PERCENT_V_LOW: self.default_threshold_percent_v_low,
                DEFAULT_THRESHOLD_PERCENT_V_HIGH: self.default_threshold_percent_v_high,
                DEFAULT_THRESHOLD_PERCENT_THD_HIGH: self.default_threshold_percent_thd_high,
                TRIGGERING_OVERRIDES: list(
                    map(TriggeringOverride.as_dict, self.box_id_to_triggering_override.values()))
            }
        }


class ThresholdOptimizationPlugin(plugins.base_plugin.MaukaPlugin):
    """
    This class provides a plugin for dynamically optimizing triggering thresholds.
    """

    NAME = "ThresholdOptimizationPlugin"

    # noinspection PyUnresolvedReferences
    # pylint: disable=E1101
    def __init__(self, conf: config.MaukaConfig, exit_event: multiprocessing.Event):
        """ Initializes this plugin

        :param conf: Configuration dictionary
        """
        super().__init__(conf, ["ThresholdOptimizationRequest"], TriggerPlugin.NAME, exit_event)

    def modify_thresholds(self, threshold_optimization_request: pb_util.mauka_pb2.ThresholdOptimizationRequest):
        makai_config_doc = self.mongo_client.makai_config_collection.find_one()
        makai_config = MakaiConfig(makai_config_doc)
        makai_config.modify_thresholds(threshold_optimization_request)
        updated_config = makai_config.as_dict()
        self.mongo_client.makai_config_collection.replace_one({ID: updated_config[ID]}, updated_config)

    def on_message(self, topic: str, mauka_message: pb_util.mauka_pb2.MaukaMessage):
        """
        Called when this plugin receives a message.
        :param topic: The topic that this message is associated with
        :param mauka_message: The message
        """
        if pb_util.is_threshold_optimization_request(mauka_message):
            self.debug("Recv threshold optimization request request %s" % str(mauka_message))
            self.modify_thresholds(mauka_message.threshold_optimization_request)
        else:
            self.logger.error("Received incorrect type of MaukaMessage :%s", str(mauka_message))


if __name__ == "__main__":
    pass
