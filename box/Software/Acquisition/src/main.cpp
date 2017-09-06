#include <iostream>
#include <Settings.hpp>
#include "ZmqInterface.hpp"

using namespace std;

int main(int argc, char**argv) {

    string setting_file = "/etc/opq/settings.set";
    if(argc >1) {
        setting_file = argv[1];

    }
    auto settings = opq::Settings::Instance();
    if(!settings->loadFromFile(setting_file)) {
        return 1;
    }
    zmq_loop();


}