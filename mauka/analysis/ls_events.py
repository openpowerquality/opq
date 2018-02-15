#!/usr/bin/env python3

import argparse
import subprocess
import typing

import datetime_util
import mongo.mongo


def safe_get(dict: typing.Dict, k: str, default: typing.Union[str, int, float] = "") -> typing.Union[str, int, float]:
    if k in dict and dict[k] is not None:
        return dict[k]
    else:
        return default


def format_box_event(box_event: typing.Dict) -> str:
    return "[{}:{:.3f}:{}]".format(safe_get(box_event, "box_id"), safe_get(box_event, "thd", 0.0),
                                   safe_get(box_event, "itic"))


def format_event(event: typing.Dict, box_events: typing.List[typing.Dict]) -> str:
    return "{:5}\t{}\t{}\t{}".format(
        event["event_id"],
        datetime_util.datetime_from_epoch_ms(event["target_event_start_timestamp_ms"]).isoformat(),
        event["type"],
        ",".join(map(format_box_event, box_events))
    )


def recent_events(skip: int = 0, max_events: int = 20, mongo_client: mongo.mongo.OpqMongoClient = None):
    client = mongo.mongo.get_default_client(mongo_client)

    for event in client.events_collection.find().skip(skip).limit(max_events).sort("event_id", -1):
        box_events = client.box_events_collection.find({"event_id": event["event_id"]})
        print(format_event(event, box_events))


def is_int(s: str) -> bool:
    try:
        int(s)
        return True
    except ValueError:
        return False


def start_recent_events_loop(skip: int = 0, max_events: int = 20, mongo_client: mongo.mongo.OpqMongoClient = None):
    client = mongo.mongo.get_default_client(mongo_client)
    recent_events(skip, max_events, client)
    i = max_events
    while True:
        io = input("<Return> for more results. 'exit' to exit ls_events> ")
        if io == "exit":
            break
        elif is_int(io):
            subprocess.call(["python3", "-m", "analysis.plotter", str(io)])
            continue
        else:
            recent_events(i, max_events, client)
            i += max_events


def handle_args(args: typing.Dict, mongo_client: mongo.mongo.OpqMongoClient = None):
    if args["m"]:
        start_recent_events_loop(args["s"], args["l"], mongo_client)
    else:
        recent_events(args["s"], args["l"], mongo_client)


if __name__ == "__main__":
    parser = argparse.ArgumentParser(prog="python3 -m analysis.ls_events",
                                     description="This script displays a list of events")

    parser.add_argument("-l",
                        help="Display last n events (default: 20)",
                        type=int,
                        default=30)

    parser.add_argument("-m",
                        help="Instead of exiting, display a prompt to scroll through more events",
                        action="store_true")

    parser.add_argument("-s",
                        help="Skip n events",
                        type=int,
                        default=0)

    args = vars(parser.parse_args())
    mongo_client = mongo.mongo.get_default_client()
    handle_args(args, mongo_client)
