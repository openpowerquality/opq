#define OPQ_DEBUG

#include "../lib/Analysis.hpp"
#include "../lib/opqdata.hpp"
#include <ctime>
#include <iostream>

using namespace std;

using namespace opq::data;
using namespace opq::analysis_util;
static const int WINDOW_COUNT = 10;

int main() {
    clock_t begin_time;
    OPQMeasurementPtr measurement = make_measurement();
    begin_time = clock();
    MeasurementFFT fft(WINDOW_COUNT);
    MeasurementIFFT ifft(WINDOW_COUNT);
    cout << "Pregenerating fft: " << float(clock() - begin_time) / CLOCKS_PER_SEC << "s" << endl;

    cout << "Filling buffer..";
    for (int i = 0; i < WINDOW_COUNT; i++) {
        measurement->cycles.push_back(OPQCycle());
        readCycle(-1, measurement->cycles[i]);
        measurement->timestamps.push_back(std::chrono::high_resolution_clock::now());
    }
    cout << "[Done]" << endl;

    begin_time = clock();
    fftwf_complex *fft_result;

    for (int i = 0; i < 1000; i++) {
        fft.transform(measurement);
        fft_result = fft.last_result();
        if (i % 100 == 0)
            cout << "." << flush;
    }
    cout << endl;
    cout << "Time per FFT operation: " << float(clock() - begin_time) / CLOCKS_PER_SEC / 10 << "s" << endl;

    begin_time = clock();
    float *ifft_result;
    for (int i = 0; i < 1000; i++) {
        ifft_result = ifft.execute(fft_result);
        if (i % 100 == 0)
            cout << "." << flush;
    }
    cout << endl;
    cout << "Time per IFFT operation: " << float(clock() - begin_time) / CLOCKS_PER_SEC / 10 << "s" << endl;
    float residual = 0;
    for (int i = 0; i < WINDOW_COUNT; i++) {
        for (int j = 0; j < SAMPLES_PER_CYCLE; j++) {
            float orig = measurement->cycles[i].data[j];
            float res = ifft_result[i * SAMPLES_PER_CYCLE + j];
            residual += fabs(res / WINDOW_COUNT / SAMPLES_PER_CYCLE - orig);
        }
    }
    cout << "Residual: " << residual << endl;
    cout << "Average error per sample " << residual / WINDOW_COUNT / SAMPLES_PER_CYCLE << endl;
}
