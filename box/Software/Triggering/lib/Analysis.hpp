#ifndef ACQUISITION_ANALYSIS_UTIL_H
#define ACQUISITION_ANALYSIS_UTIL_H
#include "opqdata.hpp"
#include <fftw3.h>

namespace opq{
namespace analysis_util{

static const size_t REAL=0;
static const size_t IMAG=1;

class MeasurementFFT{
public:
	MeasurementFFT(size_t window_count);
	~MeasurementFFT();
	fftwf_complex* execute(opq::data::OPQMeasurementPtr m);
private:
	fftwf_plan dft_plan;
	fftwf_complex* out_buffer;
	float* in_buffer;
	size_t count;
};

class MeasurementIFFT{
public:
	MeasurementIFFT(size_t window_count);
	~MeasurementIFFT();
	float* execute(fftwf_complex* buf);
private:
	fftwf_plan dft_plan;
	float* out_buffer;
	fftwf_complex* in_buffer;
	size_t count;
};
}
}
#endif
