#ifndef ACQUISITIONBROKER_DATAHANDLER_H
#define ACQUISITIONBROKER_DATAHANDLER_H

#include <zmqpp/context.hpp>
#include "config.h"

//Handles the data comming from the box and talks to Mauka
class DataHandler {
public:
    //We steal the references of global config and context
    DataHandler(Config &c, zmqpp::context &ctx);
    //handling loop
    void handle_data_loop();
private:
    //Reference to zmq context. Shared between all of the zmq sockets
    zmqpp::context &_ctx;
    //Configuration
    Config &_config;
    //loop done flag.
    bool _done;
};


#endif //ACQUISITIONBROKER_DATAHANDLER_H
