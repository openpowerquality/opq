import multiprocessing
import protobuf.util
import time
import typing

import zmq


class MaukaTestException(Exception):
    pass

current_milli_time = lambda: int(round(time.time() * 1000))

def produce_measurement(i):
    trigger_msg = protobuf.util.encode_trigger_message(i, current_milli_time(), 60.0, 120.0)
    return ("".encode(), trigger_msg)

def start_mock_makai(interface: str,
                     producer: typing.Callable,
                     interval_ms: int,
                     max_runs: int):

    def _start_mock_makai():
        zmq_context = zmq.Context()
        zmq_producer_socket = zmq_context.socket(zmq.PUB)
        zmq_producer_socket.bind(interface)

        for i in range(max_runs):
            zmq_producer_socket.send_multipart(producer(i))
            time.sleep(interval_ms / 1000.0)

        raise MaukaTestException("Makai died after {} max messages were sent".format(max_runs))

    process = multiprocessing.Process(target=_start_mock_makai)
    process.start()
    return process