#ifndef OPQ_RUNTIME_CONFIG_H_H
#define OPQ_RUNTIME_CONFIG_H_H
#include "stm32f3xx_hal.h"

///Number of OPQFrames inside the OPQ_Frame_Buffer.
#define FRAME_BUFFER_SIZE 4
#define FRAME_DATA_COUNT 200

///OPQ data frame:
typedef struct{
    ///Signed 16 bit data points
    int16_t data[FRAME_DATA_COUNT];
    //Reserved
    uint16_t last_gps_counter;
    uint16_t current_counter;
    //Reserved
    uint32_t flags;
} OPQ_Frame;

//Flag value for
#define OPQ_GPS_THIS_FRAME 1

///OPQ Frame Buffer. This is a persistent data structure for storing the data samples.
typedef struct{
    ///Data frame circular buffer.
    OPQ_Frame frames[FRAME_BUFFER_SIZE];
    ///Head of the buffer.
    uint8_t head;
    ///Tail of the buffer.
    uint8_t tail;
    ///Current data sample in the frame.
    uint8_t currentSample;
    //GPS Pulse flag set by the Interrupt
    uint8_t gps_pulse_flag;
    //GPS Counter Value set by
    uint16_t gps_last_counter;

} OPQ_Frame_Buffer;

///Circular frame buffer
extern __IO OPQ_Frame_Buffer frameBuffer;

///Register buffer implementation.
void init_OPQ_RunTime();

#endif //FIRMWARE_RUNTIME_CONFIG_H_H
