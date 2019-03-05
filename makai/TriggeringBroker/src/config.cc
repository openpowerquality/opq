#include "../lib/config.hpp"
#include "../lib/json.hpp"
#include <iostream>
#include <fstream>
#include <stdexcept>

using json = nlohmann::json;

Config::Config(string var_name) {
    auto contents = std::getenv(var_name.c_str());
    if (contents == nullptr) {
        throw std::runtime_error("Could not open the settings from the environment.");
    }
    try {
        auto j = json::parse(contents);
        _public_certs = j["client_certs"].get<string>();
        _private_cert = j["server_cert"].get<string>();
        _box_interface = j["interface"].get<string>();
        _backend_interface = j["backend"].get<string>();
        _white_list = j["white_list"].get<bool>();
    }
    catch(const std::domain_error& e){
        throw std::runtime_error("Malformed config file");
    }
    catch (const std::invalid_argument& e){
        throw std::runtime_error("Malformed config file");
    }
}
