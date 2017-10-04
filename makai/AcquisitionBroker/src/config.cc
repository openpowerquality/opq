#include "config.h"
#include "json.hpp"
#include <iostream>
#include <fstream>
#include <stdexcept>

using std::ifstream;
using json = nlohmann::json;

Config::Config(string fname) {
    ifstream input;
    try {
        //open the json file.
        input.open(fname);
    }
    catch (std::ios_base::failure& e) {
        throw std::runtime_error("Could not open the file");
    }
    json j;
    try {
        input >> j;
        public_certs = j["client_certs"].get<string>();
        private_cert = j["server_cert"].get<string>();
        box_interface_pub = j["box_pub"].get<string>();
        box_interface_pull = j["box_pull"].get<string>();
        backend_interface_rep = j["backend_rep"].get<string>();
        backend_interface_pub = j["backend_pub"].get<string>();
        mongo_uri = j["mongo_uri"].get<string>();
    }
    catch(const std::domain_error& e){
        throw std::runtime_error("Malformed config file");
    }
    catch (const std::invalid_argument& e){
        throw std::runtime_error("Malformed config file");
    }
}
