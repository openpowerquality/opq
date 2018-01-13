import enum
import math
import multiprocessing
import struct
import typing

import bson
import gridfs
import gridfs.errors
import matplotlib.path
import numpy
import pymongo
import scipy.fftpack

# Migrating from original data model to documented one at
# https://open-power-quality.gitbooks.io/open-power-quality-manual/content/datamodel/description.html

SAMPLES_PER_CYCLE = 200.0
"""Number of samples per electrical cycle for OPQ box"""

SAMPLE_RATE_HZ = 12000.0
"""Sample rate of OPQ box"""


def oid(oid_str: str) -> bson.ObjectId:
    """
    Wraps an
    :param oid_str:
    :return:
    """
    return bson.ObjectId(oid_str)


def filename(box_event: typing.Dict) -> str:
    box_id = str(int(box_event["box_id"]))
    event_id = box_event["event_number"]
    return "event_{}_{}".format(event_id, box_id)


def to_s16bit(data: bytes) -> numpy.ndarray:
    """
    Converts raw bytes into an array of 16 bit integers.
    :param data:
    :return:
    """
    return numpy.frombuffer(data, numpy.int16)


def waveform_from_file(fs: gridfs.GridFS, filename: str) -> numpy.ndarray:
    buf = fs.get_last_version(filename).read()
    s16bit_buf = to_s16bit(buf)
    return s16bit_buf


def vrms(samples: numpy.ndarray) -> float:
    """
    Calculates the Voltage root-mean-square of the supplied samples
    :param samples: Samples to calculate Vrms over.
    :return: The Vrms value of the provided samples.
    """
    summed_sqs = numpy.sum(numpy.square(samples))
    return math.sqrt(summed_sqs / len(samples))


def vrms_waveform(waveform: numpy.ndarray, window_size: int = int(SAMPLES_PER_CYCLE)) -> numpy.ndarray:
    """
    Calculated Vrms of a waveform using a given window size. In most cases, our window size should be the
    number of samples in a cycle.
    :param waveform: The waveform to find Vrms values for.
    :param window_size: The size of the window used to compute Vrms over the waveform.
    :return: An array of vrms values calculated for a given waveform.
    """
    v = []
    while len(waveform) >= window_size:
        samples = waveform[:window_size]
        waveform = waveform[window_size:]
        v.append(vrms(samples))

    if len(waveform) > 0:
        v.append(vrms(waveform))

    return numpy.array(v)


class IticRegion(enum.Enum):
    """
    Enumerations of ITIC regions.
    """
    NO_INTERRUPTION = "NO_INTERRUPTION"
    PROHIBITED = "PROHIBITED"
    NO_DAMAGE = "NO_DAMAGE"
    OTHER = "OTHER"


def c_to_ms(c: float) -> float:
    """
    Convert cycles to milliseconds
    :param c: cycles
    :return: milliseconds
    """
    return (c * (1 / 60)) * 1000.0


HUNDREDTH_OF_A_CYCLE = c_to_ms(0.01)
"""Hundredth of a power cycle in milliseconds"""

prohibited_region_polygon = [
    [HUNDREDTH_OF_A_CYCLE, 500],
    [1, 200],
    [3, 140],
    [3, 120],
    [20, 120],
    [5000, 120],
    [5000, 110],
    [10000, 110],
    [10000, 500],
    [HUNDREDTH_OF_A_CYCLE, 500]
]
"""Polygon representing the prohibited region"""

no_damage_region_polygon = [
    [20, 0],
    [20, 40],
    [20, 70],
    [5000, 70],
    [5000, 80],
    [10000, 80],
    [10000, 90],
    [10000, 0],
    [20, 0]
]
"""Polygon representing the no damage region"""

no_interruption_region_polygon = [
    [0, 0],
    [0, 500],
    [HUNDREDTH_OF_A_CYCLE, 500],
    [1, 200],
    [3, 140],
    [3, 120],
    [20, 120],
    [5000, 120],
    [5000, 110],
    [10000, 110],
    [10000, 90],
    [10000, 80],
    [5000, 80],
    [5000, 70],
    [20, 70],
    [20, 40],
    [20, 0],
    [0, 0]
]
"""Polygon representing the no interruption region"""


def point_in_polygon(x: float, y: float, polygon: typing.List[typing.List[float]]) -> bool:
    """
    Checks if a point is in a given polygon.
    :param x: x
    :param y: y
    :param polygon: The polygon to check for inclusion
    :return: Whether or not the given point is in the provided polygon
    """
    path = matplotlib.path.Path(vertices=numpy.array(polygon), closed=True)
    return path.contains_point([x, y])


