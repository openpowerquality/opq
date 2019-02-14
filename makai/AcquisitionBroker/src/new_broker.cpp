#include "../lib/config.h"
#include "../lib/SynchronizedMap.hpp"
#include "../proto/opqbox3.pb.h"
#include "../lib/util.h"
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
void box_to_app(zmqpp::context& ctx, SynchronizedMap<int, string>& map, Config config, string cert);

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
	std::thread th1{app_to_box, std::ref(ctx), std::ref(map), config, server_cert.second};
  std::thread th2{box_to_app, std::ref(ctx), std::ref(map), config, server_cert.second};
	// For good measure
	th1.join();
	th2.join();
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

	// Wait for sockets to bind
	std::this_thread::sleep_for(std::chrono::milliseconds(1000));

    uint32_t sequence = 0;

	while (true) {
		string msg;
		pull.receive(msg);

		// Deserialize the message upon receiving it
		opq::opqbox3::Command cmd;
		cmd.ParseFromString(msg);
        cmd.set_seq(sequence);
		// Log the identity of the app
		map.insert(sequence, cmd.identity());
        sequence++;
		// Forward it to boxes subscribed to the box_id as topic
		zmqpp::message fwd;
		fwd.add(cmd.box_id());
		fwd.add(cmd.SerializeAsString());
		pub.send(fwd);
	}
}

void box_to_app(zmqpp::context& ctx, SynchronizedMap<int, string>& map, Config config, string cert) {
	// Initialize pull socket
	zmqpp::socket pull{ctx, zmqpp::socket_type::pull};
    pull.set(zmqpp::socket_option::identity, "ACQ_BROKER");
    pull.set(zmqpp::socket_option::curve_server, true);
    pull.set(zmqpp::socket_option::curve_secret_key, cert);
    pull.set(zmqpp::socket_option::zap_domain, "global");
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
		opq::opqbox3::Response res;
		res.ParseFromString(msg);

		// Find the identity of the app
		auto iterator = map.find(res.seq());
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
