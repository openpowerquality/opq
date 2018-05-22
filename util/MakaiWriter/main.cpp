#include <iostream>
#include <zmqpp/zmqpp.hpp>
#include "opq.pb.h"
#include <chrono>

using namespace std;

inline uint64_t chrono_to_mili(std::chrono::time_point<std::chrono::high_resolution_clock> time) {
    std::chrono::time_point<std::chrono::high_resolution_clock > epoch;
    auto elapsed = time - epoch;
    return std::chrono::duration_cast<std::chrono::milliseconds>(elapsed).count();
}

inline uint64_t chrono_to_mili_now(){
    return chrono_to_mili(std::chrono::high_resolution_clock::now());
}


int main() {
    zmqpp::context ctx;
    // generate a sub socket
    zmqpp::socket_type type = zmqpp::socket_type::push;

    auto push = zmqpp::socket(ctx, type);
    push.connect("tcp://localhost:9884");

    type = zmqpp::socket_type::sub;
    auto sub = zmqpp::socket(ctx, type);
    sub.connect("tcp://localhost:9882");
    sub.subscribe("");

    opq::proto::RequestEventMessage m;

    uint64_t now = chrono_to_mili_now();

    m.set_trigger_type(m.OTHER);
    m.set_description("This is a test event");
    m.set_end_timestamp_ms_utc(now - 10000);
    m.set_start_timestamp_ms_utc(now - 20000);
    m.set_percent_magnitude(50);
    m.set_requestee("test");
    m.set_description("Test event");
    m.set_request_data(true);
    push.send(m.SerializeAsString());
    std::string out;
    zmqpp::message_t msg;
    sub.receive(msg);
    out = msg.get(1);
    cout << out << endl;
}
