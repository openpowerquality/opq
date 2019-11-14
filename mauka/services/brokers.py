"""
This module provides a publish subscribe broker for Mauka plugins to use and also a Makai bridge which brings triggering
data from Makai in the Mauka environment.
"""

import multiprocessing

import services.incident_id_provider
import config
import protobuf.pb_util

from plugins.routes import Routes


def start_mauka_pub_sub_broker(mauka_config: config.MaukaConfig):
    """
    Starts an instance of a mauka pub/sub broker in a separate process
    :param mauka_config: Configuration dictionary
    """

    # noinspection PyUnresolvedReferences
    # pylint: disable=E1101
    def _run(conf: config.MaukaConfig):
        """
        This is the target function that will run as its own process.
        :param conf: OPQ Mauka config file
        :return: The process object.
        """
        import logging
        import signal
        import os
        import zmq

        _logger = logging.getLogger("app")
        logging.basicConfig(
            format="[%(levelname)s][%(asctime)s][{} %(filename)s:%(lineno)s - %(funcName)s() ] %(message)s".format(
                os.getpid()))

        signal.signal(signal.SIGINT, signal.SIG_IGN)

        zmq_pub_interface = conf.get("zmq.mauka.broker.pub.interface")
        zmq_sub_interface = conf.get("zmq.mauka.broker.sub.interface")
        zmq_context = zmq.Context()
        zmq_pub_socket = zmq_context.socket(zmq.PUB)
        zmq_sub_socket = zmq_context.socket(zmq.SUB)
        zmq_pub_socket.bind(zmq_pub_interface)
        zmq_sub_socket.bind(zmq_sub_interface)
        zmq_sub_socket.setsockopt(zmq.SUBSCRIBE, b"")

        _logger.info("Starting Mauka pub/sub broker")
        zmq.proxy(zmq_sub_socket, zmq_pub_socket)
        _logger.info("Exiting Mauka pub/sub broker")

    process = multiprocessing.Process(target=_run, args=(mauka_config,))
    process.start()
    return process


def start_makai_event_bridge(mauka_config: config.MaukaConfig):
    """
    Starts an instance of the makai bridge to bring makai event information into mauka as a separate process
    :param mauka_config: Configuration dictionary
    """

    # noinspection PyUnresolvedReferences
    # pylint: disable=E1101
    def _run(conf: config.MaukaConfig):
        import logging
        import signal
        import os
        import zmq

        _logger = logging.getLogger("app")
        logging.basicConfig(
            format="[%(levelname)s][%(asctime)s][{} %(filename)s:%(lineno)s - %(funcName)s() ] %(message)s".format(
                os.getpid()))

        signal.signal(signal.SIGINT, signal.SIG_IGN)

        _logger.info("Starting makai event bridge...")

        zmq_context = zmq.Context()
        zmq_sub_event_socket = zmq_context.socket(zmq.SUB)
        zmq_sub_event_socket.setsockopt(zmq.SUBSCRIBE, b"")
        zmq_pub_socket = zmq_context.socket(zmq.PUB)
        zmq_sub_event_socket.connect(conf.get("zmq.event.interface"))
        zmq_pub_socket.connect(conf.get("zmq.mauka.plugin.pub.interface"))

        while True:
            event_msg = zmq_sub_event_socket.recv_multipart()
            if mauka_config.get("debug", False):
                _logger.debug("recv event msg: %s", str(event_msg))
            event_id = int(event_msg[1])
            makai_event = protobuf.pb_util.build_makai_event("makai_event_bridge", event_id)
            mauka_message_bytes = protobuf.pb_util.serialize_message(makai_event)
            zmq_pub_socket.send_multipart((Routes.makai_event.encode(), mauka_message_bytes))

    process = multiprocessing.Process(target=_run, args=(mauka_config,))
    process.start()
    return process


def start_incident_id_service(mauka_config: config.MaukaConfig):
    def _run(conf: config.MaukaConfig):
        import logging
        import signal
        import os

        import mongo

        import zmq

        _logger = logging.getLogger("app")
        logging.basicConfig(
            format="[%(levelname)s][%(asctime)s][{} %(filename)s:%(lineno)s - %(funcName)s() ] %(message)s".format(
                os.getpid()))

        signal.signal(signal.SIGINT, signal.SIG_IGN)

        _logger.info("Starting incident id service...")

        mongo_client = mongo.OpqMongoClient(conf.get("mongo.host"),
                                            int(conf.get("mongo.port")),
                                            conf.get("mongo.db"))
        next_available_incident_id = mongo.next_available_incident_id(mongo_client)
        incident_id_service = services.incident_id_provider.IncidentIdProvider(next_available_incident_id)

        zmq_context: zmq.Context = zmq.Context()
        zmq_req_socket: zmq.Socket = zmq_context.socket(zmq.REP)
        zmq_req_socket.bind(conf.get("zmq.incident_id_provider.rep.interface"))

        while True:
            req: bytes = zmq_req_socket.recv()
            mauka_message: protobuf.pb_util.mauka_pb2.MaukaMessage = protobuf.pb_util.deserialize_mauka_message(req)
            if protobuf.pb_util.is_incident_id_req(mauka_message):
                resp = protobuf.pb_util.build_incident_id_resp("incident_id_service",
                                                               mauka_message.incident_id_req.req_id,
                                                               incident_id_service.get_and_inc())
                zmq_req_socket.send(protobuf.pb_util.serialize_message(resp))
            else:
                _logger.error("Did not receive valid IncidentIdReq")

    process = multiprocessing.Process(target=_run, args=(mauka_config,))
    process.start()
    return process
