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
    zmqpp::socket_type type = zmqpp::socket_type::req;
    auto req = zmqpp::socket(ctx, type);
    req.connect("tcp://localhost:9884");
    opq::proto::RequestEventMessage m;

    uint64_t now = chrono_to_mili_now();

    m.set_type("TEST EVENT");
    m.set_description("This is a test event");
    m.set_forward(now - 10000);
    m.set_back(now - 20000);
    req.send(m.SerializeAsString());
    std::string out;
    req.receive(out);
    cout << out << endl;
}