def itic_region(rms_voltage: float, duration_ms: float) -> enum.Enum:
    """
    Returns the ITIC region of a given RMS voltage and duration.
    The reference curve is at http://www.keysight.com/upload/cmc_upload/All/1.pdf
    :param rms_voltage: The RMS voltage value
    :param duration_ms: The duration of the voltage event in milliseconds
    :return: The appropriate ITIC region enum
    """

    percent_nominal = (rms_voltage / 120.0) * 100.0

    # First, let's check the extreme edge cases
    if duration_ms < c_to_ms(0.01):
        return IticRegion.NO_INTERRUPTION

    if rms_voltage <= 0:
        if duration_ms <= 20:
            return IticRegion.NO_INTERRUPTION
        else:
            return IticRegion.NO_DAMAGE

    # In the x and y directions
    if duration_ms >= 10000 and percent_nominal >= 500:
        return IticRegion.PROHIBITED

    # In the x-direction
    if duration_ms >= 10000:
        if percent_nominal >= 110:
            return IticRegion.PROHIBITED
        elif percent_nominal <= 90:
            return IticRegion.NO_DAMAGE
        else:
            return IticRegion.NO_INTERRUPTION

    # In the y-direction
    if percent_nominal >= 500:
        if duration_ms <= HUNDREDTH_OF_A_CYCLE:
            return IticRegion.NO_INTERRUPTION
        else:
            return IticRegion.PROHIBITED

    # If the voltage is not an extreme case, we run point in polygon calculations to determine which region its in
    if point_in_polygon(duration_ms, percent_nominal, no_interruption_region_polygon):
        return IticRegion.NO_INTERRUPTION

    if point_in_polygon(duration_ms, percent_nominal, prohibited_region_polygon):
        return IticRegion.PROHIBITED

    if point_in_polygon(duration_ms, percent_nominal, no_damage_region_polygon):
        return IticRegion.NO_DAMAGE

    # If it's directly on the line of one of the polygons, its easiest to just say no_interruption
    return IticRegion.NO_INTERRUPTION


def itic(waveform: numpy.ndarray) -> str:
    """
    Returns the ITIC region as a string given a waveform.
    :param waveform: The waveform to measure.
    :return: ITIC region name for specified waveform
    """
    vrms_vals = vrms_waveform(waveform)
    duration_ms = (len(waveform) / SAMPLE_RATE_HZ) * 1000
    vrms_min = numpy.min(vrms_vals)
    vrms_max = numpy.max(vrms_vals)

    if numpy.abs(vrms_min - 120.0) > numpy.abs(vrms_max - 120.0):
        return itic_region(vrms_min, duration_ms).name
    else:
        return itic_region(vrms_max, duration_ms).name


def get_calibration_constant(opq_boxes, box_id: str) -> float:
    return opq_boxes.find_one({"box_id": box_id})["calibration_constant"]


def sq(num: float) -> float:
    """
    Squares a number
    :param num: Number to square
    :return: Squared number
    """
    return num * num


def closest_idx(array: numpy.ndarray, val: float) -> int:
    """
    Finds the index in a sorted array whose value is closest to the value we are searching for "val".
    :param array: The array to search through.
    :param val: The value that we want to compare to each element.
    :return: The index of the closest value to val.
    """
    return numpy.argmin(numpy.abs(array - val))


def thd(waveform: numpy.ndarray) -> float:
    """
    Calculated THD by first taking the FFT and then taking the peaks of the harmonics (sans the fundamental).
    :param waveform:
    :return:
    """
    y = scipy.fftpack.fft(waveform)
    x = numpy.fft.fftfreq(y.size, 1 / SAMPLE_RATE_HZ)

    new_x = []
    new_y = []
    for i in range(len(x)):
        if x[i] >= 0:
            new_x.append(x[i])
            new_y.append(y[i])

    new_x = numpy.array(new_x)
    new_y = numpy.abs(numpy.array(new_y))

    nth_harmonic = {
        1: new_y[closest_idx(new_x, 60.0)],
        2: new_y[closest_idx(new_x, 120.0)],
        3: new_y[closest_idx(new_x, 180.0)],
        4: new_y[closest_idx(new_x, 240.0)],
        5: new_y[closest_idx(new_x, 300.0)],
        6: new_y[closest_idx(new_x, 360.0)],
        7: new_y[closest_idx(new_x, 420.0)]
    }

    top = sq(nth_harmonic[2]) + sq(nth_harmonic[3]) + sq(nth_harmonic[4]) + sq(nth_harmonic[5])
    _thd = (math.sqrt(top) / nth_harmonic[1]) * 100.0
    return _thd


