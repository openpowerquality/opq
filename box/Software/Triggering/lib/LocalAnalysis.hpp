#ifndef ACQUISITION_METRICS_H
#define ACQUISITION_METRICS_H

#include <vector>
#include <stdint.h>
#include <thread>

#include "AntialiasDownsamplingFilter.hpp"
#include "LowPassFilter.hpp"
#include "opqdata.hpp"



namespace opq {
    /**
     * @brief Analysis thread used in generating triggering information, and storing measurements into a local redis instance.
     */
    class LocalAnalysis {
    public:
        /**
         * Default constructor.
         * @param inq ADC measuremement Queue.
         * @param outq Analysis queue.
         */
        LocalAnalysis(opq::data::MeasurementQueue  inq, opq::data::AnalysisQueue outq, opq::data::MeasurememntTimeSeries &time_series);

        /**
         * @brief main loop.
         */
        void loop(bool&running);


    private:
        ///State machine which initializes the two low pass filters.
        enum LocalAnalysisState {
            INITIALIZING_DOWNSAMPLING_FILTER,
            INITIALIZING_LOWPASS_FILTER,
            RUNNING
        };

        LocalAnalysisState _state;


        /**
         * Calculates true rms voltage.
         * @param data adc samples.
         * @return rms voltage.
         */
        float rmsVoltage(int16_t data[]);

        ///How many samples get tossed during downsampling
        static const uint16_t DECIMATION_FACTOR = 10;

        /**
         * Run an itteration of filter initialization.
         * @param m several cycle measurement.
         */
        void initFilter(opq::data::OPQMeasurementPtr &m);


        uint32_t _samplesProcessed;

        //Third party filters.
        AntialiasDownsamplingFilter adf;
        LowPassFilter lpf;

        //Buffer used for the lpf.
        std::vector<float> _downSampled;
        void calculateFrequency();

        ///Input queue.
        opq::data::MeasurementQueue _inQ;
        ///Output queue.
        opq::data::AnalysisQueue _outQ;
        //Time series shared ptr.
        opq::data::MeasurememntTimeSeries _time_series;
    };
}


#endif //ACQUISITION_METRICS_H
