/*

FIR filter designed with
 http://t-filter.appspot.com

sampling frequency: 1200 Hz

* 0 Hz - 100 Hz
  gain = 1
  desired ripple = 5 dB
  actual ripple = 3.9908821025097043 dB

* 120 Hz - 600 Hz
  gain = 0
  desired attenuation = -40 dB
  actual attenuation = -40.37960754994202 dB

*/

#ifndef ACQUISITION_LOWPASSFILTER_HPP
#define ACQUISITION_LOWPASSFILTER_HPP


#define LOWPASSFILTER_TAP_NUM 64

typedef struct {
    float history[LOWPASSFILTER_TAP_NUM];
    unsigned int last_index;
} LowPassFilter;

void LowPassFilter_init(LowPassFilter* f);
void LowPassFilter_put(LowPassFilter* f, float input);
float LowPassFilter_get(LowPassFilter* f);


#endif //ACQUISITION_LOWPASSFILTER_HPP