parallel_client = None
parallel_db = None
parallel_fs = None


def init_parallel_client():
    global parallel_client
    global parallel_db
    global parallel_fs
    parallel_client = pymongo.MongoClient()
    parallel_db = parallel_client.opq
    parallel_fs = gridfs.GridFS(parallel_db)


def parallel_migrate_measurements(measurement: typing.Dict):
    _id = oid(measurement["_id"])
    measurements = parallel_db.measurements
    if "device_id" in measurement and "box_id" not in measurement:
        box_id = measurement["device_id"]
        measurements.update_one({"_id": _id},
                                {"$rename": {"device_id": "box_id"}})
    else:
        box_id = measurement["box_id"]

    measurements.update_one({"_id": _id},
                            {"$set": {"box_id": str(int(box_id))}})


def parallel_migrate_and_decimate_measurements(device_id: int):
    prev_ts = 0
    ids_to_delete = []
    total_measurements = parallel_db.measurements.count({"device_id": device_id})
    i = 0

    for measurement in parallel_db.measurements.find({"device_id": device_id},
                                                     ["device_id", "timestamp_ms", "box_id"]).sort("timestamp_ms"):

        if i % 10_000 == 0:
            print("Migrating and decimating measurements for box", device_id, (float(i) / float(total_measurements) * 100.0), "%")


        _id = oid(measurement["_id"])
        ts = measurement["timestamp_ms"]

        if ts - prev_ts < 60_000:
            ids_to_delete.append(_id)
        else:
            if "device_id" in measurement and "box_id" not in measurement:
                box_id = measurement["device_id"]
                measurements.update_one({"_id": _id},
                                        {"$rename": {"device_id": "box_id"}})
            else:
                box_id = measurement["box_id"]

            measurements.update_one({"_id": _id},
                                    {"$set": {"box_id": str(int(box_id))}})

            prev_ts = ts
            measurements.delete_many({"_id": {"$in": ids_to_delete}})
            ids_to_delete.clear()

        i += 1


def parallel_raw_waveforms_to_gridfs_fn(box_event: typing.Dict):
    fs = parallel_fs
    box_events = parallel_db.box_events

    _id = oid(box_event["_id"])
    _data = box_event["data"]
    data = struct.pack("<{}h".format(len(_data)), *_data)

    _filename = filename(box_event)
    fs.put(data, filename=_filename)
    box_events.update_one({"_id": _id},
                          {"$unset": {"data": ""},
                           "$set": {"data_fs_filename": _filename}})


def parallel_finalize_box_events_migration_fn(box_event: typing.Dict):
    box_events = parallel_db.box_events
    _id = oid(box_event["_id"])
    box_id = str(int(box_event["box_id"]))
    box_events.update_one({"_id": _id},
                          {"$rename": {"event_number": "event_id",
                                       "time_stamp": "window_timestamps_ms",
                                       "event_start": "event_start_timestamp_ms",
                                       "event_end": "event_end_timestamp_ms",
                                       "data": "data_fs_filename"},
                           "$set": {"box_id": box_id,
                                    "location": {}}})


def parallel_thd_itic_fn(box_event: typing.Dict):
    try:
        db = parallel_db
        box_events = db.box_events
        opq_boxes = db.opq_boxes
        fs = parallel_fs
        calibration_constants = dict()
        _id = oid(box_event["_id"])

        data_fs_filename = box_event["data_fs_filename"]
        box_id = box_event["box_id"]
        waveform = waveform_from_file(fs, data_fs_filename)

        if box_id not in calibration_constants:
            calibration_constants[box_id] = get_calibration_constant(opq_boxes, box_id)

        calibrated_waveform = waveform / calibration_constants[box_id]

        _itic = itic(calibrated_waveform)
        _thd = thd(calibrated_waveform)

        box_events.update_one({"_id": _id},
                              {"$set": {"itic": _itic,
                                        "thd": _thd}})

    except gridfs.errors.NoFile as e:
        pass


def parallel_update_fs_files_metadata_fn(box_event: typing.Dict):
    fs_files = parallel_db["fs.files"]
    event_id = box_event["event_id"]
    box_id = box_event["box_id"]
    data_fs_filename = box_event["data_fs_filename"]
    fs_files.update_one({"filename": data_fs_filename},
                        {"$set": {"metadata": {"event_id": event_id,
                                               "box_id": box_id}}})


