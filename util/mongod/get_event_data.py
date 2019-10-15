from pymongo import MongoClient
import gridfs 
import numpy as np
import os
import sys

if len(sys.argv) == 1:
	print("Need an event number")
	sys.exit()

EVENT_ID = int(sys.argv[1])

client = MongoClient('localhost', 27017)
db = client.opq
col = db.events
result = col.find_one({
	"event_id" : EVENT_ID
})
start = result["target_event_start_timestamp_ms"]
end = result["target_event_end_timestamp_ms"]

os.mkdir(str(EVENT_ID))
out = open(str(EVENT_ID) + "/event", "w+")
out.write('{0}'.format(result))

col = db.box_events
results = col.find({
	"event_id" : EVENT_ID
})

devices = []
files = []
constants = {}
col2= db.opq_boxes
for p in results:
	out = open(str(EVENT_ID) + "/" + p["box_id"] + ".event", "w+")
	devices.append(p["box_id"])
	files.append(p["data_fs_filename"])

	result = col2.find_one({
		"box_id" : p["box_id"]
	})
	constants[p["data_fs_filename"]] = result["calibration_constant"]

	out.write('{0}'.format(p))
print(devices)
print(files)


col = db.measurements
for d in devices:
	result = col.find({
	"box_id" : d,
	"timestamp_ms": {
	    "$gt": start,
	    "$lte": end
	}
	})
	out = open(str(EVENT_ID) + "/" + d + ".measurement", "w+")
	for m in result:
		out.write('{0} : {1}, {2}, {3}, {4}\n'.format(m["box_id"], m["voltage"], m["frequency"], m["thd"], m["transient"]))

gridfs = gridfs.GridFS(db)
for f in files:
	print(f)
	data = gridfs.find_one({"filename": f}).read()
	samples = np.frombuffer(data, np.int16)
	out = open(str(EVENT_ID) + "/" + f, "w+")
	for sample in samples:
		out.write('{}\n'.format(float(sample)/constants[f]))
