#include <zmqpp/socket.hpp>
#include <zmqpp/message.hpp>
#include "DataHandler.h"
#include "MongoDriver.h"
#include "util.h"
#include <syslog.h>
#include "opq.pb.h"

using namespace std;

DataHandler::DataHandler(Config &c, zmqpp::context &ctx) : _ctx(ctx), _config(c) {
}

void DataHandler::handle_data_loop() {
    
    MongoDriver mongo(_config.mongo_uri);
    //Socket that pulls data from boxes.
    auto box_pull = zmqpp::socket{_ctx, zmqpp::socket_type::pull};
    auto server_cert = load_certificate(_config.private_cert);
    box_pull.set(zmqpp::socket_option::curve_server, true);
    box_pull.set(zmqpp::socket_option::curve_secret_key, server_cert.second);
    box_pull.set(zmqpp::socket_option::zap_domain, "global");
    box_pull.bind(_config.box_interface_pull);
    _done = false;
    while (!_done) {
        //Receive a data message
        zmqpp::message zm;
        box_pull.receive(zm);

        //Deserialize
        auto serialized_resp = zm.get(0);
        opq::proto::RequestDataMessage header;
        header.ParseFromString(serialized_resp);

        //Get the boxID and the event number
        auto sequence_number = header.sequence_number();

        if(header.type() == header.RESP) {
            std::vector<opq::proto::DataMessage> messages;
            syslog(LOG_NOTICE, "%s",  ("Event " + std::to_string(sequence_number) + ": Received data from box "  + std::to_string(header.boxid()) + " with " + std::to_string((int)zm.parts() -1) + " parts").c_str() );
            //Push every part of the message except for the header to redis.
            for (size_t i = 1; i < zm.parts(); i++) {
                opq::proto::DataMessage m;
                if(m.ParseFromString(zm.get(i)));
                    messages.push_back(m);
            }
            if(messages.size() > 0)
                mongo.append_data_to_event(messages, sequence_number);
        }
    }

}
