from datetime import timedelta as td
from datetime import datetime as dt
from typing import List, Optional, Tuple

import reports

import mauka_native_py as native
import matplotlib.pyplot as plt
import numpy as np
import pymongo


class IncidentData:
    def __init__(self,
                 incident_id: int,
                 mongo_client: pymongo.MongoClient,
                 incident_buffer_start_c: float = 2.0,
                 incident_buffer_end_c: float = 2.0):
        incidents_coll: pymongo.collection.Collection = mongo_client["opq"]["incidents"]
        incident = incidents_coll.find_one({"incident_id": incident_id})
        self.event_id: int = incident["event_id"]
        self.box_id: str = incident["box_id"]
        self.incident_start_timestamp_ms = incident["start_timestamp_ms"]
        self.incident_end_timestamp_ms = incident["end_timestamp_ms"]
        self.incident_start_dt = dt.utcfromtimestamp(self.incident_start_timestamp_ms / 1000.0)
        self.incident_end_dt = dt.utcfromtimestamp(self.incident_end_timestamp_ms / 1000.0)
        self.classification = incident["classifications"][0]

        box_events_coll: pymongo.collection.Collection = mongo_client["opq"]["box_events"]
        box_event = box_events_coll.find_one({"event_id": self.event_id,
                                              "box_id": self.box_id})

        self.event_start_timestamp_ms = box_event["event_start_timestamp_ms"]
        self.event_end_timestamp_ms = box_event["event_end_timestamp_ms"]
        event_data_fs_filename = box_event["data_fs_filename"]

        self.event_waveform = reports.calib_waveform(event_data_fs_filename, self.box_id, mongo_client)
        self.event_waveform_timestamps = list(map(lambda i: self.event_start_timestamp_ms + reports.sample_to_ms(i),
                                                  range(len(self.event_waveform))))

        self.event_waveform_dts = list(map(lambda ts: dt.utcfromtimestamp(ts / 1000.0), self.event_waveform_timestamps))

        self.event_vrms_values = reports.vrms_waveform(self.event_waveform)
        self.event_vrms_dts = self.event_waveform_dts[0::200]

        self.event_freq_values = reports.frequency_per_cycle(self.event_waveform)
        self.event_freq_dts = self.event_waveform_dts[0::200]

        self.event_thd_values = native.percent_thd_per_cycle(self.event_waveform)
        self.event_thd_dts = self.event_waveform_dts[0::200]

        # Incident data
        incident_start_delta_ms = self.incident_start_timestamp_ms - self.event_start_timestamp_ms
        incident_end_delta_ms = self.incident_end_timestamp_ms - self.event_start_timestamp_ms
        incident_start_idx = max(0, int(reports.ms_to_samples(incident_start_delta_ms) - (incident_buffer_start_c * 200)))
        incident_end_idx = min(len(self.event_waveform), int(reports.ms_to_samples(incident_end_delta_ms) + (incident_buffer_end_c * 200)))

        print(incident_start_idx, incident_end_idx)

        self.incident_waveform = self.event_waveform[incident_start_idx: incident_end_idx]
        self.incident_waveform_dts = self.event_waveform_dts[incident_start_idx: incident_end_idx]

        incident_c_start_idx = int(reports.samples_to_cycles(incident_start_idx))
        incident_c_end_idx = int(reports.samples_to_cycles(incident_end_idx)) + 2

        self.incident_vrms_values = self.event_vrms_values[incident_c_start_idx: incident_c_end_idx]
        self.incident_vrms_dts = self.event_vrms_dts[incident_c_start_idx: incident_c_end_idx]

        self.incident_freq_values = self.event_freq_values[incident_c_start_idx: incident_c_end_idx]
        self.incident_freq_dts = self.event_freq_dts[incident_c_start_idx: incident_c_end_idx]

        self.incident_thd_values = self.event_thd_values[incident_c_start_idx: incident_c_end_idx]
        self.incident_thd_dts = self.event_thd_dts[incident_c_start_idx: incident_c_end_idx]


