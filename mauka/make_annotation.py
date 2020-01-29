import argparse
import time
from typing import List

import zmq

from plugins.routes import Routes
import protobuf.mauka_pb2 as mauka_pb2
import protobuf.pb_util as pb_util


def insert_annotation_into_mauka(start_ts_ms: int,
                                 end_ts_ms: int,
                                 incident_ids: List[int],
                                 event_ids: List[int],
                                 annotation: str) -> None:
    try:
        zmq_context: zmq.Context = zmq.Context()
        zmq_pub_socket: zmq.Socket = zmq_context.socket(zmq.PUB)
        zmq_pub_socket.connect("tcp://localhost:9882")

        time.sleep(0.1)

        annotation_request: mauka_pb2.MaukaMessage = pb_util.build_annotation_request("make_annotation.py",
                                                                                      int(time.time()),
                                                                                      incident_ids if incident_ids is not None else [],
                                                                                      event_ids if event_ids is not None else [],
                                                                                      annotation,
                                                                                      start_ts_ms,
                                                                                      end_ts_ms)
        annotation_request_bytes: bytes = pb_util.serialize_message(annotation_request)
        zmq_pub_socket.send_multipart((Routes.annotation_request.encode(), annotation_request_bytes))
    except Exception as e:
        print(f"Encountered an error: {str(e)}")


def main() -> None:
    parser: argparse.ArgumentParser = argparse.ArgumentParser()

    parser.add_argument("start_ts_ms",
                        type=int)

    parser.add_argument("end_ts_ms",
                        type=int)

    parser.add_argument("--incident_ids",
                        nargs="*",
                        type=int)

    parser.add_argument("--event_ids",
                        nargs="*",
                        type=int)

    parser.add_argument("--annotation",
                        required=True,
                        type=str)

    args = parser.parse_args()

    print(args)

    insert_annotation_into_mauka(args.start_ts_ms,
                                 args.end_ts_ms,
                                 args.incident_ids,
                                 args.event_ids,
                                 args.annotation)

    print("Annotation inserted.")


if __name__ == "__main__":
    main()
