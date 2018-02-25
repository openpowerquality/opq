#include <iostream>
#include "Statistics.h"

Statistics::Statistics(int id) {
    this->id = id;
    this->uptime = 0;
    this->downtime = 0;
}

int Statistics::getId() {
    return this->id;
}

int Statistics::getUptime() {
    return this->uptime;
}

void Statistics::setUptime(int64_t uptime) {
    this->uptime = uptime;
}

int Statistics::getDowntime() {
    return this->downtime;
}

void Statistics::setDowntime(int64_t donwtime) {
    this->downtime = downtime;
}

void Statistics::printStatistics() {
    std::cout << "Device id: " << this->id << std::endl;
    std::cout << "Uptime: " << this->uptime << std::endl;
    std::cout << "Downtime: " << this->downtime << std::endl;
}
