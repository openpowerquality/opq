#ifndef ACQUISITIONBROKER_MONGODRIVER_H
#define ACQUISITIONBROKER_MONGODRIVER_H

#include <iostream>
#include <cstdint>
#include <iostream>
#include <vector>
#include <mongocxx/database.hpp>
#include <mongocxx/client.hpp>
#include "opq.pb.h"

class MongoDriver{
public:
    MongoDriver(std::string uri = "mongodb://emilia.ics.hawaii.edu:27017");
    static bool init_mongo_client();
    bool create_event(opq::proto::RequestEventMessage &m, uint64_t ts, uint32_t event_num);
    bool append_data_to_event(std::vector<opq::proto::DataMessage> &m, uint32_t event_num);
    uint32_t get_next_event_number();
private:
    mongocxx::database _db;
    mongocxx::client _client;
    mongocxx::collection _event_collection;
    mongocxx::collection _data_collection;

};


#endif //ACQUISITIONBROKER_MONGODRIVER_H
