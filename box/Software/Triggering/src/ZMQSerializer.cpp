#include "ZMQSerializer.hpp"
#include "Settings.hpp"
#include "util.hpp"
#include "boost/log/trivial.hpp"
#include <zmqpp/zmqpp.hpp>

using namespace opq;
using namespace std::string_literals;
using std::string;
using std::pair;

ZMQSerializer::ZMQSerializer() :  _ctx(),_client(_ctx, zmqpp::socket_type::pub) {
    Settings *set = Settings::Instance();

    _boxId = set->getInt("box_id");
    _idString = std::to_string(_boxId);

    std::string host = set->getString("zmq.trigger_host");;
    std::string server_cert_path = set->getString("zmq.server_cert");;
    std::string private_cert_path = set->getString("zmq.private_cert");

    auto my_cert = opq::util::load_certificate(private_cert_path);
    auto server_cert = opq::util::load_certificate(server_cert_path);
    _client.set( zmqpp::socket_option::identity, _idString );
    _client.set( zmqpp::socket_option::curve_secret_key, my_cert.second);
    _client.set( zmqpp::socket_option::curve_public_key, my_cert.first);
    _client.set( zmqpp::socket_option::curve_server_key, server_cert.first);
    _client.set( zmqpp::socket_option::zap_domain, "global" );
    _client.connect(host);
    BOOST_LOG_TRIVIAL(info) << "Sending data Trigger data to "  + host;
}


void ZMQSerializer::sendToZMQ(data::OPQAnalysisPtr message){
    std::string out = util::serialize_to_protobuf(_boxId,message);
    zmqpp::message m;
    m << _idString;
    m << out;
    _client.send(m);
}

ZMQSerializer& opq::operator<<(ZMQSerializer& zmq, data::OPQAnalysisPtr message)
{
    zmq.sendToZMQ(message);
    return zmq;
}