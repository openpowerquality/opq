#include <iostream>
#include <fstream>
#include <thread>
#include <chrono>
#include <mutex>

#include <zmqpp/zmqpp.hpp>

#include "json.hpp"
#include "opq.pb.h"
#include "Statistics.h"

using namespace std;
using json = nlohmann::json;

std::mutex mtx;

void getStatistics(Statistics * stats) {
    while (true) {
        mtx.lock();
        stats->printStatistics(); 
        mtx.unlock();
        std::this_thread::sleep_for(std::chrono::milliseconds(5000));        
    }
}

ifstream setConfig(string configPath) {
    ifstream in;
    try {
        in.open(configPath);
    } catch (std::ios_base::failure& e) {
        cout << "Could not open the config file" << endl;
        exit(EXIT_FAILURE);
    }

    return in;
}

string setInterface(ifstream * in) {
    json j;
    string interface;
    try {
        *in >> j;
        interface = j["interface"];
    } catch (const std::exception& e) {
        cout << "Malformed config file" << endl;
        exit(EXIT_FAILURE);
    }
    
    return interface;
}

int main(int argc, char** argv) {
    ifstream in;
    if (argc != 1) {
        in = setConfig(argv[1]);
    } else {
        in = setConfig("../config.json");
    }
    
    string interface = setInterface(&in);

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

    int64_t uptime = 0;
    int64_t downtime = 0;
    int64_t last = 0;
    Statistics stats(1);
    thread t1(getStatistics, &stats);
    while (true) {
        auto msg = zmqpp::message{};
        sub.receive(msg);
        opq::proto::TriggerMessage tm;
        tm.ParseFromString(msg.get(1));
        if (msg.get(0).compare("1") == 0) {
            if (last == 0) {
                last = tm.time();
                continue;
            } else if ((tm.time() - last) > 60000) {
                downtime = tm.time() - last;
                last = tm.time();
                uptime = 0;
            } else {
                uptime += tm.time() - last;
                last = tm.time();
                downtime = 0;
            }
            mtx.lock();
            stats.setDowntime(downtime);
            stats.setUptime(uptime);
            mtx.unlock();
        }
    }
}
