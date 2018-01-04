import bson
import pymongo


# Migrating from original data model to documented one at
# https://open-power-quality.gitbooks.io/open-power-quality-manual/content/datamodel/description.html

def oid(oid_str: str) -> bson.ObjectId:
    return bson.ObjectId(oid_str)


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

# events
# 1. Rename event_number -> event_id
# 2. Rename time_stamp -> latencies
# 3. Remove boxes_received
# 4. Remove event_start
# 5. Remove event_end
print("Migrating events...", end=" ")
events = db.events
events.update_many({}, {"$rename": {"event_number": "event_id",
                                   "time_stamp": "latencies"},
                        "$unset": {#"boxes_received": "",
                                  "event_start": "",
                                  "event_end": ""}})

print("Done.")

# # box_events
# # . Rename fields
# # 1. Populate box_events from original data collection
# # 2. Rename event_number -> event_id
# # 3. Rename time_stamp -> window_timestamps_ms
# # 4. Rename event_start -> event_start_timestamp_ms
# # 5. Rename event_end -> event_end_timestamp_ms
# # 6. Rename data -> data_fs_filename
# # 7. Change type box_id int -> str
# # 8. Fix early box events
# print("Migrating data to box_events...", end=" ")
# box_events = db.data
# box_events.rename("box_events")
#
# # Some of our earliest box events used a different schema, unfortunately these were never updated or migrated
# for box_event in box_events.find({"Box ID": {"$exists": True}}):
#     _id = oid(box_event["_id"])
#     box_id = box_event["Box ID"]
#     event_start_timestamp_ms = box_event["time_start"]
#     event_end_timestamp_ms = box_event["time_start"]
#
# for box_event in box_events:
#     _id = oid(box_event["_id"])
#     box_id = box_event["box_id"]
#     box_events.update_one({"_id": _id},
#                           {"$rename": {"event_number": "event_id",
#                                        "time_stamp": "window_timestamps_ms",
#                                        "event_start": "event_start_timestamp_ms",
#                                        "event_end": "event_end_timestamp_ms",
#                                        "data": "data_fs_filename"},
#                            "$set": {"box_id": str(int(box_id))}})
#
# print("Done.")
#
# # fs.files
# # 1. Add metadata.event_id
# # 2. Add metadata.box_id
#
# # Ensure all the indexes we want exist
#
# print("Disconnecting from mongodb...", end=" ")
# client.close()
# print("Done.")
