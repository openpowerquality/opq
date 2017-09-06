#include "ZMQTrigger.hpp"
#include "ZMQSerializer.hpp"
#include "Settings.hpp"
#include "opq.pb.h"
#include "util.hpp"
#include <opqdata.hpp>
#include <string>
#include <boost/log/trivial.hpp>
using namespace opq;

ZMQTrigger::ZMQTrigger(opq::data::AnalysisQueue q) {
    _q = q;
}


void ZMQTrigger::loop(bool &running) {
    ZMQSerializer zmq;
    while (running) {
        auto message = _q->pop();
        zmq << message;
    }
    BOOST_LOG_TRIVIAL(info) << "ZMQ thread done";
}
