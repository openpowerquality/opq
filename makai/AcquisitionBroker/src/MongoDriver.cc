//
// Created by tusk on 8/23/17.
//

#include "MongoDriver.h"
#include "util.h"
#include <mongocxx/instance.hpp>

using bsoncxx::builder::stream::close_array;
using bsoncxx::builder::stream::close_document;
using bsoncxx::builder::stream::document;
using bsoncxx::builder::stream::finalize;
using bsoncxx::builder::stream::open_array;
using bsoncxx::builder::stream::open_document;

static const std::string OPQ_DB = "opq";
static const std::string OPQ_EVENT_COLLECTION = "events";
static const std::string OPQ_DATA_COLLECTION = "data";
static const std::string BOX_ID_FIELD = "box_id";
static const std::string EVENT_NUMBER_FIELD = "event_number";
static const std::string EVENT_TYPE_FIELD = "type";
static const std::string DESCRIPTION_FIELD = "description";
static const std::string BOXES_TRIGGERED_FIELD = "boxes_triggered";
static const std::string BOXES_RECEIVED_FIELD = "boxes_received";
static const std::string EVENT_START_FIELD = "event_start";
static const std::string EVENT_END_FIELD = "event_end";
static const std::string TIME_STAMP_FIELD = "time_stamp";
static const std::string TIME_DATA_FIELD = "data";



MongoDriver::MongoDriver(std::string uri) : _client(mongocxx::uri(uri)){
    _db = _client[OPQ_DB];
    _event_collection = _db[OPQ_EVENT_COLLECTION];
    _data_collection = _db[OPQ_DATA_COLLECTION];
}

bool MongoDriver::init_mongo_client() {
    static mongocxx::instance instance{};
}

uint32_t MongoDriver::get_next_event_number() {
    mongocxx::options::find opts;
    opts.limit( 1 );
    opts.sort(document{} << EVENT_NUMBER_FIELD << -1 << finalize);
    auto result = _event_collection.find_one(document{}.view(), opts);
    if (!result) return 1;
    int32_t next_event_number = result->view()[EVENT_NUMBER_FIELD].get_int32() + 1;
    if(next_event_number < 0) return 1;
    else return next_event_number;
}

bool MongoDriver::create_event(opq::proto::RequestEventMessage &m, uint64_t ts, uint32_t event_num) {
    auto builder = document{};
    builder << EVENT_TYPE_FIELD << opq::proto::RequestEventMessage_TriggerType_Name(m.trigger_type())
            << EVENT_NUMBER_FIELD << (int32_t)event_num
            << DESCRIPTION_FIELD << m.description();

    auto box_array = builder << BOXES_TRIGGERED_FIELD << open_array;
    std::for_each(m.box_ids().begin(), m.box_ids().end(),
                  [&box_array](int box){box_array << box;});

    box_array << close_array;
    builder << BOXES_RECEIVED_FIELD << open_array << close_array;
    builder << EVENT_START_FIELD << (int64_t)m.start_timestamp_ms_utc()
            << EVENT_END_FIELD << (int64_t)m.end_timestamp_ms_utc();
    bsoncxx::document::value doc_value = builder << finalize;

    auto result = _event_collection.insert_one(doc_value.view());
}

bool MongoDriver::append_data_to_event(std::vector<opq::proto::DataMessage> &messages, uint32_t event_num) {
    if(messages.size() == 0)
        return false;
    int32_t id = messages.front().id();
    _event_collection.update_one(document{}
                                         << EVENT_NUMBER_FIELD << (int32_t)event_num
                                         << finalize,
                                 document{}
                                         << "$push"
                                         << open_document
                                               <<BOXES_RECEIVED_FIELD << id
                                               <<TIME_STAMP_FIELD << (int64_t)chrono_to_mili_now()
                                         << close_document
                                         << finalize);
    auto builder = bsoncxx::builder::stream::document{};
    auto start_time = messages.front().cycles().Get(0).time();
    size_t cycle_size = (size_t)messages.front().cycles().size();
    auto end_time = messages.front().cycles().Get(cycle_size -1).time();

    builder << BOX_ID_FIELD << id
            << EVENT_START_FIELD << (int64_t)start_time
            << EVENT_END_FIELD << (int64_t)end_time
	    << EVENT_NUMBER_FIELD << (int32_t)event_num;
    auto time_array_context = builder << TIME_STAMP_FIELD << bsoncxx::builder::stream::open_array;
    for (auto &message : messages){
        for(auto &cycle : message.cycles()) {
            time_array_context << (int64_t)cycle.time();
        }
    }
    time_array_context << close_array;

    auto data_array_context = builder << TIME_DATA_FIELD << bsoncxx::builder::stream::open_array;
    for (auto &message : messages){
        for(auto &cycle : message.cycles()) {
            std::for_each(cycle.data().begin(), cycle.data().end(),
            [&data_array_context](auto sample){data_array_context << sample;});
        }
    }
    data_array_context << close_array;

    bsoncxx::document::value doc_value = builder  << bsoncxx::builder::stream::finalize;
    auto result = _data_collection.insert_one(doc_value.view());
}
