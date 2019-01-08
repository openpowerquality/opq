import pymongo
import pymongo.database

import functools
import time
import typing


def get_db_client(client: pymongo.MongoClient = None) -> typing.Tuple[pymongo.MongoClient, pymongo.database.Database]:
    """Returns an instance of an OPQ mongo client and OPQ db object if one is not supplied."""
    if client is None:
        return get_db_client(pymongo.MongoClient())
    else:
        return client, client["opq"]


def collection_size(opq_db: pymongo.database.Database, collection: str) -> int:
    """Returns the size in bytes of a mongodb collection."""
    return opq_db.command("collstats", collection)["size"]


def active_device_count(client: pymongo.MongoClient = None) -> int:
    """
    Returns the number of devices that are currently active.
    Current active is defined as receiving a measurements within the past minute from a device.
    """
    db_client, opq_db = get_db_client(client)
    opq_boxes_collection = opq_db["opq_boxes"]
    box_ids = list(map(lambda obj: obj["box_id"], opq_boxes_collection.find({}, ["box_id"])))

    measurements_collection = opq_db["measurements"]
    now_ms = int(time.time()) * 1000
    one_min_ago_ms = now_ms - 60000
    measurements = measurements_collection.find({"timestamp_ms": {"$gt": one_min_ago_ms,
                                                                  "$lt": now_ms}},
                                                ["box_id"])
    return len(set(map(lambda obj: obj["box_id"], measurements)))


def instantaneous_measurement_metrics(client: pymongo.MongoClient = None) -> int:
    """Return the size in bytes of the instantaneous measurements level."""
    total_active_devices = active_device_count(client)
    window_size_bytes = 10
    buffer_windows = 3000
    return buffer_windows * window_size_bytes * total_active_devices


def aggregate_measurement_metrics(client: pymongo.MongoClient = None) -> int:
    """Return the size in bytes of the aggregate measurements level for measurements."""
    db_client, opq_db = get_db_client(client)
    return collection_size(opq_db, "measurements")


def aggregate_trend_metrics(client: pymongo.MongoClient = None) -> int:
    """Return the size in bytes of the aggregate measurements level for trends."""
    db_client, opq_db = get_db_client(client)
    return collection_size(opq_db, "trends")


def detection_metrics(client: pymongo.MongoClient = None) -> int:
    """Return the size in bytes of the aggregate detections level."""
    db_client, opq_db = get_db_client(client)
    events_metadata_size = collection_size(opq_db, "events")
    fs_files_collection = opq_db["fs.files"]
    event_files = fs_files_collection.find({"filename": {"$regex": "^event"}},
                                           ["filename", "chunkSize"])

    return events_metadata_size + functools.reduce(lambda acc, v: acc + v["chunkSize"], event_files, 0)


def incident_metrics(client: pymongo.MongoClient = None) -> int:
    """Return the size in bytes of the incidents level."""
    db_client, opq_db = get_db_client(client)
    incidents_metadata_size = collection_size(opq_db, "incidents")
    fs_files_collection = opq_db["incidents"]
    incident_files = fs_files_collection.find({"filename": {"$regex": "^incident"}},
                                              ["filename", "chunkSize"])
    return incidents_metadata_size + functools.reduce(lambda acc, v: acc + v["chunkSize"], incident_files, 0)


def phenomena_metrics(client: pymongo.MongoClient = None) -> int:
    """Return the size in bytes of the phenomena level."""
    db_client, opq_db = get_db_client(client)
    return 0


def sample_system_metrics() -> typing.Dict:
    """Return metrics for each level of the Laha hierarchy."""
    db_client, _ = get_db_client()
    return {
        "instantaneous_measurements_level": instantaneous_measurement_metrics(db_client),
        "aggregate_measurements_level": {
            "measurements": aggregate_measurement_metrics(db_client),
            "trends": aggregate_trend_metrics(db_client)
        },
        "detections_level": detection_metrics(db_client),
        "incidents_level": incident_metrics(db_client),
        "phenomena_level": phenomena_metrics(db_client)
    }


if __name__ == "__main__":
    print(sample_system_metrics())
