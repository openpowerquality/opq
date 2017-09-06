#ifndef ACQUISITIONBROKER_REQUESTHANDLER_H
#define ACQUISITIONBROKER_REQUESTHANDLER_H

#include <zmqpp/context.hpp>
#include "config.h"
//Handles requests for events and logs metadata
class RequestHandler {
public:
    //We steal the references of global config and context
    RequestHandler(Config& c, zmqpp::context &ctx);
    //handling loop
    void handle_request_loop();
private:
    //Reference to zmq context. Shared between all of the zmq sockets
    zmqpp::context &_ctx;
    //Configuration
    Config &_config;
    //loop done flag.
    bool _done;
};

#endif //ACQUISITIONBROKER_REQUESTHANDLER_H
