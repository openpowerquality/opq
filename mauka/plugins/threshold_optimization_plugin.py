"""
This module provides methods for modifying thresholds dynamically.
"""

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
    """
    This class provides a type-safe wrapper around triggering overrides from the makai_config collection.
    """

    def __init__(self,
                 trigger_override_dict: TriggeringOverrideType):
        """
        Instantiates this object by passing in non-type safe data.
        :param trigger_override_dict:
        """
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
        """
        Modifies the value only if the same field in the request is > 0.
        :param field_name: The field name to check in this and the request object.
        :param threshold_optimization_request: The request to check the field value for.
        """
        val = getattr(threshold_optimization_request, field_name)
        if val > 0.0:
            setattr(self, field_name, val)

    def modify_thresholds(self, threshold_optimization_request: pb_util.mauka_pb2.ThresholdOptimizationRequest):
        """
        Given a threshold optimization request, modify all values for this override where the request values are > 0.
        :param threshold_optimization_request: The request to check the values of.
        """
        self.__modify_threshold(REF_F, threshold_optimization_request)
        self.__modify_threshold(REF_V, threshold_optimization_request)
        self.__modify_threshold(THRESHOLD_PERCENT_F_LOW, threshold_optimization_request)
        self.__modify_threshold(THRESHOLD_PERCENT_F_HIGH, threshold_optimization_request)
        self.__modify_threshold(THRESHOLD_PERCENT_V_LOW, threshold_optimization_request)
        self.__modify_threshold(THRESHOLD_PERCENT_V_HIGH, threshold_optimization_request)
        self.__modify_threshold(THRESHOLD_PERCENT_THD_HIGH, threshold_optimization_request)

    def as_dict(self) -> TriggeringOverrideType:
        """
        :return: This classes attributes as a dictionary for storage in MongoDB.
        """
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
    """
    Constructs a new override document with default values from makai_config document.
    :param makai_config: The makai config document.
    :param box_id: The box_id.
    :return: A default override document.
    """
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


def _override_has_modifications(threshold_optimization_request: pb_util.mauka_pb2.ThresholdOptimizationRequest) -> bool:
    """
    Tests if any of the override threshold fields have values > 0.
    :param threshold_optimization_request: Request to test.
    :return: True if there are modification, False otherwise.
    """
    vals = {threshold_optimization_request.ref_f,
            threshold_optimization_request.ref_v,
            threshold_optimization_request.threshold_percent_f_low,
            threshold_optimization_request.threshold_percent_f_high,
            threshold_optimization_request.threshold_percent_v_low,
            threshold_optimization_request.threshold_percent_v_high,
            threshold_optimization_request.threshold_percent_thd_high}

    return len(set(filter(lambda val: val > 0.0, vals))) > 0


class MakaiConfig:
    """
    This class provides a type-safe wrapper around makai_config documents.
    """

    def __init__(self, makai_config_dict: MakaiConfigType):
        """
        Initializes this object from non-type-safe data.
        :param makai_config_dict: Non-type-safe data.
        """
        self.id = makai_config_dict[ID]
        self.default_ref_f = makai_config_dict[TRIGGERING][DEFAULT_REF_F]
        self.default_ref_v = makai_config_dict[TRIGGERING][DEFAULT_REF_V]
        self.default_threshold_percent_f_low = makai_config_dict[TRIGGERING][DEFAULT_THRESHOLD_PERCENT_F_LOW]
        self.default_threshold_percent_f_high = makai_config_dict[TRIGGERING][DEFAULT_THRESHOLD_PERCENT_F_HIGH]
        self.default_threshold_percent_v_low = makai_config_dict[TRIGGERING][DEFAULT_THRESHOLD_PERCENT_V_LOW]
        self.default_threshold_percent_v_high = makai_config_dict[TRIGGERING][DEFAULT_THRESHOLD_PERCENT_V_HIGH]
        self.default_threshold_percent_thd_high = makai_config_dict[TRIGGERING][DEFAULT_THRESHOLD_PERCENT_THD_HIGH]
        self.box_id_to_triggering_override = {}

        for override in makai_config_dict[TRIGGERING][TRIGGERING_OVERRIDES]:
            self.box_id_to_triggering_override[override[BOX_ID]] = TriggeringOverride(override)

    def __modify_default_value(self,
                               field_name: str,
                               threshold_optimization_request: pb_util.mauka_pb2.ThresholdOptimizationRequest):
        """
        Modifies the value only if the same field in the request is > 0.
        :param field_name: The field name to check in this and the request object.
        :param threshold_optimization_request: The request to check the field value for.
        """
        val = getattr(threshold_optimization_request, field_name)
        if val > 0.0:
            setattr(self, field_name, val)

    def __modify_default_thresholds(self,
                                    threshold_optimization_request: pb_util.mauka_pb2.ThresholdOptimizationRequest):
        """
        Modifies default thresholds if the request values with the same name have values > 0.
        :param threshold_optimization_request: The request to check values in.
        """
        self.__modify_default_value(DEFAULT_REF_F, threshold_optimization_request)
        self.__modify_default_value(DEFAULT_REF_V, threshold_optimization_request)
        self.__modify_default_value(DEFAULT_THRESHOLD_PERCENT_F_LOW, threshold_optimization_request)
        self.__modify_default_value(DEFAULT_THRESHOLD_PERCENT_F_HIGH, threshold_optimization_request)
        self.__modify_default_value(DEFAULT_THRESHOLD_PERCENT_V_LOW, threshold_optimization_request)
        self.__modify_default_value(DEFAULT_THRESHOLD_PERCENT_V_HIGH, threshold_optimization_request)
        self.__modify_default_value(DEFAULT_THRESHOLD_PERCENT_THD_HIGH, threshold_optimization_request)

    def __modify_override_thresholds(self,
                                     threshold_optimization_request: pb_util.mauka_pb2.ThresholdOptimizationRequest):
        """
        Modify override thresholds if any present. Create new override thresholds for boxes that don't already have
        a threshold.
        :param threshold_optimization_request: The request.
        """
        # If an override doesn't already exist, we need to create one based off of defaults
        if _override_has_modifications(threshold_optimization_request):
            box_id = threshold_optimization_request.box_id
            if box_id not in self.box_id_to_triggering_override:
                self.box_id_to_triggering_override[box_id] = _default_override(self, box_id)
            self.box_id_to_triggering_override[box_id].modify_thresholds(threshold_optimization_request)

    def modify_thresholds(self, threshold_optimization_request: pb_util.mauka_pb2.ThresholdOptimizationRequest):
        """
        Modify thresholds based off request.
        :param threshold_optimization_request: The request.
        """
        self.__modify_default_thresholds(threshold_optimization_request)
        self.__modify_override_thresholds(threshold_optimization_request)

    def as_dict(self) -> MakaiConfigType:
        """
        :return: This classes attributes as a dictionary for MongoDB consumption.
        """
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
        """
        Modify and store new threshold modifications.
        :param threshold_optimization_request: Modification request.
        :return:
        """
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

