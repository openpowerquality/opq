#include <unistd.h>
#include <sys/stat.h>
#include <fcntl.h>
#include <math.h>
#include <iostream>
#include "calibration.hpp"

inline bool readCycle(int fd, OPQCycle &cycle){
	if(read(fd, &cycle, sizeof(OPQCycle)) != sizeof(OPQCycle)) return false;
	return true;
}

float getCalibrationConstant() {
	float av = 0;
	int fd = open("/dev/opq0", O_RDONLY);
	
	if (fd < 0) {
		// throw exception
		return 0.0;
	}

	for (int i = 0; i < 10; i++) {
		OPQCycle cycle;
		readCycle(fd, cycle);
		for (int j = 0; j < SAMPLES_PER_CYCLE; j++) {
			av += 1.0 * cycle.data[j] * cycle.data[j];
		}
	}
	return sqrtf((float) av / SAMPLES_PER_CYCLE * 10);
}

int main() {
	float calibrationConst = getCalibrationConstant();
	return calibrationConst;
}
