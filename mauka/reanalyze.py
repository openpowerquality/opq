import argparse
import time

from plugins.routes import Routes
import protobuf.pb_util

import zmq


def reanalyze_event(event_id: int,
                    zmq_push_ep: str):
    try:
        zmq_context: zmq.Context = zmq.Context()
        zmq_pub_socket: zmq.Socket = zmq_context.socket(zmq.PUB)
        zmq_pub_socket.connect(zmq_push_ep)
        time.sleep(0.1)
        makai_event = protobuf.pb_util.build_makai_event("makai_event_bridge", event_id)
        mauka_message_bytes = protobuf.pb_util.serialize_message(makai_event)
        print(makai_event, len(mauka_message_bytes))
        zmq_pub_socket.send_multipart((Routes.makai_event.encode(), mauka_message_bytes))
        print("event_id sent")
    except Exception as e:
        print("Encountered an error %s" % str(e))


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("event_id",
                        type=int)
    parser.add_argument("zmq_push_ep")
    args = parser.parse_args()
    print(args)
    event_id = args.event_id
    zmq_push_ep = args.zmq_push_ep
    reanalyze_event(event_id, zmq_push_ep)
