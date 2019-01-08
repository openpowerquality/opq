import pymongo

import time


def get_db_client(client: pymongo.MongoClient = None) -> pymongo.MongoClient:
    if client is None:
        return pymongo.MongoClient()
    else:
        return client

def active_device_count(client: pymongo.MongoClient = None) -> int:
    db_client = get_db_client(client)
    opq_db = db_client["opq"]
    opq_boxes_collection = opq_db["opq_boxes"]
    box_ids = list(map(lambda obj: obj["box_id"], opq_boxes_collection.find({}, ["box_id"])))

    # Look up measurements for the past minute and check if we've received one for each of the available box ids
    measurements_collection = opq_db["measurements"]
    now_ms = int(time.time()) * 1000
    one_min_ago_ms = now_ms - 60000
    measurements = measurements_collection.find({"timestamp_ms": {"$gt": one_min_ago_ms,
                                                                  "$lt": now_ms}},
                                                ["box_id"])
    return len(set(map(lambda obj: obj["box_id"], measurements)))


def instantaneous_measurement_metrics(client: pymongo.MongoClient = None) -> int:
    total_active_devices = active_device_count(client)
    window_size_bytes = 10
    buffer_windows = 3000
    return buffer_windows * window_size_bytes * total_active_devices


def aggregate_measurement_metrics(client: pymongo.MongoClient = None) -> int:
    db_client = get_db_client(client)
    opq_db = db_client["opq"]
    return opq_db.command("collstats", "measurements")["size"]


def aggregate_trend_metrics(client: pymongo.MongoClient = None):
    db_client = get_db_client(client)
    opq_db = db_client["opq"]
    return opq_db.command("collstats", "trends")["size"]


def detection_metrics(client: pymongo.MongoClient = None):
    db_client = get_db_client(client)
    pass


def incident_metrics(client: pymongo.MongoClient = None):
    db_client = get_db_client(client)
    pass


def phenomena_metrics(client: pymongo.MongoClient = None):
    db_client = get_db_client(client)
    pass


def sample_system_metrics():
    db_client = get_db_client()
    return {
        "instantaneous_measurements_level": instantaneous_measurement_metrics(db_client),
        "aggregate_measurements_level": {
            "measurements": aggregate_measurement_metrics(db_client),
            "trends": aggregate_trend_metrics(db_client)
        }
    }

if __name__ == "__main__":
    print(sample_system_metrics())
