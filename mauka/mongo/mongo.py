import pymongo


class BoxEventType:
    FREQUENCY_DIP = "FREQUENCY_SAG"
    FREQUENCY_SWELL = "FREQUENCY_SWELL"
    VOLTAGE_DIP = "VOLTAGE_SAG"
    VOLTAGE_SWELL = "VOLTAGE_SWELL"


class Collection:
    MEASUREMENTS = "measurements"
    BOX_EVENTS = "boxEvents"
    DATA = "data"


class OpqMongoClient:
    def __init__(self, host="127.0.0.1", port=27017, db="opq"):
        self.client = pymongo.MongoClient(host, port)
        self.db = self.client[db]

    def get_collection(self, collection):
        return self.db[collection]

    def drop_collection(self, collection):
        self.db[collection].drop()

    def drop_indexes(self, collection):
        self.db[collection].drop_indexes()

    def display_indexes(self):
        for i in self.db[Collection.MEASUREMENTS].list_indexes():
            print(i)
