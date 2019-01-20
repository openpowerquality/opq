#include <iostream>
#include <zmqpp/zmqpp.hpp>
#include "opqbox3.pb.h"
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

    uint64_t now = chrono_to_mili_now();

    opq::proto3::GetDataCommand dcmd;
    dcmd.set_start_ms(now - 20000);
    dcmd.set_end_ms(now - 10000);
    dcmd.set_wait(false);

    opq::proto3::Command cmd;
    cmd.set_box_id(-1);
    cmd.set_identity("test");
    cmd.set_timestamp_ms(now);
    cmd.set_allocated_data_command(&dcmd);

    std::string out;
    cmd.SerializeToString(&out);
    push.send(out);

    zmqpp::message_t msg;
    sub.receive(msg);
    cout << msg.get(1) << endl;
}
