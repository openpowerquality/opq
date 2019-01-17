#include "../lib/config.h"
#include "../lib/SynchronizedMap.hpp"
#include "../proto/opqbox3.pb.h"
#include <iostream>
#include <vector>
#include <zmqpp/zmqpp.hpp>
#include <regex>
#include <fstream>
#include <syslog.h>
#include <mongocxx/client.hpp>
#include <mongocxx/instance.hpp>
#include <thread>
#include <chrono>

using namespace std::string_literals;

/*
 * App-to-box thread callable.
 */
void app_to_box(zmqpp::context& ctx, SynchronizedMap<int, string>& map, Config config, string cert);

/*
 * Box-to-app thread callable.
 */
void box_to_app(zmqpp::context& ctx, SynchronizedMap<int, string>& map, Config config);

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

	if (config.white_list) {

		auto opq_boxes = conn["opq"]["opq_boxes"];
		auto cursor = opq_boxes.find({});

		for (auto&& doc : cursor) {
			auto public_key = doc["public_key"];
	 		auto client_public_cert = public_key? public_key.get_utf8().value.to_string() : ""s;

	    		auth.configure_curve(client_public_cert);
	    		count++;
			//std::cout << ".";
		}

		syslog(LOG_NOTICE, "%s", ("Loaded " + std::to_string(count) + " keys").c_str());
	} else {
		syslog(LOG_NOTICE, "Whitelisting Disabled");
		auth.configure_curve("CURVE_ALLOW_ANY");
	}

	SynchronizedMap<int, string> map;

	// Starts the thread that pulls from app and publishes to box
	std::thread th{app_to_box, std::ref(ctx), std::ref(map), config, server_cert.second};

	// For good measure
	th.join();

	return 0;
}

void app_to_box(zmqpp::context& ctx, SynchronizedMap<int, string>& map, Config config, string cert) {
	//std::cout << "Hello from app-to-box thread" << std::endl;

	// Initialize pull socket
	zmqpp::socket pull{ctx, zmqpp::socket_type::pull};
	pull.bind(config.backend_interface_pull);
	//pull.bind("tcp://*:4444");

	// Initialize pub socket and encrypt it
	zmqpp::socket pub{ctx, zmqpp::socket_type::publish};
	pub.set(zmqpp::socket_option::identity, "ACQ_BROKER");
	pub.set(zmqpp::socket_option::curve_server, true);
	pub.set(zmqpp::socket_option::curve_secret_key, cert);
	pub.set(zmqpp::socket_option::zap_domain, "global");
	pub.bind(config.box_interface_pub);
	//pub.bind("tcp://*4445");

	// Wait for sockets to bind
	std::this_thread::sleep_for(std::chrono::milliseconds(1000));

	while (true) {
		string msg;
		pull.receive(msg);

		// Deserialize the message upon receiving it
		opq::proto3::Command cmd;
		cmd.ParseFromString(msg);

		// Log the identity of the app
		map.insert(cmd.box_id(), cmd.identity());

		// Forward it to boxes subscribed to the box_id as topic
		zmqpp::message fwd;
		fwd.add(cmd.box_id());
		fwd.add(msg);

		pub.send(fwd);
	}
}

void box_to_app(zmqpp::context& ctx, SynchronizedMap<int, string>& map, Config config) {
	// Initialize pull socket
	zmqpp::socket pull{ctx, zmqpp::socket_type::pull};
	pull.bind(config.box_interface_pull);

	// Initialize pub socket and encrypt it
	zmqpp::socket pub{ctx, zmqpp::socket_type::publish};
	pub.bind(config.backend_interface_pub);

	// Wait for sockets to bind
	std::this_thread::sleep_for(std::chrono::milliseconds(1000));

	while (true) {
		string msg;
		pull.receive(msg);

		// Deserialize the message upon receiving it
		opq::proto3::Response res;
		res.ParseFromString(msg);

		// Find the identity of the app
		auto iterator = map.find(res.box_id());
		if (iterator == map.end()) {
			// Drop the message
			continue;
		}

		// Forward it to boxes subscribed to the identity as topic
		zmqpp::message fwd;
		fwd.add(iterator->second);
		fwd.add(msg);

		map.erase(res.box_id());

		pub.send(fwd);
	}
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
