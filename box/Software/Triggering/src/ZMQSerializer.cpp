#include "ZMQSerializer.hpp"
#include "Settings.hpp"
#include "util.hpp"
#include "boost/log/trivial.hpp"
#include <zmqpp/zmqpp.hpp>

using namespace opq;
using namespace std::string_literals;
using std::string;
using std::pair;

auto load_certificate( string const& path ) -> pair<string, string>;

ZMQSerializer::ZMQSerializer() :  _ctx(),_client(_ctx, zmqpp::socket_type::pub) {
    Settings *set = Settings::Instance();

    _boxId = set->getInt("box_id");
    _idString = std::to_string(_boxId);

    std::string host = set->getString("zmq.trigger_host");;
    std::string server_cert_path = set->getString("zmq.server_cert");;
    std::string private_cert_path = set->getString("zmq.private_cert");

    auto my_cert = load_certificate(private_cert_path);
    auto server_cert = load_certificate(server_cert_path);
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

#include <regex>
#include <fstream>

using std::regex;
using std::regex_search;

auto public_re = regex{R"r(public-key\s+=\s+"(.+)")r"};
auto private_re = regex{R"r(secret-key\s+=\s+"(.+)")r"};

auto load_certificate(string const &path) -> pair<string, string> {
    auto file = std::ifstream{ path };
    assert(file);

    auto ss = std::stringstream{};
    ss << file.rdbuf();
    auto contents = ss.str();

    auto public_sm = std::smatch{}, private_sm = std::smatch{};

    auto has_public = regex_search(contents, public_sm, public_re);
    auto has_private = regex_search(contents, private_sm, private_re);

    return {has_public ? public_sm[1] : ""s,
            has_private ? private_sm[1] : ""s};
}
