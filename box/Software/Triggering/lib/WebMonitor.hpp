#ifndef HTML_BULLSHIT_WEBMONITOR_HPP
#define HTML_BULLSHIT_WEBMONITOR_HPP

#include "../mongoose/mongoose.h"
#include "string"
#include "opqdata.hpp"

class WebMonitor {
public:
    WebMonitor(opq::data::MeasurementQueue mq,
    opq::data::AnalysisQueue aq,
    opq::data::MeasurememntTimeSeries ts);
    void loop(bool & running);
private:
    void push_data_to_all_WebSocket_connections(std::string);
    std::string buildMessage();
    bool is_websocket(const struct mg_connection *nc);
    bool _running;
    struct mg_mgr _mgr;
    struct mg_connection *_nc;
    opq::data::MeasurementQueue _mq;
    opq::data::AnalysisQueue _aq;
    opq::data::MeasurememntTimeSeries _ts;

};


#endif //HTML_BULLSHIT_WEBMONITOR_HPP
