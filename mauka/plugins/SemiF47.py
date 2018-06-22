import plugins.base
import protobuf.util
import numpy
import constants
import mongo


PU = 120.0
time_datum=200.0*1.0/constants.SAMPLES_PER_MILLISECOND  
# time in msec (1e-3 sec), 
# of one data in the array

def viol_check(data, lvl):
    lvl_tym=200 if lvl==5 else 500 if lvl==7 else 1000 # is in msec
    lvl=0.5 if lvl==5 else 0.7 if lvl==7 else 0.8
    
    data_bool= numpy.logical_and(data>=(lvl-0.05)*PU,data<=(lvl+0.05)*PU)

    prev=0
    f=[]
    for k in range(0,data_bool.size):
        if data_bool[k]:
            prev+=1
            if prev==1:
                prev_ind=k
        else:
            if prev*time_datum>=lvl_tym:
                f.append([prev_ind,k-1])
            prev=0
    
    if prev*time_datum>=lvl_tym:
         f.append([prev_ind,k])    
    
    return f


############################# TESTING START ###############################

## code to check the functionality of viol_check

#VRMS values. each data point in the array is 200 sample times long
# to work with a smaller array for testing; we change time_datum
time_datum=200.0 #ONLY FOR TESTING viol_check function (DEBUGGING)  
vol=numpy.array([30,35,54,56,58,66,67,70,78,85,120,115,80,81,83,95
                  ,98,96,101,102,101.5,96.4,58])
print(vol)
print("With 0.5*PU checking viol_check")
f=viol_check(vol,5)
print(f)

print("With 0.7*PU checking viol_check")
f=viol_check(vol,7)
print(f)


print("With 0.8*PU checking viol_check")
f=viol_check(vol,8)
print(f) 

############################# TESTING STOP ###############################


class SemiF47Plugin(plugins.base.MaukaPlugin):
    def __init__(self, config, exit_event):
        super().__init__(config, ["RmsWindowedVoltage"], "SemiF47Plugin", exit_event)

    def on_message(self, topic, mauka_message):
        event_id=mauka_message.payload.event_id
        box_id=mauka_message.payload.box_id
        data=protobuf.util.repeated_as_ndarray(mauka_message.payload.data)
        start_time_ms=mauka_message.payload.start_timestamp_ms        
        # this will check if a violation ocurred or not
        
        lvl=[5, 7, 8]
        for k in [0,1,2]:
            f=viol_check(data, lvl[k])
            if len(f)>0: 
                # there are violations
                for k in range(0,len(f)):
                    dev=max(abs(120.0-numpy.max(data[f[k][0],f[k][1]])),
                            abs(120.0-numpy.min(data[f[k][0],f[k][1]])))
                    mongo.store_incident(
                        event_id,
                        box_id,
                        start_time_ms+f[k][0]*time_datum,
                        start_time_ms+(f[k][1]+1)*time_datum,
                        mongo.IncidentMeasurementType.VOLTAGE,
                        dev,
                        ["SEMI_F47_VIOLATION"],
                        [],
                        {},
                        self.mongo_client
                    )

