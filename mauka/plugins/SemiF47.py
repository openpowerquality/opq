import plugins.base
import protobuf.util
import numpy
import constants


PU = 120.0
time_datum=1.0/constants.SAMPLES_PER_MILLISECOND  # time in msec (1e-3 sec), 
                                        # of one data in the array

def viol_check(data,prev,lvl):
    lvl=0.5 if lvl==5 else 0.7 if lvl==7 else 0.8
    lvl_tym=200 if lvl==5 else 500 if lvl==7 else 1000 # is in msec
    
    data_bool= numpy.logical_and(data>=(lvl-0.05)*PU,data<=(lvl+0.05)*PU)

    prev_ind=-1
    f=[]
    for k in range(0,data_bool.size):
        if data_bool[k]:
            prev+=1
            if prev==1:
                prev_ind=k
        else:
            if prev*time_datum>=lvl_tym and k>0:
                f.append([prev_ind,k-1])
            prev=0
    
    if prev*time_datum>=lvl_tym:
         f.append([prev_ind,k])    
    
    return (f,prev)

#d=numpy.random.randint(40,70,10)+numpy.random.random_sample(10)
#d=numpy.array([60, 60, 30, 60, 60, 60, 60])
#print(d)
#print(viol_check(d,2,5))
                
        

class SemiF47Plugin(plugins.base.MaukaPlugin):
    V_05=0;
    V_07=0;
    V_08=0;
    def __init__(self, config, exit_event):
        super().__init__(config, ["RmsWindowedVoltage"], "SemiF47Plugin", exit_event)

    def on_message(self, topic, mauka_message):
        event_id=mauka_message.payload.event_id
        box_id=mauka_message.payload.box_id
        data=protobuf.util.repeated_as_ndarray(mauka_message.payload.data)
        
    # this will call semiF47 to check if a violation ocurred or not
        viol_bool=semiF47(data,self.V_05, self.V_07, self.V_08)
        