def plot_incident(incident_id: int,
                  report_dir: str,
                  mongo_client: pymongo.MongoClient,
                  plot_incident_fft_fit: bool = False):
    incident_data = IncidentData(incident_id, mongo_client)

    fig, axes = plt.subplots(4, 1, figsize=(16, 9))
    fig: plt.Figure = fig
    axes: List[plt.Axes] = axes

    fig.suptitle("Incident #%d (%s) and Event #%d for OPQ Box %s (%s) @ %s UTC" % (
        incident_id,
        incident_data.classification,
        incident_data.event_id,
        incident_data.box_id,
        reports.box_to_location[incident_data.box_id],
        dt.utcfromtimestamp(incident_data.event_start_timestamp_ms / 1000.0).strftime("%Y-%m-%d %H:%M:%S")
    ))

    # Incident Waveform / Vrms
    ax_incident_waveform = axes[0]
    ax_incident_waveform.axvline(x=incident_data.incident_start_dt,
                                 color="red",
                                 linewidth=1)
    ax_incident_waveform.axvline(x=incident_data.incident_end_dt,
                                 color="red",
                                 linewidth=1)
    ax_incident_waveform.plot(incident_data.incident_waveform_dts, incident_data.incident_waveform, color="blue")
    ax_incident_waveform.set_title("Incident #%d Voltage and $V_{RMS}$" % incident_id)
    ax_incident_waveform.set_ylabel("Voltage")
    ax_incident_waveform.tick_params(axis="y", colors="blue")
    ax_incident_waveform.yaxis.label.set_color("blue")
    ax_incident_waveform.set_xlim(xmin=incident_data.incident_waveform_dts[0] - td(seconds=1.0/120.0),
                                  xmax=incident_data.incident_waveform_dts[-1] + td(seconds=1.0/120.0))

    ax_incident_vrms: plt.Axes = ax_incident_waveform.twinx()
    ax_incident_vrms.plot(incident_data.incident_vrms_dts, incident_data.incident_vrms_values, color="black")
    ax_incident_vrms.set_ylabel("$V_{RMS}$")
    ax_incident_vrms.tick_params(axis="y", colors="black")
    ax_incident_vrms.yaxis.label.set_color("black")

    # Incident Frequency / THD
    ax_incident_freq = axes[1]
    ax_incident_freq.axvline(x=incident_data.incident_start_dt,
                             color="red",
                             linewidth=1)
    ax_incident_freq.axvline(x=incident_data.incident_end_dt,
                             color="red",
                             linewidth=1)
    ax_incident_freq.plot(incident_data.incident_freq_dts, incident_data.incident_freq_values, color="blue")
    ax_incident_freq.set_title("Incident #%d Frequency and Percent THD" % incident_id)
    ax_incident_freq.set_ylabel("Frequency (Hz)")
    ax_incident_freq.tick_params(axis="y", colors="blue")
    ax_incident_freq.yaxis.label.set_color("blue")
    ax_incident_freq.set_xlim(xmin=incident_data.incident_waveform_dts[0] - td(seconds=1.0/120.0),
                              xmax=incident_data.incident_waveform_dts[-1] + td(seconds=1.0/120.0))

    ax_incident_thd = ax_incident_freq.twinx()
    ax_incident_thd.plot(incident_data.incident_thd_dts, incident_data.incident_thd_values, color="black")
    ax_incident_thd.set_ylabel("Percent THD")
    ax_incident_thd.tick_params(axis="y", colors="black")
    ax_incident_thd.yaxis.label.set_color("black")

    # Event Waveform / Vrms
    ax_event_waveform = axes[2]
    ax_event_waveform.axvline(x=incident_data.incident_start_dt,
                              color="red",
                              linewidth=1)
    ax_event_waveform.axvline(x=incident_data.incident_end_dt,
                              color="red",
                              linewidth=1)
    ax_event_waveform.plot(incident_data.event_waveform_dts, incident_data.event_waveform, color="blue")
    ax_event_waveform.set_title("Event #%d Voltage and $V_{RMS}$" % incident_data.event_id)
    ax_event_waveform.set_ylabel("Voltage")
    ax_event_waveform.tick_params(axis="y", colors="blue")
    ax_event_waveform.yaxis.label.set_color("blue")
    ax_event_waveform.set_xlim(xmin=incident_data.event_waveform_dts[0] - td(seconds=1.0/120.0),
                               xmax=incident_data.event_waveform_dts[-1] + td(seconds=1.0/120.0))

    ax_event_vrms: plt.Axes = ax_event_waveform.twinx()
    ax_event_vrms.plot(incident_data.event_vrms_dts, incident_data.event_vrms_values, color="black")
    ax_event_vrms.set_ylabel("$V_{RMS}$")
    ax_event_vrms.tick_params(axis="y", colors="black")
    ax_event_vrms.yaxis.label.set_color("black")

    # Event Frequency / THD
    ax_event_freqs = axes[3]
    ax_event_freqs.axvline(x=incident_data.incident_start_dt,
                           color="red",
                           linewidth=1)
    ax_event_freqs.axvline(x=incident_data.incident_end_dt,
                           color="red",
                           linewidth=1)

    ax_event_freqs.plot(incident_data.event_freq_dts, incident_data.event_freq_values, color="blue")
    ax_event_freqs.set_title("Event #%d Frequency and Percent THD" % incident_data.event_id)
    ax_event_freqs.set_ylabel("Frequency (Hz)")
    ax_event_freqs.tick_params(axis="y", colors="blue")
    ax_event_freqs.yaxis.label.set_color("blue")
    ax_event_freqs.set_xlim(xmin=incident_data.event_waveform_dts[0] - td(seconds=1.0/120.0),
                            xmax=incident_data.event_waveform_dts[-1] + td(seconds=1.0/120.0))

    ax_event_thds: plt.Axes = ax_event_freqs.twinx()
    ax_event_thds.plot(incident_data.event_thd_dts, incident_data.event_thd_values, color="black")
    ax_event_thds.set_ylabel("Percent THD")
    ax_event_thds.tick_params(axis="y", colors="black")
    ax_event_thds.yaxis.label.set_color("black")

    plt.subplots_adjust(hspace=.5)
    plt.savefig("%s/incident-%d.png" % (
        report_dir,
        incident_id
    ))

    if plot_incident_fft_fit:
        reports.frequency_per_cycle(incident_data.incident_waveform, True)


if __name__ == "__main__":
    mongo_client = pymongo.MongoClient()
    # waveform = reports.calib_waveform("incident_92169", "1025", mongo_client)
    # plot_waveform(waveform, 1573259173006, "Test", ".")
    plot_incident(101664, ".", mongo_client, True)

