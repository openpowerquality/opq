"""
This module contains classes and functions for querying and manipulating data within a mongo database.
"""

import collections
import typing

import numpy
import pymongo
import gridfs


def to_s16bit(data: bytes) -> numpy.ndarray:
    """
    Converts raw bytes into an array of 16 bit integers.
    :param data:
    :return:
    """
    return numpy.frombuffer(data, numpy.int16)


def get_box_calibration_constants(mongo_client: pymongo.MongoClient = None, defaults: typing.Dict[int, float] = {}) -> \
typing.Dict[int, float]:
    """
    Loads calibration constants from the mongo database a a dictionary from box id to calibration constant.
    Default values can be passed in if needed.
    :param mongo_client: Optional mongo db opq client
    :param defaults: Default values supplied as a mapping from box id to calibration constant.
    :return: A dictionary mapping of box_id to calibration constant
    """
    _mongo_client = mongo_client if mongo_client is not None else OpqMongoClient()
    calibration_constants = _mongo_client.calibration_constants_collection.find(projection={'_id': False})
    r = {}
    for k, v in defaults.items():
        r[k] = v
    for device_constant in calibration_constants:
        r[device_constant["device_id"]] = device_constant["calibration_constant"]
    return r


def get_data(mongo_client: pymongo.MongoClient, event_data: typing.List[typing.Dict]):
    """
    Attempt to retrieve raw waveform for specific event.
    Updates the event_data pass by reference.
    If raw data is found, this will replace the value stored at the data key with the actual waveform.
    :param mongo_client: The mongo client required to perform the retrieval
    :param event_data: Dictionary of event metadata
    """
    if "data" in event_data:
        data = mongo_client.read_file(event_data["data"])
        event_data["data"] = to_s16bit(data)
    else:
        print("No data pointer in event metadata")


def load_event(event_id: int, mongo_client: pymongo.MongoClient = None) -> typing.Dict[str, typing.Dict]:
    """
    Queries the mongo database and combines all event information from both the events and data collection for a
    specified event.
    :param event_id: The event number to load data from
    :param mongo_client: An optional mongo client to use to make the query.
    :return: A dictionary which contains event and event_data information from mongo. If raw data is available, the
    data field is updated to include the raw data loaded via gridfs.
    """
    _mongo_client = mongo_client if mongo_client is not None else OpqMongoClient()

    events_collection = _mongo_client.get_collection(Collection.EVENTS)
    event = events_collection.find_one({"event_number": event_id})

    data_collection = _mongo_client.get_collection(Collection.DATA)
    event_data = list(data_collection.find({"event_number": event_id}))

    for d in event_data:
        get_data(_mongo_client, d)

    return {"event": event,
            "event_data": event_data}


class BoxEventType:
    """String enumerations and constants for event types"""
    FREQUENCY_DIP = "FREQUENCY_SAG"
    FREQUENCY_SWELL = "FREQUENCY_SWELL"
    VOLTAGE_DIP = "VOLTAGE_SAG"
    VOLTAGE_SWELL = "VOLTAGE_SWELL"
    OTHER = "OTHER"


class Collection:
    """String enumerations and constants for collection names"""
    MEASUREMENTS = "measurements"
    BOX_EVENTS = "boxEvents"
    DATA = "data"
    EVENTS = "events"
    CALIBRATION_CONSTANTS = "CalibrationConstants"


