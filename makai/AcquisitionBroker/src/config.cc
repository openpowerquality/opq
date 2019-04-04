#include "config.h"
#include "json.hpp"
#include <iostream>
#include <fstream>
#include <stdexcept>

using json = nlohmann::json;

Config::Config(string var_name) {
    auto contents = std::getenv(var_name.c_str());

    if (contents == nullptr) {
        throw std::runtime_error("Could not open settings from environment.");
    }

    try {
        auto j = json::parse(contents);
        public_certs = j["client_certs"].get<string>();
        private_cert = j["server_cert"].get<string>();
        box_interface_pub = j["box_pub"].get<string>();
        box_interface_pull = j["box_pull"].get<string>();
        backend_interface_pull = j["backend_pull"].get<string>();
        backend_interface_pub = j["backend_pub"].get<string>();
        mongo_uri = j["mongo_uri"].get<string>();
	white_list = j["white_list"].get<bool>();
    }
    catch(const std::domain_error& e){
        throw std::runtime_error("Malformed config file");
    }
    catch (const std::invalid_argument& e){
        throw std::runtime_error("Malformed config file");
    }
}
