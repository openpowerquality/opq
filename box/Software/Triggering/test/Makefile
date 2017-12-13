all:ffttest

ffttest: ffttest.cpp
	 g++ ffttest.cpp ../src/Analysis.cpp -I../lib/ -O3 -std=c++11 -lfftw3 -lfftw3f -lm -o ffttest

clean:
	rm -rf ffttest
