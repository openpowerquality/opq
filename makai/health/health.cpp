#include <zmqpp/zmqpp.hpp>
#include <string>
#include <iostream>
#include <thread>
#include <chrono>
#include <unordered_set>
#include "mongoose.h"
#include "opqbox3.pb.h"
#include "json.hpp"

using namespace std::string_literals;

/*
 * Event handler used by http_server
 */
void ev_handler(struct mg_connection, int);

/*
 * Thread callable that handles HTTP requests
 */
void http_server(int port);

/*
 * Thread callable that monitors OPQBoxes from the TriggeringBroker
 */
void box_monitor(); 

inline uint64_t chrono_to_mili(std::chrono::time_point<std::chrono::high_resolution_clock> time) {
	std::chrono::time_point<std::chrono::high_resolution_clock> epoch;
	auto elapsed = time - epoch;
	return std::chrono::duration_cast<std::chrono::milliseconds>(elapsed).count();
}

inline uint64_t chrono_to_mili_now() {
	return chrono_to_mili(std::chrono::high_resolution_clock::now());
}

std::unordered_set<int> set;

int main (int argc, char **argv) {

	// Starts the thread that listens to HTTP requests
	std::thread th_http_server{http_server, 8000};

	// Starts the thread that monitors OPQ boxes
	std::thread th_box_monitor{box_monitor};

	// For good measure
	th_http_server.join();
	th_box_monitor.join();

	return 0;
}

void ev_handler(struct mg_connection *c, int ev, void *p) {

	if (ev == MG_EV_HTTP_REQUEST) {

		// Initialize push and sub socket
		zmqpp::context ctx;
		zmqpp::socket push{ctx, zmqpp::socket_type::push};
		zmqpp::socket sub{ctx, zmqpp::socket_type::subscribe};

		// TODO Get these interfaces from config
		push.bind("tcp:://*:9884");
		sub.bind("tcp://*:9899");

		// Array with all the box info
		nlohmann::json r = nlohmann::json::array();

		for (auto it = set.begin(); it != set.end(); ++it) {

			// Build Command and send it to the AcquisitionBroker
			opq::proto3::GetInfoCommand gic;
			opq::proto3::Command cmd;

			cmd.set_box_id(*it);
			cmd.set_identity("health");
			cmd.set_timestamp_ms(chrono_to_mili_now());
			cmd.set_allocated_info_command(&gic);

			std::string out;
			cmd.SerializeToString(&out);
			push.send(out);

			// Listen for response
			std::string in;
			sub.receive(in);
			
			// Deserialize message--should be Response
			opq::proto3::Response res;
			res.ParseFromString(in);

			// Build JSON (what we want to send)
			nlohmann::json j;
			j["box_id"] = res.box_id();
			j["seq"] = res.seq();
			j["timestamp_ms"] = res.timestamp_ms();

			// Do we have more info?
			if (res.has_info_response()) {
				opq::proto3::GetInfoResponse gir = res.info_response();
				j["mac_addr"] = gir.mac_addr();
				j["wifi_network"] = gir.wifi_network();
				j["ip"] = gir.ip();
				j["uptime"] = gir.uptime();
				j["calibration_constant"] = gir.calibration_constant();
				j["pub_key"] = gir.pub_key();
				j["measurement_rate"] = gir.measurement_rate();
			}

			r.push_back(j);
		}


		// Respond to HTTP request
		struct http_message *hm = (struct http_message *) p;

		mg_send_head(c, 200, hm->message.len, "Content-Type: text/plain");
		mg_printf(c, "%s", r.dump());
	}	
}

void http_server(int port) {
	struct mg_mgr mgr;
	struct mg_connection *c;
	
	mg_mgr_init(&mgr, NULL);

	// TODO Use the param port
	c = mg_bind(&mgr, "8000", ev_handler);
	if (c == NULL) {
		std::cout << "Could not connect to port " << "8000"  << std::endl;
		return;
	}
	mg_set_protocol_http_websocket(c);

	while (true) {
		mg_mgr_poll(&mgr, 1000);
	}
	mg_mgr_free(&mgr);
}


void box_monitor() {

	// Initialize sub socket
	zmqpp::context ctx;
	zmqpp::socket sub{ctx, zmqpp::socket_type::subscribe};

	// TODO Get the port from config
	sub.bind("tcp://*:9881");

	// Wait for socket to bind
	std::this_thread::sleep_for(std::chrono::milliseconds(1000));

	while (true) {
		zmqpp::message msg;
		sub.receive(msg);
		
		uint32_t box_id;
		msg.get(box_id, 0);

		set.insert(box_id);
	}

	// TODO Get the port from config
	sub.disconnect("tcp://*:9881");
}
