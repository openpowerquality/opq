#include <stdexcept>
#include <memory>
#include <unistd.h>
#include <iostream>
#include <chrono>

#include "Settings.hpp"
#include "Reader.hpp"
#include "opqdata.hpp"

#include <boost/log/trivial.hpp>

using namespace std;
using namespace opq;
using namespace opq::data;


#ifdef OPQ_DEBUG

#include <math.h>
#include <time.h>
#include <stdlib.h>
#else
#include <sys/types.h>
#include <sys/stat.h>
#include <fcntl.h>
#include <opqdata.hpp>

#endif

Reader::Reader(MeasurementQueue &q){
    _q = q;
#ifndef OPQ_DEBUG
    BOOST_LOG_TRIVIAL(info) << "Opening /dev/opq0";
    _fd = ::open("/dev/opq0",O_RDONLY);
    if(_fd < 0){
       BOOST_LOG_TRIVIAL(fatal) << "Could not open /dev/opq0";
       exit(0);
    }
#else
    BOOST_LOG_TRIVIAL(info) << "Running in simulation mode";
    srand(time(NULL));
#endif
    auto settings = Settings::Instance();
    _frames_per_measurement = settings->getInt("frames_per_measurement");
    _fpm_callback_id = settings->onChangeCallback("frames_per_measurement",
    [=](OPQSetting s){this->_onFramesPerMeasurementChange(s);}
    );
}

Reader::~Reader(){
    ::close(_fd);
    auto settings = Settings::Instance();
    settings->removeChangeCallback("frames_per_measurement", _frames_per_measurement);
}

void Reader::loop(bool &running){
    while(running){
        int current_frame = 0;
        auto measurement = make_measurement();
        while(current_frame < _frames_per_measurement){
            measurement->cycles.push_back(OPQCycle());
            if(!data::readCycle(_fd, measurement->cycles[current_frame])){
                BOOST_LOG_TRIVIAL(fatal) << "Could not communicate with driver.";
                exit(0);
            }
            measurement->timestamps.push_back(std::chrono::high_resolution_clock::now());
            current_frame++;
        }
        _q->push(measurement);
    }
    BOOST_LOG_TRIVIAL(info) << "Reader thread done";
}

void Reader::_onFramesPerMeasurementChange(OPQSetting s) {
    _frames_per_measurement = boost::get<int>(s);
}
