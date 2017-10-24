import pymongo
import gridfs


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


class OpqMongoClient:
    """Convenience mongo client for easily operating on OPQ data"""
    def __init__(self, host="127.0.0.1", port=27017, db="opq"):
        self.client = pymongo.MongoClient(host, port)
        self.db = self.client[db]
        self.fs = gridfs.GridFS(self.db)

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

    def read_file(self, fid):
        return self.fs.find_one({"filename": fid}).read()

