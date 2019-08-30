import plugins.base_plugin


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
        super().__init__(conf, ["TriggerRequest"], TriggerPlugin.NAME, exit_event)
        # Setup ZMQ
        zmq_context = zmq.Context()
        self.zmq_trigger_interface: str = conf.get("zmq.trigger.interface")
        self.zmq_data_interface: str = conf.get("zmq.data.interface")
        self.zmq_producer_interface: str = conf.get("zmq.mauka.plugin.pub.interface")
        self.zmq_event_id_interface: str = conf.get("zmq.event_id.interface")
        self.zmq_trigger_socket = zmq_context.socket(zmq.PUSH)
        self.zmq_trigger_socket.connect(self.zmq_trigger_interface)
        self.zmq_event_id_socket = zmq_context.socket(zmq.REQ)
        self.zmq_event_id_socket.connect(self.zmq_event_id_interface)

        # Setup trigger records
        self.trigger_records = TriggerRecords()

        # Start MakaiDataSubscriber thread
        makai_data_subscriber = MakaiDataSubscriber(self.zmq_data_interface,
                                                    self.zmq_producer_interface,
                                                    self.trigger_records,
                                                    self.logger)
        makai_data_subscriber.start()

    def on_message(self, topic: str, mauka_message: pb_util.mauka_pb2.MaukaMessage):
        """Subscribed messages occur async

        Messages are printed to stdout

        :param topic: The topic that this message is associated with
        :param mauka_message: The message
        """
        if pb_util.is_trigger_request(mauka_message):
            self.debug("Recv trigger request %s" % str(mauka_message))
            trigger_boxes(self.zmq_trigger_socket,
                          self.zmq_event_id_socket,
                          self.trigger_records,
                          mauka_message.trigger_request.start_timestamp_ms,
                          mauka_message.trigger_request.end_timestamp_ms,
                          mauka_message.trigger_request.box_ids[:],
                          self.logger,
                          self.mongo_client)
        else:
            self.logger.error("Received incorrect type of MaukaMessage :%s", str(mauka_message))
