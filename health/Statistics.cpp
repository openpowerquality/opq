#include <iostream>
#include <fstream>
#include "Statistics.h"

Statistics::TimeInterval::TimeInterval(int64_t start, int64_t end) {
    this->start = start;
    this->end = end;
}

int64_t Statistics::TimeInterval::getStart() {
    return this->start;
}

void Statistics::TimeInterval::setStart(int64_t start) {
    this->start = start;
}

int64_t Statistics::TimeInterval::getEnd() {
    return this->end;
}

void Statistics::TimeInterval::setEnd(int64_t end) {
    this->end = end;
}

Statistics::Statistics(int id) {
    this->id = id;
    this->last = 0;
    this->uptimes = {};
    this->downtimes = {};
}

int Statistics::getId() {
    return this->id;
}

void Statistics::printUptimes() {
    for (TimeInterval t : this->uptimes) {
       std::cout << t.getStart() << " " << t.getEnd() << std::endl;
   }
}

void Statistics::addUptime(int64_t start, int64_t end) {
    if (uptimes.empty()) {
        uptimes.push_back(TimeInterval(start, end));
    } else if (uptimes.back().getEnd() == start) {
        uptimes.back().setEnd(end);
    } else {
        uptimes.push_back(TimeInterval(start, end));
    }
}

void Statistics::printDowntimes() {
    for (TimeInterval t : this->downtimes) {
        std::cout << t.getStart() << " " << t.getEnd() << std::endl;
    }
}

void Statistics::addDowntime(int64_t start, int64_t end) {
    if (downtimes.empty()) {
        downtimes.push_back(TimeInterval(start, end));
    } else if (downtimes.back().getEnd() == start) {
        downtimes.back().setEnd(end);
    } else {
        downtimes.push_back(TimeInterval(start, end));
    }
}

void Statistics::addNewTime(int64_t time) {
    if (last == 0) {
        last = time;
    } else if ((time - last) > 60000) {
        addDowntime(last, time);
    } else {
        addUptime(last, time);
    }
    last = time;
}

void Statistics::logStatistics(std::ofstream * logFile) {
    *logFile << "Device id: " << this->id << std::endl;
    //*logFile << "Uptime: " << this->uptime << std::endl;
    //*logFile << "Downtime: " << this->downtime << std::endl;
}
