#include "../lib/config.h"
#include <iostream>
#include <vector>
#include <zmqpp/zmqpp.hpp>
#include <regex>
#include <fstream>
#include <syslog.h>
#include <mongocxx/client.hpp>
#include <mongocxx/instance.hpp>
#include <thread>

using namespace std::string_literals;

/*
 * App-to-box thread callable.
 */
void app_to_box(zmqpp::context& ctx);

/*
 * Loads a certificate from a file as a pair of strings.
 */
auto load_certificate(string const& path) -> std::pair<string, string>;

int main (int argc, char **argv) {
	auto config = argc == 1 ? Config{} : Config{ argv[1] };

	//Load our certificate. Make sure we get both public and private keys.
	auto server_cert = load_certificate(config.private_cert);
	if(server_cert.first == "" || server_cert.second != ""){
	    syslog(LOG_ERR, "Could not load Certificates");
	}

	syslog(LOG_NOTICE, "%s", ("server public key " +  server_cert.first).c_str());

	auto ctx = zmqpp::context{};
	zmqpp::auth auth{ctx};
	auth.configure_domain("*");

	//Load all of the client public keys.
	int count = 0;
	mongocxx::instance inst{};
	mongocxx::client conn{mongocxx::uri{}};

	auto opq_boxes = conn["opq"]["opq_boxes"];
	auto cursor = opq_boxes.find({});

	for (auto&& doc : cursor) {
	    auto public_key = doc["public_key"];
	    auto client_public_cert = public_key? public_key.get_utf8().value.to_string() : ""s;

	    auth.configure_curve(client_public_cert);
	    count++;
	    std::cout << ".";
	}

	syslog(LOG_NOTICE, "%s", ("Loaded " + std::to_string(count) + " keys").c_str());

	std::thread th(app_to_box, std::ref(ctx));
	th.join();
	/*
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
	*/

	return 0;
}

void app_to_box(zmqpp::context& ctx) {
	std::cout << "Hello from app-to-box thread" << std::endl;
}

auto load_certificate( string const& path ) -> std::pair<string, string> {
	auto file = std::ifstream{ path };
	assert(file);

	auto ss = std::stringstream{};
	ss << file.rdbuf();
	auto contents = ss.str();

	auto public_sm = std::smatch{}, private_sm = std::smatch{};

	auto public_re = std::regex{R"r(public-key\s+=\s+"(.+)")r"};
	auto private_re = std::regex{R"r(secret-key\s+=\s+"(.+)")r"};

	auto has_public = std::regex_search(contents, public_sm, public_re);
	auto has_private = std::regex_search(contents, private_sm, private_re);

	return {has_public ? public_sm[1] : ""s,
		has_private ? private_sm[1] : ""s};
}
