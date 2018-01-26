#include "RequestHandler.h"
#include "util.h"
#include "opq.pb.h"
#include <zmqpp/socket.hpp>
#include <zmqpp/message.hpp>
#include <string>
#include <MongoDriver.h>
#include <thread>
#include <syslog.h>

using namespace std::string_literals;

using namespace std;

RequestHandler::RequestHandler(Config &c, zmqpp::context &ctx) : _ctx(ctx), _config(c){
}

void RequestHandler::handle_request_loop() {

    auto backend_rep = zmqpp::socket(_ctx, zmqpp::socket_type::rep);
    //Connect to mauka broker
    //This is where the data requests come in.
    backend_rep.bind(_config.backend_interface_rep);

    MongoDriver mongo{};

    //Get the last event number from mongo.
    uint32_t event_number = mongo.get_next_event_number();

    syslog(LOG_NOTICE, ("Next event number will be " + std::to_string(event_number)).c_str());

    //Encrypted/Box End
    auto box_pub = zmqpp::socket{ _ctx, zmqpp::socket_type::pub };
    auto server_cert = load_certificate(_config.private_cert);
    box_pub.set( zmqpp::socket_option::curve_server, true );
    box_pub.set( zmqpp::socket_option::curve_secret_key, server_cert.second );
    box_pub.set( zmqpp::socket_option::zap_domain, "global" );
    box_pub.bind(_config.box_interface_pub);
    _done = false;

    int ping_counter = 0;
    int ping_sequence = 0;

    while(!_done){
        //recieve a request for event message
        zmqpp::message z_request_event;
        if(!backend_rep.receive(z_request_event, true)){
            std::this_thread::sleep_for(500ms);
            ping_counter++;
            if(ping_counter > 25) {
                zmqpp::message z_ping;
                opq::proto::RequestDataMessage ping_message;
                ping_message.set_type(ping_message.PING);
                ping_message.set_sequence_number((uint32_t)ping_sequence);
                ping_sequence++;
                ping_counter = 0;
                z_ping.add(BOX_EVENT_GET_TOPIC);
                z_ping.add(ping_message.SerializeAsString());
                box_pub.send(z_ping);
            }
            continue;
        }
        ping_counter = 0;
        //Deserialize

        //Deserialize
        opq::proto::RequestEventMessage request_event;
        if (z_request_event.parts() == 0 || !request_event.ParseFromString(z_request_event.get(0))) {
            syslog(LOG_WARNING, "Could not understand request for event.");
            continue;
        }

        //current time
        //uint64_t request_time = chrono_to_mili_now();
        uint64_t event_time = (request_event.end_timestamp_ms_utc() + request_event.start_timestamp_ms_utc())/2;

        mongo.create_event(request_event, event_time, event_number);

        //Reply to the requester with an event id
        zmqpp::message z_reply_event;
        z_reply_event.add(to_string(event_number));
        backend_rep.send(z_reply_event);
        if(!request_event.request_data()){
            event_number++;
            continue;
        }
        //Compose a message to the opqboxes
        zmqpp::message z_request_data;
        opq::proto::RequestDataMessage request_data;
        //Sequence is the event number so we know where the data belongs on the receiving end.
        request_data.set_sequence_number(event_number);
        //Time of the request
        request_data.set_time(event_time);

        //Set the ranges for the request
        request_data.set_back(request_event.start_timestamp_ms_utc());
        request_data.set_forward(request_event.end_timestamp_ms_utc());

        //Set the request type
        request_data.set_type(opq::proto::RequestDataMessage::READ);

        //Set the topic
        z_request_data.add(BOX_EVENT_GET_TOPIC);
        //Serialize the message
        z_request_data.add(request_data.SerializeAsString());
        //Blast it to the boxen
        box_pub.send(z_request_data);
        //Increment event number
        event_number++;
    }

}
