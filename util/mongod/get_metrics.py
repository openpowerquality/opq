from pymongo import MongoClient
import gridfs 
import numpy as np
import os

BOX_ID = 1003

client = MongoClient('localhost', 27017)
db = client.opq
col = db.events

os.mkdir(str(BOX_ID))
f = open(str(BOX_ID) + "/f", "w+")
t= open(str(BOX_ID) + "/t", "w+")
v= open(str(BOX_ID) + "/v", "w+")


col = db.measurements
result = col.find({"box_id" : str(BOX_ID)})
for m in result:
	f.write(str(m["timestamp_ms"]/1000) +"," +str(m["frequency"]) + "\n")
	t.write(str(m["timestamp_ms"]/1000) +"," +str(m["thd"]) +"\n")
	v.write(str(m["timestamp_ms"]/1000) +"," +str(m["voltage"]) + "\n")

