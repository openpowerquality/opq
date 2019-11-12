from datetime import datetime as dt
from typing import List, Optional, Tuple

import reports

import mauka_native_py as native
import matplotlib.pyplot as plt
import numpy as np
import pymongo


def plot_incident(incident_id: int,
                  report_dir: str,
                  mongo_client: pymongo.MongoClient,
                  start_time_ms: Optional[float] = None,
                  end_time_ms: Optional[float] = None):
    incidents_coll: pymongo.collection.Collection = mongo_client["opq"]["incidents"]
    incident = incidents_coll.find_one({"incident_id": incident_id})
    event_id: int = incident["event_id"]
    box_id: str = incident["box_id"]
    start_timestamp_ms: int = incident["start_timestamp_ms"]
    gridfs_filename: str = incident["gridfs_filename"]
    classification: str = incident["classifications"][0]
    waveform = reports.calib_waveform(gridfs_filename, box_id, mongo_client)
    waveform_start_time_ms = start_timestamp_ms

    fig, axes = plt.subplots(4, 1, figsize=(16, 9))
    fig: plt.Figure = fig
    axes: List[plt.Axes] = axes

    fig.suptitle("Incident #%d (%s) and Event #%d for OPQ Box %s (%s) @ %s UTC" % (
        incident_id,
        classification,
        event_id,
        box_id,
        reports.box_to_location[box_id],
        dt.utcfromtimestamp(start_timestamp_ms / 1000.0).strftime("%Y-%m-%d %H:%M:%S")
    ))

    # Waveform and Vrms on first row
    sample_timestamps = map(lambda i: waveform_start_time_ms + reports.sample_to_ms(i), range(len(waveform)))
    sample_dts = list(map(lambda ts: dt.utcfromtimestamp(ts / 1000.0), sample_timestamps))

    # Plot waveform
    ax_waveform = axes[0]
    ax_waveform.plot(sample_dts, waveform, color="blue")
    ax_waveform.set_title("Incident Voltage and $V_{RMS}$")
    ax_waveform.set_ylabel("Voltage")
    ax_waveform.tick_params(axis="y", colors="blue")
    ax_waveform.yaxis.label.set_color("blue")
    ax_waveform.set_xlim(xmin=min(sample_dts), xmax=max(sample_dts))

    # Plot Vrms
    per_cycle_dts = sample_dts[0::200]
    ax_vrms: plt.Axes = ax_waveform.twinx()
    ax_vrms.plot(per_cycle_dts, reports.vrms_waveform(waveform), color="red")
    ax_vrms.set_ylabel("$V_{RMS}$")
    ax_vrms.tick_params(axis="y", colors="red")
    ax_vrms.yaxis.label.set_color("red")

    # Frequency and THD on second row
    # Plot frequency
    ax_freq: plt.Axes = axes[1]
    freqs = reports.frequency_per_cycle(waveform)
    ax_freq.plot(per_cycle_dts[:len(freqs)], freqs, color="blue")
    ax_freq.set_title("Incident Frequency and Percent THD")
    ax_freq.set_ylabel("Frequency (Hz)")
    ax_freq.tick_params(axis="y", colors="blue")
    ax_freq.yaxis.label.set_color("blue")
    ax_freq.set_xlim(xmin=min(sample_dts), xmax=max(sample_dts))

    ax_thd: plt.Axes = ax_freq.twinx()
    thds = native.percent_thd_per_cycle(waveform)
    ax_thd.plot(per_cycle_dts[:len(thds)], thds, color="red")
    ax_thd.set_ylabel("Percent THD")
    ax_thd.tick_params(axis="y", colors="red")
    ax_thd.yaxis.label.set_color("red")

    # Event Plots
    # Event Waveform
    box_events_coll: pymongo.collection.Collection = mongo_client["opq"]["box_events"]
    box_event = box_events_coll.find_one({"event_id": event_id,
                                          "box_id": box_id})

    event_start_timestamp_ms: int = box_event["event_start_timestamp_ms"]
    data_fs_filename: str = box_event["data_fs_filename"]
    event_waveform = reports.calib_waveform(data_fs_filename, box_id, mongo_client)
    event_timestamps = map(lambda i: event_start_timestamp_ms + reports.sample_to_ms(i) , range(len(event_waveform)))
    event_dts = list(map(lambda ts: dt.utcfromtimestamp(ts / 1000.0), event_timestamps))

    ax_event_waveform = axes[2]
    ax_event_waveform.set_title("Event Voltage and $V_{RMS}$")
    ax_event_waveform.plot(event_dts, event_waveform, color="blue")
    ax_event_waveform.set_ylabel("Voltage")
    ax_event_waveform.tick_params(axis="y", colors="blue")
    ax_event_waveform.yaxis.label.set_color("blue")
    ax_event_waveform.set_xlim(xmin=min(event_dts), xmax=max(event_dts))

    # Event Vrms
    per_cycle_event_dts = event_dts[0::200]
    ax_event_vrms: plt.Axes = ax_event_waveform.twinx()
    ax_event_vrms.plot(per_cycle_event_dts, reports.vrms_waveform(event_waveform), color="red")
    ax_event_vrms.set_ylabel("$V_{RMS}$")
    ax_event_vrms.tick_params(axis="y", colors="red")
    ax_event_vrms.yaxis.label.set_color("red")

    # Event freq and thd
    # Event freq
    ax_event_freq: plt.Axes = axes[3]
    freqs = reports.frequency_per_cycle(event_waveform)
    ax_event_freq.plot(per_cycle_event_dts[:len(freqs)], freqs, color="blue")
    ax_event_freq.set_title("Event Frequency and Percent THD")
    ax_event_freq.set_ylabel("Frequency (Hz)")
    ax_event_freq.tick_params(axis="y", colors="blue")
    ax_event_freq.yaxis.label.set_color("blue")
    ax_event_freq.set_xlim(xmin=min(event_dts), xmax=max(event_dts))

    ax_event_thd: plt.Axes = ax_event_freq.twinx()
    thds = native.percent_thd_per_cycle(event_waveform)
    ax_event_thd.plot(per_cycle_event_dts[:len(thds)], thds, color="red")
    ax_event_thd.set_ylabel("Percent THD")
    ax_event_thd.tick_params(axis="y", colors="red")
    ax_event_thd.yaxis.label.set_color("red")


    plt.subplots_adjust(hspace=.5)
    plt.savefig("%s/incident-%d.png" % (
        report_dir,
        incident_id
    ))


if __name__ == "__main__":
    mongo_client = pymongo.MongoClient()
    waveform = reports.calib_waveform("incident_92169", "1025", mongo_client)
    # plot_waveform(waveform, 1573259173006, "Test", ".")
    plot_incident(92169, ".", mongo_client)
