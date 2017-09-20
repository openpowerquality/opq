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

void WebMonitor::push_data_to_all_WebSocket_connections(std::string str) {
    struct mg_connection *c;
    for (c = mg_next(&_mgr, NULL); c != NULL; c = mg_next(&_mgr, c)) {
        if (is_websocket(c)) {
            mg_send_websocket_frame(c, WEBSOCKET_OP_TEXT, str.c_str() ,str.length());
        }
    }
}

void WebMonitor::loop(bool& running) {
    static struct mg_serve_http_opts s_http_server_opts;
    mg_mgr_init(&_mgr, NULL);
    _nc = mg_bind(&_mgr, "8080", [](struct mg_connection *nc, int ev, void *ev_data){
        if(ev == MG_EV_HTTP_REQUEST)
            mg_serve_http(nc, (struct http_message *) ev_data, s_http_server_opts);
    });
    if(!_nc) throw std::runtime_error("Could not serve http");
    mg_set_protocol_http_websocket(_nc);
    s_http_server_opts.document_root = "../html/";  // Serve current directory
    s_http_server_opts.enable_directory_listing = "no";

    std::chrono::system_clock::time_point last = std::chrono::system_clock::now();
    while(running){
        mg_mgr_poll(&_mgr, 1000/6);
        std::chrono::system_clock::time_point now = std::chrono::system_clock::now();
        if((now - last) > std::chrono::milliseconds(1000/6)) {
            last = now;
            push_data_to_all_WebSocket_connections(buildMessage());
        }
    }
    mg_mgr_free(&_mgr);
}

std::string WebMonitor::buildMessage() {
    using json = nlohmann::json;
    json j;
    j["q"] = {
            {"r", _mq->size() > 100 ? 100 : _mq->size()},
            {"a", _aq->size() > 100 ? 100 : _aq->size()},
            {"z", 0},
            {"d", _ts->getSize()*100.0/_ts->getMax()}
    };
    auto settings = opq::Settings::Instance();
    j["v"] = settings->getFloat("v");
    j["f"] = settings->getFloat("f");

    return j.dump();

}