#include "LocalAnalysis.hpp"
#include "Settings.hpp"
#include "Analysis.hpp"
#include <math.h>
#include <boost/log/trivial.hpp>
#include <algorithm>
#include <numeric>
#include <opqdata.hpp>

using namespace opq;
using namespace opq::data;
using namespace std;

LocalAnalysis::LocalAnalysis(opq::data::MeasurementQueue inQ, opq::data::AnalysisQueue outQ, opq::data::MeasurememntTimeSeries &time_series) {
    _inQ = inQ;
    _outQ = outQ;
    _time_series = time_series;
    _state = INITIALIZING_DOWNSAMPLING_FILTER;
    AntialiasDownsamplingFilter_init(&adf);
    LowPassFilter_init(&lpf);
}

void LocalAnalysis::loop(bool &running) {
    auto settings = Settings::Instance();
    float calConstant = settings->getFloat("acquisition_calibration_constant");
    BOOST_LOG_TRIVIAL(info) << "Analysis filter setup....";
    opq::analysis_util::MeasurementFFT fft(settings->getInt64("frames_per_measurement"));
    cout << "Ready" << endl;
    while (running) {
        opq::data::OPQMeasurementPtr measurement = _inQ->pop();
        if (_state != RUNNING) {
            initFilter(measurement);
            continue;
        }
        opq::data::OPQAnalysisPtr analysis = opq::data::make_analysis();

        analysis->RMS = calculateVoltage(measurement, calConstant);
        settings->setSetting("v",opq::OPQSetting(analysis->RMS));

        analysis->frequency = calculateFrequency(measurement);

        settings->setSetting("f",opq::OPQSetting(analysis->frequency));
        analysis->start = measurement->timestamps.front();
        analysis->current_counter = measurement->cycles[measurement->cycles.size() - 1].current_counter;
        analysis->last_gps_counter = measurement->cycles[measurement->cycles.size() - 1].last_gps_counter;
        analysis->flags = 0;
        for (auto &&frame : measurement->cycles) {
            analysis->flags |= frame.flags;
        }
        fft.transform(measurement);
        analysis->thd = fft.compute_thd_and_filter_harmonics();
        _outQ->push(analysis);
        _time_series->addLatest(measurement->timestamps[0], measurement);
    }
    BOOST_LOG_TRIVIAL(info) << "Analysis thread done";
}

void LocalAnalysis::initFilter(opq::data::OPQMeasurementPtr &m) {
    if (_state == INITIALIZING_DOWNSAMPLING_FILTER) {
        for (auto frame : m->cycles) {
            for (int i = 0; i < opq::data::SAMPLES_PER_CYCLE; i++) {
                AntialiasDownsamplingFilter_put(&adf, frame.data[i]);
                _samplesProcessed++;
            }
        }
        if (_samplesProcessed > ANTIALIASDOWNSAMPLINGFILTER_TAP_NUM) {
            _state = INITIALIZING_LOWPASS_FILTER;
            _samplesProcessed = 0;
        }
    }
    else if (_state == INITIALIZING_LOWPASS_FILTER) {
        for (auto frame : m->cycles) {
            for (int i = 0; i < opq::data::SAMPLES_PER_CYCLE; i++) {
                AntialiasDownsamplingFilter_put(&adf, frame.data[i]);
                if (i % DECIMATION_FACTOR == 0) {
                    LowPassFilter_put(&lpf, AntialiasDownsamplingFilter_get(&adf));
                    _samplesProcessed++;
                }
            }
        }
        if (_samplesProcessed > INITIALIZING_LOWPASS_FILTER) {
            BOOST_LOG_TRIVIAL(info) << "Analysis filters ready";
            _state = RUNNING;
            _samplesProcessed = 0;
        }
    }
}

float LocalAnalysis::calculateFrequency(opq::data::OPQMeasurementPtr measurement) {
    //Filter the data;
    //Buffer used for the lpf.
    std::vector<float> downSampled;
    for (auto &&frame : measurement->cycles) {
        for (int i = 0; i < SAMPLES_PER_CYCLE; i++) {
            AntialiasDownsamplingFilter_put(&adf, frame.data[i]);
            if (i % DECIMATION_FACTOR == 0) {
                float antialiased_value = AntialiasDownsamplingFilter_get(&adf);
                LowPassFilter_put(&lpf, antialiased_value);
                downSampled.push_back(LowPassFilter_get(&lpf));
            }
        }
    }
    //Find the zero crossings.
    std::vector<float> zeroCrossings;
    float last = FP_NAN;
    float next = 0;
    for (size_t i = 0; i < downSampled.size(); i++) {
        if (last != FP_NAN) {
            if ((last <= 0 && downSampled[i] > 0) || (last < 0 && downSampled[i] >= 0)) {
                next = downSampled[i];
                zeroCrossings.push_back(1.0f * i - (next) / (next - last));
            }
        }
        last = downSampled[i];
    }

    float accumulator = 0;
    for (size_t i = 1; i < zeroCrossings.size(); i++) {
        accumulator += zeroCrossings[i] - zeroCrossings[i - 1];
    }
    accumulator /= zeroCrossings.size() - 1;
    return  SAMPLES_PER_CYCLE *
                          CYCLES_PER_SEC /
                          DECIMATION_FACTOR /
                          accumulator;
}


float LocalAnalysis::calculateVoltage(opq::data::OPQMeasurementPtr measurement, float calConstant){
    //Calculate rms voltage
    float rms = std::accumulate(measurement->cycles.begin(), measurement->cycles.end(), (float)0. ,
                                 [this](float accm, auto && frame){
                                     return accm + this->rmsVoltage(frame.data);
                                 });
    rms /= measurement->cycles.size();
    rms /= calConstant;
    return rms;
}


float LocalAnalysis::rmsVoltage(int16_t data[]) {
    float av = 0;
    for (int i = 0; i < opq::data::SAMPLES_PER_CYCLE; i++) {
        av += 1.0 * data[i] * data[i];
    }
    return sqrtf((float) av / opq::data::SAMPLES_PER_CYCLE);
}
