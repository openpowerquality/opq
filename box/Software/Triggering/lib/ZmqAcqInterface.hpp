#ifndef TRIGGERING_ZMQINTERFACE_HPP
#define TRIGGERING_ZMQINTERFACE_HPP

#include "TimeSeries.hpp"
#include "opqdata.hpp"
#include "util.hpp"

void zmq_acq_loop(bool &running, opq::data::MeasurememntTimeSeries t);

#endif //TRIGGERING_ZMQINTERFACE_HPP
