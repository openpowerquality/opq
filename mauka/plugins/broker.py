"""
This module provides a publish subscribe broker for Mauka plugins to use and also a Makai bridge which brings triggering
data from Makai in the Mauka environment.
"""

import multiprocessing
import typing


def start_mauka_pub_sub_broker(config: typing.Dict):
    """
    Starts an instance of a mauka pub/sub broker in a separate process
    :param config: Configuration dictionary
    """
    def _run(config: typing.Dict):
        """
        This is the target function that will run as its own process.
        :param config: OPQ Mauka config file
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

        zmq_pub_interface = config["zmq.mauka.broker.pub.interface"]
        zmq_sub_interface = config["zmq.mauka.broker.sub.interface"]
        zmq_context = zmq.Context()
        zmq_pub_socket = zmq_context.socket(zmq.PUB)
        zmq_sub_socket = zmq_context.socket(zmq.SUB)
        zmq_pub_socket.bind(zmq_pub_interface)
        zmq_sub_socket.bind(zmq_sub_interface)
        zmq_sub_socket.setsockopt(zmq.SUBSCRIBE, b"")

        _logger.info("Starting Mauka pub/sub broker")
        zmq.proxy(zmq_sub_socket, zmq_pub_socket)
        _logger.info("Exiting Mauka pub/sub broker")

    process = multiprocessing.Process(target=_run, args=(config,))
    process.start()
    return process


def start_makai_bridge(config: typing.Dict):
    """
    Starts an instance of the makai bridge to bring makai triggering data into mauka as a separate process
    :param config: Configuration dictionary
    """
    def _run(config: typing.Dict):
        import logging
        import signal
        import os
        import zmq

        _logger = logging.getLogger("app")
        logging.basicConfig(
            format="[%(levelname)s][%(asctime)s][{} %(filename)s:%(lineno)s - %(funcName)s() ] %(message)s".format(
                os.getpid()))

        signal.signal(signal.SIGINT, signal.SIG_IGN)

        _logger.info("Starting makai bridge...")

        zmq_context = zmq.Context()
        zmq_sub_trigger_socket = zmq_context.socket(zmq.SUB)
        zmq_sub_trigger_socket.setsockopt(zmq.SUBSCRIBE, b"")
        zmq_pub_socket = zmq_context.socket(zmq.PUB)
        zmq_sub_trigger_socket.connect(config["zmq.triggering.interface"])
        zmq_pub_socket.connect(config["zmq.mauka.plugin.pub.interface"])

        while True:
            trigger_msg = zmq_sub_trigger_socket.recv_multipart()
            zmq_pub_socket.send_multipart(("measurement".encode(), trigger_msg[1]))

    process = multiprocessing.Process(target=_run, args=(config,))
    process.start()
    return process