class OpqMongoClient:
    """Convenience mongo client for easily operating on OPQ data"""

    def __init__(self, host: str = "127.0.0.1", port: int = 27017, db: str = "opq"):
        """
        Initializes an OpqMongoClient.
        :param host: Host of mongo database
        :param port: Port of mongo database
        :param db: The name of the database on mongo
        """

        self.client = pymongo.MongoClient(host, port)
        """MongoDB client"""

        self.db = self.client[db]
        """MongoDB"""

        self.fs = gridfs.GridFS(self.db)
        """Access to MongoDB gridfs"""

        self.events_collection = self.get_collection(Collection.EVENTS)
        """Events collections"""

        self.measurements_collection = self.get_collection(Collection.MEASUREMENTS)
        """Measurements collection"""

        self.data_collection = self.get_collection(Collection.DATA)
        """Data collection"""

        self.calibration_constants_collection = self.get_collection(Collection.CALIBRATION_CONSTANTS)
        """Calibration constants collection"""

    def get_collection(self, collection: str):
        """ Returns a mongo collection by name

        Parameters
        ----------
        collection : str
            Name of collection

        Returns
        -------
        A mongo collection

        """
        return self.db[collection]

    def drop_collection(self, collection: str):
        """Drops a collection by name

        Parameters
        ----------
        collection : str
            Name of the collection

        """
        self.db[collection].drop()

    def drop_indexes(self, collection: str):
        """Drop all indexes of a particular named collection

        Parameters
        ----------
        collection : str
            Name of the collection

        Returns
        -------

        """
        self.db[collection].drop_indexes()

    def read_file(self, fid: str) -> bytes:
        """
        Loads a file from gridfs as an array of bytes
        :param fid: The file name to open stored in gridfs
        :return: A list of bytes from reading the file
        """
        return self.fs.find_one({"filename": fid}).read()

    def export_data(self, out_dir: str, start_ts_ms_utc: int, end_ts_ms_utc: int):
        """
        Export CSV data to the specified directory.
        :param out_dir: Diretory to write data files to
        :param start_ts_ms_utc: Start timestamp of when to export data from
        :param end_ts_ms_utc: End timestamp of when to export data to
        """
        measurements = self.measurements_collection.find(
                {"$and": [{"timestamp_ms": {"$gte": start_ts_ms_utc}}, {"timestamp_ms": {"$lte": end_ts_ms_utc}}]},
                {"_id": False})
        device_id_to_measurements = collections.defaultdict(list)

        for measurement in measurements:
            device_id_to_measurements[measurement["device_id"]].append(measurement)

        for device_id, measurements in device_id_to_measurements.items():
            path = out_dir + "/measurements_" + str(device_id) + "_" + str(start_ts_ms_utc) + "_" + str(
                    end_ts_ms_utc) + ".txt"
            with open(path, "w") as out:
                out.writelines(
                        map(lambda m: str(m["timestamp_ms"]) + "," + str(m["frequency"]) + "," + str(
                                m["voltage"]) + "\n",
                            measurements))

        event_ids = map(lambda event: event["event_number"], self.events_collection.find(
                {"$and": [{"event_start": {"$gte": start_ts_ms_utc}}, {"event_start": {"$lte": end_ts_ms_utc}}]},
                ["event_number"]))
        events = map(lambda event_id: load_event(event_id, self), event_ids)

        for event in events:
            event_meta = event["event"]
            event_data = event["event_data"]
            event_number = str(event_meta["event_number"])
            path = out_dir + "/event_" + event_number + ".txt"
            with open(path, "w") as out:
                out.write(str(event_meta["type"]) + "," + str(event_meta["description"]) + "," + str(
                        event_meta["boxes_triggered"]) + "," +
                          str(event_meta["boxes_received"]) + "," + str(event_meta["event_start"]) + "," + str(
                        event_meta["event_end"]) + "\n")
                # out.write(str(event_data) + "\n")
                if len(event_data) > 0:
                    for ed in event_data:
                        out.write(
                                str(ed["box_id"]) + "," + str(len(ed["data"])) + "," + str(
                                        ed["event_start"]) + "," + str(
                                        ed["event_end"]) + "\n")
                        for datum in ed["data"]:
                            out.write(str(datum) + "\n")


def get_default_client(mongo_client: OpqMongoClient = None) -> OpqMongoClient:
    """
    Creates a new mongo client or reuses a passed in mongo client
    :param mongo_client: Mongo client
    :return: Mongo client
    """
    if mongo_client is None:
        return OpqMongoClient()
    else:
        return mongo_client
