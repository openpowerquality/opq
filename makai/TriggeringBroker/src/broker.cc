#include "../lib/config.hpp"

#include <iostream>
#include <memory>
#include <vector>

#include "zmqpp/zmqpp.hpp"
#include <experimental/filesystem>
#include "zmqpp/proxy.hpp"
#include <regex>
#include <fstream>

using namespace std::string_literals;
using namespace std;
namespace fs = std::experimental::filesystem;
/*
 * Loads a certificate from a file as a pair of strings.
 */
auto load_certificate( string const& path ) -> pair<string, string>;

int main (int argc, char **argv) {
    cout << "Parsing config." << endl;

    auto config = argc == 1 ? Config{} : Config{ argv[1] };
    cout << "public certs: " << config.publicCerts() << endl;
    cout << "private certs: " << config.privateCert() << endl;
    cout << "box port: " << config.boxPort() << endl;
    cout << "backend port: " << config.backendPort() << endl;

    //Load our certificate. Make sure we gor both public and private keys.
    auto server_cert = load_certificate(config.privateCert());
    assert(server_cert.first != "");
    assert(server_cert.second != "");

    cout << "server public key " << server_cert.first << endl;
    cout << "Starting broker." << endl;

    fs::path client_certs(config.publicCerts());
    assert(fs::is_directory(client_certs));

    auto ctx = zmqpp::context{};
    zmqpp::auth auth{ctx};
    auth.configure_domain("*");
    int count = 0;
    //Load all of the client public keys.
    for(auto& cert_enrty: fs::recursive_directory_iterator(config.publicCerts())){
        auto client_public_cert = load_certificate(cert_enrty.path().string()).first;
        auth.configure_curve(client_public_cert);
        count++;
        cout << ".";
    }
    cout << endl << "Loaded " << count<< " keys"<< endl;
    //Unencrypted end.
    auto front = zmqpp::socket{ ctx, zmqpp::socket_type::xpublish };
    front.bind(config.backendPort());

    //Encrypted end.
    auto back = zmqpp::socket{ ctx, zmqpp::socket_type::xsubscribe };
    back.set( zmqpp::socket_option::identity, "TRG_BROKER" );
    back.set( zmqpp::socket_option::curve_server, true );
    back.set( zmqpp::socket_option::curve_secret_key, server_cert.second );
    back.set( zmqpp::socket_option::zap_domain, "global" );
    back.bind(config.boxPort());

    cout << "Broker started..." << endl;
    zmqpp::proxy{ front, back };

    return 0;
}


auto public_re = regex{R"r(public-key\s+=\s+"(.+)")r"};
auto private_re = regex{R"r(secret-key\s+=\s+"(.+)")r"};

auto load_certificate( string const& path ) -> pair<string, string> {
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
