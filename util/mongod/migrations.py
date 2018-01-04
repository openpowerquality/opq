import struct
import typing

import bson
import gridfs
import pymongo


# Migrating from original data model to documented one at
# https://open-power-quality.gitbooks.io/open-power-quality-manual/content/datamodel/description.html

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


print("Connecting to OPQ mongodb...", end=" ")
database_name = "opq"
client = pymongo.MongoClient()
db = client.opq
print("Connected.")

# Migration plan

# # measurements
# # 1. Rename device_id -> box_id
# # 2. Change box_id value to str
# print("Migrating measurements...")
# measurements = db.measurements
# total_measurements = measurements.count()
# i = 0
# for measurement in measurements.find({}, ["_id", "device_id", "box_id"]):
#     _id = oid(measurement["_id"])
#
#     if "device_id" in measurement and "box_id" not in measurement:
#         measurements.update_one({"_id": _id},
#                                 {"$rename": {"device_id": "box_id"}})
#
#     measurements.update_one({"_id": _id},
#                             {"$set": {"box_id": str(int(measurement["box_id"]))}})
#
#     if i % 100000 == 0:
#         print("Migrating measurements", str(float(i) / float(total_measurements) * 100.0), "%")
#
#     i += 1
#
# print("Done.")
#
# # opq_boxes
# # 1. Create opq_boxes collection from CalibrationConstants collection
# # 2. Rename device_id -> box_id
# # 3. Update type of box_id from number -> string
# # 4. Add blank fields for rest of opq_box documents
# print("Migrating CalibrationConstants to opq_boxes...", end=" ")
# opq_boxes = db.CalibrationConstants
# opq_boxes.rename("opq_boxes")
# opq_boxes = db.opq_boxes
# for opq_box in opq_boxes.find({}):
#     _id = oid(opq_box["_id"])
#     box_id = str(int(opq_box["device_id"]))
#     opq_boxes.update_one({"_id": _id},
#                          {"$rename": {"device_id": "box_id"}})
#     opq_boxes.update_one({"_id": _id},
#                          {"$set": {"box_id": box_id,
#                                    "name": "",
#                                    "description": "",
#                                    "locations": []}})
# print("Done.")
#
# # events
# # 1. Rename event_number -> event_id
# # 2. Rename time_stamp -> latencies
# # 3. Remove boxes_received
# # 4. Remove event_start
# # 5. Remove event_end
# print("Migrating events...", end=" ")
# events = db.events
# events.update_many({}, {"$rename": {"event_number": "event_id",
#                                     "time_stamp": "latencies"},
#                         "$unset": {  # "boxes_received": "", # May be needed
#                             "event_start": "",
#                             "event_end": ""}})
#
# print("Done.")
#
# # box_events
# # 1. Rename data collection to box_events collection
# # 2. Rename fields of old-old events
# # 3. Create files for old events
# # 4. Rename event_number -> event_id
# # 5. Rename time_stamp -> window_timestamps_ms
# # 6. Rename event_start -> event_start_timestamp_ms
# # 7. Rename event_end -> event_end_timestamp_ms
# # 8. Rename data -> data_fs_filename
# # 9. Change type box_id int -> str
# print("Migrating data to box_events...", end=" ")
# box_events = db.data
# box_events.rename("box_events")
box_events = db.box_events
#
# # Some of our earliest box events used a different schema, unfortunately these were never updated or migrated
# # First we'll migrate these to the older format to later migrate to the newest format
# for box_event in box_events.find({"Box ID": {"$exists": True}}):
#     _id = oid(box_event["_id"])
#     box_events.update_one({"_id": _id},
#                           {"$rename": {"Box ID": "box_id",
#                                        "time_start": "event_start",
#                                        "time_end": "event_end",
#                                        "time_stamps": "time_stamp"}})
#
# # Next, some of our box events store the raw waveform directly in the collection, but they should be stored in separate
# # files. Go through, and make sure these documents get converted to mongo gridfs file storage.
# # File names should be of the form "event_[event_id]_[box_id]"
# fs = gridfs.GridFS(db)
#
# for box_event in box_events.find({"data": {"$type": "array"}}):
#     _id = oid(box_event["_id"])
#     _data = box_event["data"]
#     data = struct.pack("<{}h".format(len(_data)), *_data)
#
#     _filename = filename(box_event)
#     fs.put(data, filename=_filename)
#     box_events.update_one({"_id": _id},
#                           {"$set": {"data": _filename}})
#
# # Finally, now that everything has been migrated to a common schema, we can perform the final migration for box_events.
# for box_event in box_events.find({}):
#     _id = oid(box_event["_id"])
#     box_id = str(int(box_event["box_id"]))
#     box_events.update_one({"_id": _id},
#                           {"$rename": {"event_number": "event_id",
#                                        "time_stamp": "window_timestamps_ms",
#                                        "event_start": "event_start_timestamp_ms",
#                                        "event_end": "event_end_timestamp_ms",
#                                        "data": "data_fs_filename"},
#                            "$set": {"box_id": box_id,
#                                     "location": {}}})
#
# print("Done.")

# fs.files
# 1. Add metadata.event_id
# 2. Add metadata.box_id
print("Migrating fs.files...", end=" ")
fs_files = db["fs.files"]
for box_event in box_events.find({}, ["event_id", "box_id", "data_fs_filename"]):
    event_id = box_event["event_id"]
    box_id = box_event["box_id"]
    data_fs_filename = box_event["data_fs_filename"]
    fs_files.update_one({"filename": data_fs_filename},
                        {"$set": {"metadata": {"event_id": event_id,
                                               "box_id": box_id}}})
print("Done.")

# # Cleanup
# # 1. Drop deprecated boxEvents collection
# print("Cleaning up....")
# print("Dropping boxEvents collection...")
# print(db.boxEvents.drop())
# print("Done.")

# Ensure all the indexes we want exist

print("Disconnecting from mongodb...", end=" ")
client.close()
print("Done.")
