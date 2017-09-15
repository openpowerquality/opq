#include "ZmqAcqInterface.hpp"
#include <zmqpp/zmqpp.hpp>
#include <Settings.hpp>
#include <boost/log/trivial.hpp>

#include "opq.pb.h"

using namespace std;

void zmq_acq_loop(bool &running, opq::data::MeasurememntTimeSeries time_series) {

    auto settings = opq::Settings::Instance();
    auto ctx = zmqpp::context();
    auto private_cert = opq::util::load_certificate(settings->getString("zmq.private_cert"));
    auto server_cert = opq::util::load_certificate(settings->getString("zmq.server_cert"));

    auto recv_address = settings->getString("zmq.acq_recv_host");
    auto send_address = settings->getString("zmq.acq_send_host");
    BOOST_LOG_TRIVIAL(info) << "Sending raw data to " << send_address;
    BOOST_LOG_TRIVIAL(info) << "Recieving raw data request from " << recv_address;
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
    while(running) {
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
            BOOST_LOG_TRIVIAL(warning) << "Could not understand request from server";
            continue;
        }
        m.set_time(opq::util::crono_to_mili(std::chrono::high_resolution_clock::now()));
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
                auto start = opq::util::mili_to_crono(m.back());
                auto stop = opq::util::mili_to_crono(m.forward());
                std::time_t ttp = std::chrono::system_clock::to_time_t(start);
                std::cout << "start: " << std::ctime(&ttp) << " " <<m.back() << endl;

                ttp = std::chrono::system_clock::to_time_t(stop);
                std::cout << "stop: " << std::ctime(&ttp) << " " << m.forward() << endl;

                auto cycles = time_series->getTimeRange(start, stop);
                cout << cycles.size() << endl;
                for (auto &cycle : cycles) {
                    response.add(opq::util::serialize_to_protobuf(box_id, cycle));
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
