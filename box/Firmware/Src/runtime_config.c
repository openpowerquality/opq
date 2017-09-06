#include <runtime_config.h>
//This is the runtime settings data structure organized as a register map.


__IO OPQ_Frame_Buffer frameBuffer;

void init_OPQ_RunTime(){
    frameBuffer.head = 0;
    frameBuffer.tail = 0;
    frameBuffer.currentSample = 0;
}