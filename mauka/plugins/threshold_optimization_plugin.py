import plugins.base_plugin
import protobuf.pb_util as pb_util


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
        """Subscribed messages occur async

        Messages are printed to stdout

        :param topic: The topic that this message is associated with
        :param mauka_message: The message
        """
        if pb_util.is_trigger_request(mauka_message):
            self.debug("Recv threshold optimization request request %s" % str(mauka_message))

        else:
            self.logger.error("Received incorrect type of MaukaMessage :%s", str(mauka_message))
