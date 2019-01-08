import pymongo

import time


def sample_system_metrics():
    pass


def active_device_count() -> int:
    db_client = pymongo.MongoClient()
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


def instantaneous_measurement_metrics() -> int:
    total_active_devices = active_device_count()
    window_size_bytes = 10
    buffer_windows = 3000
    return buffer_windows * window_size_bytes * total_active_devices


def aggregate_measurement_metrics():
    pass


def aggregate_trend_metrics():
    pass


def detection_metrics():
    pass


def incident_metrics():
    pass


def phenomena_metrics():
    pass


if __name__ == "__main__":
    print(instantaneous_measurement_metrics())
