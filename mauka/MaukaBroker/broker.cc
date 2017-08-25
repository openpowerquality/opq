#include "config.hpp"

#include <iostream>
#include <memory>
#include <vector>
#include <string>
#define _GLIBCXX_USE_CXX17_ABI 0
#include "zmqpp/zmqpp.hpp"
#include "zmqpp/proxy.hpp"

using namespace std::string_literals;
using std::string;
using std::pair;

int main (int argc, char **argv) {
    std::cout << "Parsing config." << std::endl;

    auto config = argc == 1 ? Config{} : Config{ argv[1] };

    std::cout << "box port: " << config.boxPort() << '\n';
    std::cout << "backend port: " << config.backendPort() << std::endl;

    auto ctx = zmqpp::context{};

    auto front = zmqpp::socket{ ctx, zmqpp::socket_type::xpublish };
    front.bind(config.backendPort());
    assert(front);

    auto back = zmqpp::socket{ ctx, zmqpp::socket_type::xsubscribe };
    back.bind(config.boxPort());
    assert(back);

    std::cout << "Broker started..." << std::endl;
    zmqpp::proxy{ front, back };

    return 0;
}
