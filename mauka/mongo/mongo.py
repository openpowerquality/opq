import collections

import numpy
import pymongo
import gridfs

def to_s16bit(data):
    return numpy.frombuffer(data, numpy.int16)


def get_data(mongo_client, event_data):
    if "data" in event_data:
        data = mongo_client.read_file(event_data["data"])
        event_data["data"] = to_s16bit(data)
    else:
        print("No data pointer in event metadata")


def load_event(event_id: int, mongo_client=None):
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


class OpqMongoClient:
    """Convenience mongo client for easily operating on OPQ data"""
    def __init__(self, host="127.0.0.1", port=27017, db="opq"):
        self.client = pymongo.MongoClient(host, port)
        self.db = self.client[db]
        self.fs = gridfs.GridFS(self.db)

        self.events_collection = self.get_collection(Collection.EVENTS)
        self.measurements_collection = self.get_collection(Collection.MEASUREMENTS)
        self.data_collection = self.get_collection(Collection.DATA)

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

    def export_data(self, out_dir: str, start_ts_ms_utc: int, end_ts_ms_utc: int):
        # measurements = self.measurements_collection.find({"$and": [{"timestamp_ms": {"$gte": start_ts_ms_utc}}, {"timestamp_ms": {"$lte": end_ts_ms_utc}}]}, {"_id": False})
        # device_id_to_measurements = collections.defaultdict(list)

        # for measurement in measurements:
        #     device_id_to_measurements[measurement["device_id"]].append(measurement)
        #
        # for device_id, measurements in device_id_to_measurements.items():
        #     path = out_dir + "/measurements_" + str(device_id) + "_" + str(start_ts_ms_utc) + "_" + str(end_ts_ms_utc) + ".txt"
        #     with open(path, "w") as out:
        #         out.writelines(map(lambda m: str(m["timestamp_ms"]) + "," + str(m["frequency"]) + "," + str(m["voltage"]) + "\n", measurements))

        event_ids = map(lambda event: event["event_number"], self.events_collection.find({"$and": [{"event_start": {"$gte": start_ts_ms_utc}}, {"event_start": {"$lte": end_ts_ms_utc}}]}, ["event_number"]))
        events = map(lambda event_id: load_event(event_id, self), event_ids)

        for event in events:
            event_meta = event["event"]
            event_data = event["event_data"]
            event_number = str(event_meta["event_number"])
            path = out_dir + "/event_" + event_number + ".txt"
            with open(path, "w") as out:
                out.write(str(event_meta["type"]) + "," + str(event_meta["description"]) + "," + str(event_meta["boxes_triggered"]) + "," +
                          str(event_meta["boxes_received"]) + "," + str(event_meta["event_start"]) + "," + str(event_meta["event_end"]) + "\n")
                # out.write(str(event_data) + "\n")
                if len(event_data) > 0:
                    for ed in event_data:
                        out.write(str(ed["box_id"]) + " " + str(len(ed["data"])) + "\n")
                        for datum in ed["data"]:
                            out.write(str(datum) + "\n")


if __name__ == "__main__":
    mongo_client = OpqMongoClient()

    start_ts_ms_utc = 1508781600000 # Oct 23 8AM HST
    end_ts_ms_utc   = 1508868000000 # Oct 24 8AM HST

    mongo_client.export_data("/home/anthony/Development/opq/mauka/scrap", start_ts_ms_utc, end_ts_ms_utc)

