#include <iostream>
#include <fstream>

#include <zmqpp/zmqpp.hpp>

#include "json.hpp"
#include "opq.pb.h"

using namespace std;
using json = nlohmann::json;

int main(int argc, char** argv) {
    //Default config
    string configPath = "/etc/opq/makai_reader.json";
    if(argc != 1){
        configPath = argv[1];
    }
    //Read in config file
    ifstream in;
    try {
        in.open(configPath);
    }
    catch (std::ios_base::failure& e) {
        cout << "Could not open the config file" << endl;
        return -1;
    }
    json j;
    string interface;
    try {
        in >> j;
        interface = j["interface"];
    }
    catch(const std::domain_error& e){
        cout << "Malformed config file" << endl;
        return -1;
    }
    catch (const std::invalid_argument& e){
        cout << "Malformed config file" << endl;
        return -1;
    }

    //ZMQ
    zmqpp::context ctx;
    // generate a sub socket
    zmqpp::socket_type type = zmqpp::socket_type::subscribe;
    auto sub = zmqpp::socket(ctx, type);
    try {
        sub.connect(interface);
    }
    catch(const zmqpp::zmq_internal_exception& e){
        cout << "Could not connect to " << interface<< endl;
        return -1;
    }
    sub.subscribe("");

    while (true) {
        auto msg = zmqpp::message{};
        sub.receive(msg);
        opq::proto::TriggerMessage tm;
        tm.ParseFromString(msg.get(1));
        cout << msg.get(0) << " " << tm.time() << " " << tm.rms() << " " <<tm.frequency() << endl;
    }
}
