#!/usr/bin/env python3

import argparse
import typing

import matplotlib

matplotlib.use('TkAgg')
import matplotlib.pyplot as plt

import numpy
import tkinter

import analysis
import analysis.thd
import analysis.itic
import constants
import datetime_util
import mongo.mongo


def in_args(name: str, args: typing.Dict) -> bool:
    return name in args and args[name] is not None


def array_slice_args(args: typing.Dict, data: numpy.ndarray) -> typing.Tuple[int, int]:
    if not in_args("slice", args) or len(args["slice"]) != 2:
        return 0, len(data)
    else:
        slices = args["slice"]
        start = slices[0]
        end = slices[1]
        return start, end


def array_slice(args: typing.Dict, data: numpy.ndarray) -> numpy.ndarray:
    if not in_args("slice", args):
        return data
    else:
        start, end = array_slice_args(args, data)
        return data[start:end]


def plot_event(args: typing.Dict, mongo_client: mongo.mongo.OpqMongoClient = None):
    client = mongo.mongo.get_default_client(mongo_client)

    # Make sure there is data to plot
    event_id = args["event_id"]

    secondary = args["secondary"]

    total_box_events = client.box_events_collection.count({"event_id": event_id})
    if total_box_events <= 0:
        print("No data to plot for event with event_id", event_id)
        return

    # Let's go ahead and load the waveforms for each box_event and perform calibration in the process
    box_id_to_waveform = {}
    box_id_to_secondary = {}
    box_id_to_box_event = {}
    min_waveform = 99999
    max_waveform = -min_waveform
    min_secondary = 99999
    max_max_secondary = -min_secondary

    box_event_query = {"event_id": event_id}
    if in_args("box_ids", args):
        box_ids = args["box_ids"].split(",")
        box_event_query["box_id"] = {"$in": box_ids}

    for box_event in client.box_events_collection.find(box_event_query):
        box_id = box_event["box_id"]
        box_id_to_box_event[box_id] = box_event
        waveform = analysis.waveform_from_file(client.fs, box_event["data_fs_filename"])
        calibration_constant = constants.cached_calibration_constant(box_id)
        calibrated_waveform = analysis.calibrate_waveform(waveform, calibration_constant)
        sliced_waveform = array_slice(args, calibrated_waveform)
        min_waveform = numpy.min([min_waveform, numpy.min(sliced_waveform)])
        max_waveform = numpy.max([max_waveform, numpy.max(sliced_waveform)])
        box_id_to_waveform[box_id] = sliced_waveform

        if secondary == "Vrms":
            secondary_waveform = analysis.vrms_waveform(sliced_waveform)
        elif secondary == "THD":
            secondary_waveform = analysis.thd.thd_waveform(sliced_waveform)
        else:
            secondary_waveform = numpy.array([])

        min_secondary = numpy.min([min_secondary, numpy.min(secondary_waveform)])
        max_max_secondary = numpy.max([max_max_secondary, numpy.max(secondary_waveform)])
        box_id_to_secondary[box_id] = secondary_waveform



    total_box_ids = len(box_id_to_waveform)
    title = "event_id {}".format(event_id)
    fig = plt.figure(title, figsize=(13, total_box_ids * 2.5))

    i = 1
    for box_id, waveform in box_id_to_waveform.items():
        box_event = box_id_to_box_event[box_id]
        start, end = array_slice_args(args, waveform)
        xs = numpy.array(range(start, end))
        ax_waveform = fig.add_subplot(total_box_ids, 1, i)
        ax_waveform.plot(xs, waveform, "b-", label="Calibrated Voltage")
        ax_waveform.set_title("box_id {} @ {}".format(box_id, datetime_util.datetime_from_epoch_ms(box_event["event_start_timestamp_ms"]).isoformat()))
        ax_waveform.set_ylabel("Calibrated Voltage")
        ax_waveform.set_xlabel("Samples @ {} Hz".format(int(constants.SAMPLE_RATE_HZ)))

        ax_secondary = ax_waveform.twinx()

        if in_args("fixed_y", args) and args["fixed_y"]:
            ax_waveform.set_ylim(bottom=min_waveform - 1, top=max_waveform + 1)
            ax_secondary.set_ylim(bottom=min_secondary - .5, top=max_max_secondary + .5)

        ax_secondary.plot(xs[0::constants.SAMPLES_PER_CYCLE], box_id_to_secondary[box_id], "r-", label=secondary)
        ax_secondary.set_ylabel(secondary)

        i += 1

    if in_args("save_file", args):
        fig.savefig(args["save_file"])

    fig.tight_layout()
    fig.subplots_adjust(top=0.87)
    fig.suptitle(title)
    fig.legend()
    fig.show()
    tkinter.mainloop()


if __name__ == "__main__":
    parser = argparse.ArgumentParser(prog="python3 -m analysis.plotter",
                                     description="Utility for plotting OPQ events.")

    parser.add_argument("event_id",
                        help="event_id to plot",
                        type=int)

    parser.add_argument("--box-ids", "-b",
                        help="only plot provided box ids (comma separated)")

    parser.add_argument("--slice", "-s",
                        help="start and end index into data",
                        nargs=2,
                        type=int)

    parser.add_argument("--vrms",
                        help="plot Vrms on secondary axis",
                        dest="secondary",
                        action="store_const",
                        default="Vrms",
                        const="Vrms")

    parser.add_argument("--thd",
                        help="plot THD on secondary axis",
                        dest="secondary",
                        action="store_const",
                        const="THD")

    parser.add_argument("--fixed-y", "-y",
                        help="all plots will scale the y-axis to the same scale",
                        action="store_true")

    parser.add_argument("--save-file", "-f",
                        help="save a file to the specified path")

    args = parser.parse_args()
    # print(args)
    plot_event(vars(args))
