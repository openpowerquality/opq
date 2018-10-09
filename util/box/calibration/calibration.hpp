#include <cstdint>

///Grid cycles per second
const static int CYCLES_PER_SEC = 60;
///Sampling rate per cycle
const static int SAMPLES_PER_CYCLE = 200;
//Sampling rate:
const static int SAMPLING_RATE = CYCLES_PER_SEC * SAMPLES_PER_CYCLE;

typedef struct OPQCycle{
    int16_t data[SAMPLES_PER_CYCLE];
    uint16_t last_gps_counter;
    uint16_t current_counter;
    //Reserved
    uint32_t flags;
} __attribute__((packed)) OPQCycle;

inline bool readCycle(int fd, OPQCycle &cycle);
float getCalibrationConstant();
