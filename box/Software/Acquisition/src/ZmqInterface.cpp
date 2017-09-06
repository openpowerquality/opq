#include "ZmqInterface.hpp"
#include "RedisInterface.hpp"
#include <zmqpp/zmqpp.hpp>
#include <Settings.hpp>
#include <regex>
#include <fstream>
#include <chrono>
#include <thread>

#include "opq.pb.h"

using namespace std;

pair<string, string> load_certificate(string const &path);
inline uint64_t chrono_to_mili(std::chrono::time_point<std::chrono::high_resolution_clock > time);

void zmq_loop() {
    RedisInterface redis;

    auto settings = opq::Settings::Instance();
    auto ctx = zmqpp::context();
    auto private_cert = load_certificate(settings->getString("zmq.private_cert"));
    auto server_cert = load_certificate(settings->getString("zmq.server_cert"));

    auto recv_address = settings->getString("zmq.acq_recv_host");
    auto send_address = settings->getString("zmq.acq_send_host");

    auto box_id = settings->getInt("box_id");

    auto recv = zmqpp::socket{ctx, zmqpp::socket_type::sub};
    recv.set(zmqpp::socket_option::curve_server_key, server_cert.first);
    recv.set(zmqpp::socket_option::curve_public_key, private_cert.first);
    recv.set(zmqpp::socket_option::curve_secret_key, private_cert.second);
    recv.set(zmqpp::socket_option::zap_domain, "global" );
    recv.subscribe("");
    recv.connect(recv_address);
    
    auto send = zmqpp::socket{ctx, zmqpp::socket_type::push};
    send.set(zmqpp::socket_option::curve_server_key, server_cert.first);
    send.set(zmqpp::socket_option::curve_public_key, private_cert.first);
    send.set(zmqpp::socket_option::curve_secret_key, private_cert.second);
    send.set(zmqpp::socket_option::zap_domain, "global" );
    send.connect(send_address);

    int reset_counter = 0;
    while(true) {
        zmqpp::message request;
        if(!recv.receive(request, true)){
            std::this_thread::sleep_for(500ms);
            reset_counter++;
            if (reset_counter > 120){
                reset_counter = 0;
                recv = zmqpp::socket{ctx, zmqpp::socket_type::sub};
                recv.set(zmqpp::socket_option::curve_server_key, server_cert.first);
                recv.set(zmqpp::socket_option::curve_public_key, private_cert.first);
                recv.set(zmqpp::socket_option::curve_secret_key, private_cert.second);
                recv.set(zmqpp::socket_option::zap_domain, "global" );
				recv.connect(recv_address);
                recv.subscribe("");
		        cout << "reset" << endl;
            }
            continue;
        }

        reset_counter = 0;

        auto m = opq::proto::RequestDataMessage();
        if(!m.ParseFromString(request.get(1))){
            cout << "Could not understand request from server" << endl;
            continue;
        }
        m.set_time(chrono_to_mili(std::chrono::high_resolution_clock::now()));
        m.set_boxid(box_id);
        switch(m.type()){
            case m.PING:
                m.set_type(m.PONG);
                send.send(m.SerializeAsString());
                break;
            case m.READ: {
                //Respond with data
                zmqpp::message response;
                m.set_type(m.RESP);
                response.add(m.SerializeAsString());
                auto cycles = redis.getMeasurementsForRange(m.back(), m.forward());
                for (auto &cycle : cycles) {
                    response.add(cycle);
                }
                send.send(response);
            }
                break;
            default:
                //Respond with Error
                m.set_type(m.ERROR);
                send.send(m.SerializeAsString());
                break;
        };
    }

}

auto public_re = regex{R"r(public-key\s+=\s+"(.+)")r"};
auto private_re = regex{R"r(secret-key\s+=\s+"(.+)")r"};

pair<string, string> load_certificate(string const &path) {
    std::ifstream file(path);
    assert(file);

    std::stringstream ss;
    ss << file.rdbuf();
    auto contents = ss.str();

    auto public_sm = std::smatch(), private_sm = std::smatch();

    pair<string, string> ret = make_pair("","");

    if(regex_search(contents, public_sm, public_re)){
        ret.first = public_sm[1];
    }
    if(regex_search(contents, private_sm, private_re)){
        ret.second = private_sm[1];
    }
    return ret;
}

uint64_t chrono_to_mili(std::chrono::time_point<std::chrono::high_resolution_clock> time) {
    std::chrono::time_point<std::chrono::high_resolution_clock > epoch;
    auto elapsed = time - epoch;
    return std::chrono::duration_cast<std::chrono::milliseconds>(elapsed).count();
}