if __name__ == "__main__":
    print("Connecting to OPQ mongodb...", end=" ", flush=True)
    database_name = "opq"
    client = pymongo.MongoClient()
    db = client.opq
    print("Connected.")

    # Migration plan

    # measurements
    # 1. Rename device_id -> box_id
    # 2. Change box_id value to str
    print("Migrating measurements...", end=" ", flush=True)
    measurements = db.measurements
    total_meansurements = measurements.count()
    device_ids = [1, 2, 3, 4, 5]
    pool = multiprocessing.Pool(initializer=init_parallel_client)
    pool.imap_unordered(parallel_migrate_and_decimate_measurements, device_ids)
    pool.close()

    # i = 0
    # pool = multiprocessing.Pool(6, initializer=init_parallel_client)
    # for v in pool.imap_unordered(parallel_migrate_measurements, measurements.find({}, ["_id", "device_id",
    # "box_id"])):
    #     if i % 10000 == 0:
    #         print("\rMigrating measurements...", float(i) / float(total_meansurements) * 100.0, "%", end="",
    # flush=True)
    #     i += 1
    # pool.close()

    # for measurement in measurements.find({}, ["_id", "device_id", "box_id"]):
    #     _id = oid(measurement["_id"])
    #     if "device_id" in measurement and "box_id" not in measurement:
    #         box_id = measurement["device_id"]
    #         measurements.update_one({"_id": _id},
    #                                 {"$rename": {"device_id": "box_id"}})
    #     else:
    #         box_id = measurement["box_id"]
    #
    #     measurements.update_one({"_id": _id},
    #                             {"$set": {"box_id": str(int(box_id))}})

    print("\rMigrating measurements... Done.")

    # opq_boxes
    # 1. Create opq_boxes collection from CalibrationConstants collection
    # 2. Rename device_id -> box_id
    # 3. Update type of box_id from number -> string
    # 4. Add blank fields for rest of opq_box documents
    print("Migrating CalibrationConstants to opq_boxes...", end=" ", flush=True)
    opq_boxes = db.CalibrationConstants
    opq_boxes.rename("opq_boxes")
    opq_boxes = db.opq_boxes
    for opq_box in opq_boxes.find({}):
        _id = oid(opq_box["_id"])
        box_id = str(int(opq_box["device_id"]))
        opq_boxes.update_one({"_id": _id},
                             {"$rename": {"device_id": "box_id"}})
        opq_boxes.update_one({"_id": _id},
                             {"$set": {"box_id": box_id,
                                       "name": "",
                                       "description": "",
                                       "locations": []}})
    print("Done.")

    # events
    # 1. Rename event_number -> event_id
    # 2. Rename time_stamp -> latencies
    # 3. Remove boxes_received
    # 4. Remove event_start
    # 5. Remove event_end
    print("Migrating events...", end=" ", flush=True)
    events = db.events
    events.update_many({}, {"$rename": {"event_number": "event_id",
                                        "time_stamp": "latencies_ms",
                                        "event_start": "target_event_start_timestamp_ms",
                                        "event_end": "target_event_end_timestamp_ms"}})
    print("Done.")

    # box_events
    # 1. Rename data collection to box_events collection
    # 2. Rename fields of old-old events
    # 3. Create files for old events
    # 4. Rename event_number -> event_id
    # 5. Rename time_stamp -> window_timestamps_ms
    # 6. Rename event_start -> event_start_timestamp_ms
    # 7. Rename event_end -> event_end_timestamp_ms
    # 8. Rename data -> data_fs_filename
    # 9. Change type box_id int -> str
    # 10. Make sure ITIC is updated for all box_events
    # 11. Make sure THD is updated for all box_events
    box_events = db.data
    box_events.rename("box_events")
    box_events = db.box_events

    # Some of our earliest box events used a different schema, unfortunately these were never updated or migrated
    # First we'll migrate these to the older format to later migrate to the newest format
    print("Migrating early events...", end=" ", flush=True)
    for box_event in box_events.find({"Box ID": {"$exists": True}}):
        _id = oid(box_event["_id"])
        box_events.update_one({"_id": _id},
                              {"$rename": {"Box ID": "box_id",
                                           "time_start": "event_start",
                                           "time_end": "event_end",
                                           "time_stamps": "time_stamp"}})
    print("Done.")

    # Next, some of our box events store the raw waveform directly in the collection, but they should be stored in
    # separate files. Go through, and make sure these documents get converted to mongo gridfs file storage. File
    # names should be of the form "event_[event_id]_[box_id]"
    print("Migrating raw waveform data from documents to gridfs...", end=' ', flush=True)
    total_arrays = box_events.count({"data": {"$type": "array"}})
    i = 0
    pool = multiprocessing.Pool(6, initializer=init_parallel_client)
    for v in pool.imap_unordered(parallel_raw_waveforms_to_gridfs_fn, box_events.find({"data": {"$type": "array"}})):
        if i % 50 == 0:
            print("\rMigrating raw waveform data from documents to gridfs...", float(i) / float(total_arrays) * 100.0,
                  "%", end="", flush=True)
        i += 1
    pool.close()
    print("\rMigrating raw waveform data from documents to gridfs... Done.")

    # Finally, now that everything has been migrated to a common schema, we can perform the final migration for
    # box_events.
    print("Performing final migration of box_events...", end=" ", flush=True)
    total = box_events.count()
    i = 0
    pool = multiprocessing.Pool(6, initializer=init_parallel_client)
    for v in pool.imap_unordered(parallel_finalize_box_events_migration_fn, box_events.find()):
        if i % 50 == 0:
            print("\rPerforming final migration of box_events...", float(i) / float(total) * 100.0, "%", end="",
                  flush=True)
        i += 1
    pool.close()
    print("\rPerforming final migration of box_events... Done.")

    # THD & ITIC
    print("Updating THD and ITIC values...", end=" ", flush=True)
    total_events = box_events.count()
    i = 0
    pool = multiprocessing.Pool(6, initializer=init_parallel_client)
    for v in pool.imap_unordered(parallel_thd_itic_fn, box_events.find({}, ["_id", "data_fs_filename", "box_id"])):
        if i % 50 == 0:
            print("\rUpdating THD and ITIC values...", float(i) / float(total_events) * 100.0, "%", end="", flush=True)
        i += 1
    pool.close()
    print("\rUpdating THD and ITIC values... Done.")

    # fs.files
    # 1. Add metadata.event_id
    # 2. Add metadata.box_id
    print("Migrating fs.files...", end=" ", flush=True)
    total_events = box_events.count()
    i = 0
    pool = multiprocessing.Pool(6, initializer=init_parallel_client)
    for v in pool.imap_unordered(parallel_update_fs_files_metadata_fn,
                                 box_events.find({}, ["event_id", "box_id", "data_fs_filename"])):
        if i % 50 == 0:
            print("\rMigrating fs.files...", float(i) / float(total_events) * 100.0, "%", end="", flush=True)
        i += 1
    pool.close()
    print("\rMigrating fs.files... Done.")

    # Ensure all the indexes we want exist
    print("Ensuring measurements indexes...", end=" ", flush=True)
    db.measurements.create_indexes([pymongo.IndexModel("box_id"),
                                    pymongo.IndexModel("timestamp_ms")])
    print("Done.")

    print("Ensuring opq_boxes indexes...", end=" ", flush=True)
    db.opq_boxes.create_index("box_id")
    print("Done.")

    print("Ensuring events indexes...", end=" ", flush=True)
    db.events.create_indexes([pymongo.IndexModel("event_id"),
                              pymongo.IndexModel("type")])
    print("Done.")

    print("Ensuring box_events indexes...", end=" ", flush=True)
    db.box_events.create_indexes([pymongo.IndexModel("event_id"),
                                  pymongo.IndexModel("box_id"),
                                  pymongo.IndexModel("event_start_timestamp_ms"),
                                  pymongo.IndexModel("event_end_timestamp_ms"),
                                  pymongo.IndexModel("data_fs_filename"),
                                  pymongo.IndexModel("thd"),
                                  pymongo.IndexModel("itic")])
    print("Done.")

    print("Ensuring fs.files indexes...", end=" ", flush=True)
    db.fs.files.create_indexes([pymongo.IndexModel("metadata.box_id"),
                                pymongo.IndexModel("metadata.event_id")])
    print("Done.")

    # Cleanup
    # 1. Drop deprecated boxEvents collection
    print("Cleaning up....")
    print("Dropping boxEvents collection...")
    db.boxEvents.drop()
    print("Done.")

    print("Disconnecting from mongodb...", end=" ", flush=True)
    client.close()
    print("Pau.")
