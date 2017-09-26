import multiprocessing
import typing


def start_mauka_pub_sub_broker(config: typing.Dict):
    def _run(config: typing.Dict):
        import logging
        import os
        import zmq

        _logger = logging.getLogger("app")
        logging.basicConfig(
            format="[%(levelname)s][%(asctime)s][{} %(filename)s:%(lineno)s - %(funcName)s() ] %(message)s".format(
                os.getpid()))

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
