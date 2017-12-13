#include <Analysis.hpp>

using namespace opq::analysis_util;

//FFT

MeasurementFFT::MeasurementFFT(size_t window_count){
	count  = window_count * opq::data::SAMPLES_PER_CYCLE;
	out_buffer = new fftwf_complex[count/2 + 1];
	in_buffer = new float[count];
	dft_plan = fftwf_plan_dft_r2c_1d(count,
		in_buffer,
		out_buffer,
		FFTW_MEASURE);
}

MeasurementFFT::~MeasurementFFT(){
	delete[] out_buffer;
	delete[] in_buffer;
	fftwf_destroy_plan(dft_plan);
}


float MeasurementFFT::compute_thd_and_filter_harmonics(){
    using namespace opq::data;
    float fft_resolution = 1.0*SAMPLING_RATE/count;

    size_t sixty_hz_bin = 60.0/(fft_resolution);

    if (sixty_hz_bin > count)
        return 0;

    float sixty_hz_power = out_buffer[sixty_hz_bin][0]* out_buffer[sixty_hz_bin][0]+
			out_buffer[sixty_hz_bin][1]*out_buffer[sixty_hz_bin][1];
    sixty_hz_power = sqrt(sixty_hz_power);
	out_buffer[sixty_hz_bin][0] = 0;
	out_buffer[sixty_hz_bin][1] = 0;

    float harmonics = 0;

    for (size_t i = sixty_hz_bin*2; i < count; i += sixty_hz_bin){
        harmonics += out_buffer[i][0]* out_buffer[i][0]+
				out_buffer[i][1]*out_buffer[i][1];
		out_buffer[i][0] = 0;
		out_buffer[i][1] = 0;
    }
    return sqrt(harmonics)/sixty_hz_power;
}


void MeasurementFFT::transform(opq::data::OPQMeasurementPtr m){
	size_t index = 0;
	for(auto && frame : m->cycles){
		for(size_t sample = 0; sample < opq::data::SAMPLES_PER_CYCLE; sample++){
			in_buffer[index] = (float)frame.data[sample];
			index++; 
		}
	}
	fftwf_execute(dft_plan);
}

fftwf_complex * MeasurementFFT::last_result() {
    return out_buffer;
}
//IFFT

MeasurementIFFT::MeasurementIFFT(size_t window_count){
	count  = window_count * opq::data::SAMPLES_PER_CYCLE;
	in_buffer = new fftwf_complex[count/2 +1];
	out_buffer = new float[count];
	dft_plan = fftwf_plan_dft_c2r_1d(count,
		in_buffer,
		out_buffer,
		FFTW_MEASURE);
}

MeasurementIFFT::~MeasurementIFFT(){
	delete[] out_buffer;
	delete[] in_buffer;
	fftwf_destroy_plan(dft_plan);
}

float* MeasurementIFFT::execute(fftwf_complex* buf){
	for(size_t index = 0; index < count/2+1; index++){
		in_buffer[index][REAL] = buf[index][REAL];
		in_buffer[index][IMAG] = buf[index][IMAG];
	}
	fftwf_execute(dft_plan);
	return out_buffer;
}
