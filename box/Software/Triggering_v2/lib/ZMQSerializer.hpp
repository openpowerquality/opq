#ifndef ACQUISITION_ZMQSERIALIZER_HPP
#define ACQUISITION_ZMQSERIALIZER_HPP

#include <iostream>
#include <string>
#include "opqdata.hpp"
#include <memory>
#include <zmqpp/zmqpp.hpp>

using std::unique_ptr;

namespace opq {
    /**
     * @brief zeromq connector to the acquisition network service.
     * All of the configuration parameters are loaded via the Settings object.
     */
    class ZMQSerializer {
    public:
        /**
         * @brief Creates a new encrypted ZMQ connection.
         */
        ZMQSerializer();

        /**
         * @brief Send an analysis result to the network.
         * @param message message to be sent.
         */
        void sendToZMQ(data::OPQAnalysisPtr message);
    private:
        int _boxId;
        zmqpp::context _ctx;
        zmqpp::socket _client;
        std::string _idString;
    };

    ///@brief Overloaded left shift operator for convenience.
    ZMQSerializer& operator<<(ZMQSerializer& zmq, data::OPQAnalysisPtr message);
};

#endif //ACQUISITION_ZMQSERIALIZER_HPP
