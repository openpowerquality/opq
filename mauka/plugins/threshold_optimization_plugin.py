import mongo
import multiprocessing
import plugins.base_plugin
import protobuf.pb_util as pb_util
import typing

import config

import bson


def maybe_update_default(defaults: typing.Dict[str, float],
                         threshold_optimization_request: pb_util.mauka_pb2.ThresholdOptimizationRequest,
                         attribute_name: str):
    val = getattr(threshold_optimization_request, attribute_name)
    if val > 0.0:
        defaults[attribute_name] = val


def modify_thresholds(threshold_optimization_request: pb_util.mauka_pb2.ThresholdOptimizationRequest,
                      opq_mongo_client: typing.Optional[mongo.OpqMongoClient] = None):
    """
    Given a threshold optimization request, modify dynamic thresholds with new values.
    :param threshold_optimization_request: A ThresholdOptimizationRequest.
    :param opq_mongo_client: An OpqMongoClient.
    """
    mongo_client = mongo.get_default_client(opq_mongo_client)

    doc_id = mongo_client.makai_config_collection.find_one(projection={"_id": True})["_id"]

    # First, setup updates for default values
    defaults = {}
    default_attributes = ["default_ref_f",
                          "default_ref_v",
                          "default_threshold_percent_f_low",
                          "default_threshold_percent_f_high",
                          "default_threshold_percent_v_low",
                          "default_threshold_percent_v_high",
                          "default_threshold_percent_thd_high"]

    for default_attribute in default_attributes:
        maybe_update_default(defaults, threshold_optimization_request, default_attribute)

    # Next, setup updates for override values

    filter_doc = {"_id": bson.objectid.ObjectId(doc_id)}
    update_doc = {"$set": defaults}

    mongo_client.makai_config_collection.update_one(filter_doc, update_doc)


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

    def on_message(self, topic: str, mauka_message: pb_util.mauka_pb2.MaukaMessage):
        """
        Called when this plugin receives a message.
        :param topic: The topic that this message is associated with
        :param mauka_message: The message
        """
        if pb_util.is_threshold_optimization_request(mauka_message):
            self.debug("Recv threshold optimization request request %s" % str(mauka_message))
            modify_thresholds(mauka_message.threshold_optimization_request, self.mongo_client)
        else:
            self.logger.error("Received incorrect type of MaukaMessage :%s", str(mauka_message))


if __name__ == "__main__":
    defaults = {}
    threshold_optimization_request = pb_util.mauka_pb2.ThresholdOptimizationRequest()
    threshold_optimization_request.default_ref_f = 60.0
    maybe_update_default(defaults, threshold_optimization_request, "default_ref_f")
    maybe_update_default(defaults, threshold_optimization_request, "default_ref_v")
    print(defaults)
    threshold_optimization_request.default_ref_v = 120.0
    maybe_update_default(defaults, threshold_optimization_request, "default_ref_v")
    print(defaults)
