#ifndef ACQUISITIONBROKER_UTIL_H
#define ACQUISITIONBROKER_UTIL_H

#include <regex>
#include <fstream>
#include <iostream>
#include <chrono>
#include <cassert>
#include <exception>

using std::string;
using std::regex;
using std::regex_match;
using std::runtime_error;
using namespace std::string_literals;

//Topic for the box data request
static const string BOX_EVENT_GET_TOPIC = "evget";

//Load zmq elliptic curve certificate as a pair.
inline auto load_certificate( string const& path ) -> std::pair<string, string> {
    auto public_re = regex{R"r(public-key\s+=\s+"(.+)")r"};
    auto private_re = regex{R"r(secret-key\s+=\s+"(.+)")r"};
    auto file = std::ifstream{ path };
    if (!file.is_open()){
        throw runtime_error("could not load certificate form " + path);
    }
    auto ss = std::stringstream();
    ss << file.rdbuf();
    auto contents = ss.str();

    auto public_sm = std::smatch{}, private_sm = std::smatch{};

    auto has_public = regex_search(contents, public_sm, public_re);
    auto has_private = regex_search(contents, private_sm, private_re);

    return {has_public ? public_sm[1] : ""s,
            has_private ? private_sm[1] : ""s};
}

//Converts a std::chrono ts to microseconds since epoch.
inline uint64_t chrono_to_mili(std::chrono::time_point<std::chrono::high_resolution_clock> time) {
    std::chrono::time_point<std::chrono::high_resolution_clock > epoch;
    auto elapsed = time - epoch;
    return std::chrono::duration_cast<std::chrono::milliseconds>(elapsed).count();
}

//Get the current time in microseconds since epoch.
inline uint64_t chrono_to_mili_now(){
    return chrono_to_mili(std::chrono::high_resolution_clock::now());
}


#endif //ACQUISITIONBROKER_UTIL_H_H
