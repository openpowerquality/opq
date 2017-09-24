#include <boost/log/core.hpp>
#include <boost/log/trivial.hpp>
#include "WebMonitor.hpp"
#include "json.hpp"
#include "Settings.hpp"
WebMonitor::WebMonitor(opq::data::MeasurementQueue mq, opq::data::AnalysisQueue aq,
                       opq::data::MeasurememntTimeSeries ts) {
    _mq = mq;
    _aq = aq;
    _ts = ts;
}

bool WebMonitor::is_websocket(const struct mg_connection *nc) {
    return nc->flags & MG_F_IS_WEBSOCKET;
}

void WebMonitor::push_data_to_all_WebSocket_connections() {
    struct mg_connection *c;
    std::string str = "";
    bool buildString = true;
    for (c = mg_next(&_mgr, NULL); c != NULL; c = mg_next(&_mgr, c)) {
        if (is_websocket(c)) {
            if(buildString){
                buildString = false;
                str = buildMessage();
            }
            mg_send_websocket_frame(c, WEBSOCKET_OP_TEXT, str.c_str() ,str.length());
        }
    }
}

void WebMonitor::loop(bool& running) {

    static struct mg_serve_http_opts s_http_server_opts;
    mg_mgr_init(&_mgr, NULL);


    auto settings = opq::Settings::Instance();
    std::string port = settings->getString("monitor.port");
    std::string html_path = settings->getString("monitor.html");
    BOOST_LOG_TRIVIAL(info) << "Monitor running on port " << port;
    _nc = mg_bind(&_mgr, port.c_str(), [](struct mg_connection *nc, int ev, void *ev_data){
        if(ev == MG_EV_HTTP_REQUEST)
            mg_serve_http(nc, (struct http_message *) ev_data, s_http_server_opts);
    });
    if(!_nc) throw std::runtime_error("Could not serve http");
    mg_set_protocol_http_websocket(_nc);
    s_http_server_opts.document_root = html_path.c_str();
    s_http_server_opts.enable_directory_listing = "no";

    std::chrono::system_clock::time_point last = std::chrono::system_clock::now();
    while(running){
        mg_mgr_poll(&_mgr, 1000/6);
        std::chrono::system_clock::time_point now = std::chrono::system_clock::now();
        if((now - last) > std::chrono::milliseconds(1000/6)) {
            last = now;
            push_data_to_all_WebSocket_connections();
        }
    }
    mg_mgr_free(&_mgr);
}

std::string WebMonitor::buildMessage() {
    using json = nlohmann::json;
    json j;
    j["q"] = {
            {"r", _mq->size() > 10 ? 100 : 100.0*_mq->size()/10},
            {"a", _aq->size() > 10 ? 100 : 100.0*_aq->size()},
            {"z", 0},
            {"d", _ts->getSize()*100.0/_ts->getMax()}
    };
    auto settings = opq::Settings::Instance();
    j["v"] = settings->getFloat("v");
    j["f"] = settings->getFloat("f");

    return j.dump();

}