import argparse
import pprint
import typing

import numpy
import matplotlib.pyplot as plt
import pandas
import seaborn

import config
import plugins.makai_event_plugin as analysis
import mongo
import constants


class Incident:
    def __init__(self, incident_id: int, opq_mongo_client: mongo.OpqMongoClient = None):
        opq_mongo_client: mongo.OpqMongoClient = opq_mongo_client if opq_mongo_client is not None else mongo.OpqMongoClient()
        incident_dict = opq_mongo_client.incidents_collection.find_one({"incident_id": incident_id})

        if incident_dict is None:
            print("Incident does not exist", incident_id)
            return

        self.incident_id: int = incident_id
        self.box_id: str = incident_dict["box_id"]
        self.start_timestamp_ms: int = incident_dict["start_timestamp_ms"]
        self.end_timestamp_ms: int = incident_dict["end_timestamp_ms"]
        self.location: str = incident_dict["location"]
        self.measurement_type: mongo.IncidentMeasurementType = mongo.IncidentMeasurementType[
            incident_dict["measurement_type"]]
        self.deviation_from_nominal: float = incident_dict["deviation_from_nominal"]
        self.measurements: typing.List[typing.Dict] = incident_dict["measurements"]
        self.gridfs_filename: str = incident_dict["gridfs_filename"]
        self.classifications: typing.List[mongo.IncidentClassification] = list(
            map(lambda incident_classification: mongo.IncidentClassification[incident_classification],
                incident_dict["classifications"]))
        self.ieee_duration: mongo.IEEEDuration = incident_dict["ieee_duration"]
        self.annotations: typing.List = incident_dict["annotations"]
        self.metadata: typing.Dict = incident_dict["metadata"]

        self.calibrated_waveform = mongo.get_waveform(opq_mongo_client,
                                                      self.gridfs_filename) / mongo.cached_calibration_constant(
            self.box_id)
        self.conf = config.from_env(constants.CONFIG_ENV)
        self.filter_order = int(self.conf["plugins.MakaiEventPlugin.filterOrder"])
        self.cutoff_frequency = float(self.conf["plugins.MakaiEventPlugin.cutoffFrequency"])
        self.samples_per_window = int(constants.SAMPLES_PER_CYCLE) * \
                                  int(self.conf["plugins.MakaiEventPlugin.frequencyWindowCycles"])
        self.down_sample_factor = int(self.conf["plugins.MakaiEventPlugin.frequencyDownSampleRate"])

    def __str__(self):
        return pprint.pformat(self.__dict__)

    def vrms_values(self) -> numpy.ndarray:
        return analysis.vrms_waveform(self.calibrated_waveform)

    def frequency_values(self) -> numpy.ndarray:
        return analysis.frequency_waveform(self.calibrated_waveform, self.filter_order, self.cutoff_frequency,
                                           self.down_sample_factor)


if __name__ == "__main__":
    arg_parser = argparse.ArgumentParser()
    arg_parser.add_argument("incident_id", type=int)

    args = arg_parser.parse_args()

    incident_id = args.incident_id

    incident = Incident(incident_id)

    seaborn.set()

    samples_df = pandas.DataFrame({"x": numpy.arange(0, len(incident.calibrated_waveform)),
                                    "Sample": incident.calibrated_waveform})

    vrms_df = pandas.DataFrame({"x": numpy.arange(0, len(incident.calibrated_waveform), 200),
                                "Vrms": incident.vrms_values()})

    fig, ax = plt.subplots()
    ax2 = ax.twinx()
    seaborn.regplot(x="x", y="Sample", data=samples_df, order=2, ax=ax)
    seaborn.regplot(x="x", y="Vrms", data=vrms_df, order=2, ax=ax2)

    plt.show()


    # mongo_client = mongo.OpqMongoClient()
    # for i in range(1, 500000):
    #     incident = Incident(i, mongo_client)
    #     if len(incident.waveform) > 0:
    #         print(i)
