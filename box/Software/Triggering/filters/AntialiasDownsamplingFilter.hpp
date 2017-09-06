/*

FIR filter designed with
 http://t-filter.appspot.com

sampling frequency: 12000 Hz

* 0 Hz - 500 Hz
  gain = 1
  desired ripple = 5 dB
  actual ripple = 3.9758323825872433 dB

* 600 Hz - 6000 Hz
  gain = 0
  desired attenuation = -40 dB
  actual attenuation = -40.41130148960798 dB

*/


#ifndef ACQUISITION_ANTIALIASDOWNSAMPLINGFILTER_HPP
#define ACQUISITION_ANTIALIASDOWNSAMPLINGFILTER_HPP



#define ANTIALIASDOWNSAMPLINGFILTER_TAP_NUM 128

typedef struct {
    float history[ANTIALIASDOWNSAMPLINGFILTER_TAP_NUM];
    unsigned int last_index;
} AntialiasDownsamplingFilter;

void AntialiasDownsamplingFilter_init(AntialiasDownsamplingFilter* f);
void AntialiasDownsamplingFilter_put(AntialiasDownsamplingFilter* f, float input);
float AntialiasDownsamplingFilter_get(AntialiasDownsamplingFilter* f);

#endif //ACQUISITION_ANTIALIASDOWNSAMPLINGFILTER_HPP
