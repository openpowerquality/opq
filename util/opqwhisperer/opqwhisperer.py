import json
import redis
import random
import time
import math
import lz4
import threading
import signal
import os
from time import sleep

#sampling parameters
SAMPLES_PER_CYCLE = 200
CYCLES_PER_MEASUREMENT = 10*60


random.seed()
#make some devices and locations
deviceId = range(0, random.randint(5,20))
deviceLoc = map(lambda id : [id,id], deviceId)
print "Starting with " + str(len(deviceId)) + " devices"

#connect to redis
r = redis.Redis(host='localhost', port=6379, password=os.environ['REDIS_PASSWORD'])
print "Redis connection established"

#threading handles
done = False;
threads = []

#Catching sigint cause Python threads are stupid.
def signal_handler(signal, frame):
    #python signal handlers are stupid too....
    global done
    print('Spooling down. Wait (up to) 10 seconds')
    done = True

#Jsonable object. Also supports LZ4 compression.
class Jsonable:
    def to_JSON(self):
        return json.dumps(self, default=lambda o: o.__dict__, sort_keys=True, indent=4)
    def to_LZJSON(self):
        return lz4.dumps(self.to_JSON())

#Voltage frequency thread
def triggeringThread(devId):
    triggerHandle = "box:" + str(devId) + ":trg"
    #clear the queue
    r.delete(triggerHandle)
    while not done:
        #generate a fake voltage and frequency.
        item = str(int(time.time() * 1000)) + ":" + str(120 + random.randint(-10,10)) + ":" + str(60 + random.uniform(-0.03,0.03))
        #push and trim up the list
        r.lpush(triggerHandle, item)
        r.ltrim(triggerHandle, 0, 600)
        sleep(0.1)

#Generates a Sag. frac represents how bad it is, and eid is the event ID.
def makeSagSwell(frac, eid):
    #where the event took place
    epicenterX = random.uniform(min(deviceId), max(deviceId))
    epicenterY = random.uniform(min(deviceId), max(deviceId))
    activeDevices = [];
    activeLoc = [];
    activeDistances = [];
    #pick some random devices from the device list and compute their distance from event
    map(lambda id :  random.getrandbits(1) == 1 and (activeDevices.append(id[0]) or activeLoc.append(id[1])), zip(deviceId, deviceLoc))
    map(lambda loc : activeDistances.append(math.hypot(epicenterX- loc[0], epicenterY - loc[1])), activeLoc)
    #populate the event ID and timestamp
    event = Jsonable()
    event.eventId = eid;
    event.time = int(time.time())
    event.devices = []
    #fill in the data field.This field is an array of devices and their corresponding data
    for dev in zip(activeDevices, activeDistances):
        devData = Jsonable();
        #Scale the voltage sag based on the distance from the epicenter via 1 - 1/2*(distance + 1) suverity can be scaled using the frac argument.
        devData.data = map(lambda x: frac*(1 - 1/2*(dev[1] + 1)) * 170 * math.sin(x*2.0*math.pi/SAMPLES_PER_CYCLE), range(0, SAMPLES_PER_CYCLE * CYCLES_PER_MEASUREMENT))
        #fill in the device ID and append to the event object
        devData.id = dev[0]
        event.devices.append(devData)
    #publish the event
    r.publish("gridwide", event.to_LZJSON())

#setup signals create the triggering threads.
signal.signal(signal.SIGINT, signal_handler)
map(lambda id : threads.append(threading.Thread(target = triggeringThread, args=(id, ))), deviceId)
map(lambda thread : thread.start(), threads)

#this is the gridwide event generator.
while not done:
    eventId = 1;
    makeSagSwell(1, eventId)
    eventId += 1
    sleep(random.randint(1,10))
#spool down
print "Gathering up threads"
map(lambda thread : thread.join(), threads)
print "Exiting"
