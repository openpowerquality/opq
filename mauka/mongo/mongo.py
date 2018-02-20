"""
This module contains classes and functions for querying and manipulating data within a mongo database.
"""
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


class BoxEventType:
    """String enumerations and constants for event types"""
    FREQUENCY_DIP = "FREQUENCY_SAG"
    FREQUENCY_SWELL = "FREQUENCY_SWELL"
    VOLTAGE_DIP = "VOLTAGE_SAG"
    VOLTAGE_SWELL = "VOLTAGE_SWELL"
    THD = "THD"
    OTHER = "OTHER"


class Collection:
    """String enumerations and constants for collection names"""
    MEASUREMENTS = "measurements"
    EVENTS = "events"
    BOX_EVENTS = "box_events"
    OPQ_BOXES = "opq_boxes"


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

        self.box_events_collection = self.get_collection(Collection.BOX_EVENTS)
        """Box events collection"""

        self.opq_boxes_collection = self.get_collection(Collection.OPQ_BOXES)
        """Opq boxes collection"""

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


def get_waveform(mongo_client: OpqMongoClient, data_fs_filename: str) -> numpy.ndarray:
    data = mongo_client.read_file(data_fs_filename)
    waveform = to_s16bit(data)
    return waveform


def get_box_calibration_constants(mongo_client: OpqMongoClient = None, defaults: typing.Dict[int, float] = {}) -> \
        typing.Dict[int, float]:
    """
    Loads calibration constants from the mongo database a a dictionary from box id to calibration constant.
    Default values can be passed in if needed.
    :param mongo_client: Optional mongo db opq client
    :param defaults: Default values supplied as a mapping from box id to calibration constant.
    :return: A dictionary mapping of box_id to calibration constant
    """
    _mongo_client = mongo_client if mongo_client is not None else OpqMongoClient()
    opq_boxes = _mongo_client.opq_boxes_collection.find(projection={'_id': False,
                                                                     "calibration_constant": True,
                                                                     "box_id": True})
    r = {}
    for k, v in defaults.items():
        r[k] = v
    for opq_box in opq_boxes:
        r[opq_box["box_id"]] = opq_box["calibration_constant"]
    return r


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
