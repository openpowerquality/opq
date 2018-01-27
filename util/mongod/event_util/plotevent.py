import enum
import math
import multiprocessing
import struct
import typing

import bson
import gridfs
import gridfs.errors
import matplotlib.path
import matplotlib.pyplot as plt
import numpy as np
import pymongo
import scipy.fftpack
import sys


SAMPLE_RATE_HZ = 12000.0



def to_s16bit(data: bytes) -> np.ndarray:
    return np.frombuffer(data, np.int16)

def waveform_from_file(fs: gridfs.GridFS, filename: str) -> np.ndarray:
    buf = fs.get_last_version(filename).read()
    s16bit_buf = to_s16bit(buf)
    return s16bit_buf

database_name = "opq"
client = pymongo.MongoClient()
db = client.opq
events = db.events
box_events = db.box_events
box_info = db.opq_boxes

fs = gridfs.GridFS(db)

min = 0
max = -1
event_num = -1
if len(sys.argv) > 1:
    event_num = int(sys.argv[1])
else:
    event_num = int(box_events.find_one(sort=[("event_id", -1)])["event_id"])
if len(sys.argv) > 2:
    min = int(sys.argv[2])
    min = int(min/200)*200
if len(sys.argv) > 3:
    max = int(sys.argv[3])
    max = int(max/200)*200

cal_constant = 1


for box_event in box_events.find( {"event_id" : event_num}):
    event_name = box_event["data_fs_filename"]
    box_cal = float(box_info.find_one({"box_id" : box_event["box_id"]})["calibration_constant"])
    event_data = waveform_from_file(fs, event_name)
    event_data = event_data[min:max]
    event_data = [x/box_cal for x in event_data]
    event_rms = []
    for i in range(0, int(len(event_data)/200)):
        rms = np.sum([1.0*x*x for x in event_data[i*200:(i+1)*200]]);
        rms = rms/200
        rms = rms**(1.0/2)
        event_rms.append(rms)
    plt.plot(range(0,len(event_data)), event_data, ".", label=("Box #" + box_event["box_id"]))
    plt.plot([x*200 for x in range(0, len(event_rms))], event_rms, "-*", label=("RMS #" + box_event["box_id"]))

plt.title("Event #" + str(event_num) + " samples " + str(min) + "..." + (max == -1 and str(len(event_data)) or str(max)))
plt.legend(loc="upper right")
plt.xlabel("Time(s)")
plt.ylabel("Voltage(V)");
plt.show()
