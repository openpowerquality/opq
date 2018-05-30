#include "MongoDriver.h"
#include <syslog.h>

#include "util.h"
#include "config.h"
#include <mongocxx/instance.hpp>
#include <mongocxx/exception/write_exception.hpp>
#include <mongocxx/exception/query_exception.hpp>
#include <bsoncxx/builder/stream/document.hpp>
#include <bsoncxx/document/element.hpp>
#include <bsoncxx/json.hpp>

using bsoncxx::builder::stream::close_array;
using bsoncxx::builder::stream::close_document;
using bsoncxx::builder::stream::document;
using bsoncxx::builder::stream::finalize;
using bsoncxx::builder::stream::open_array;
using bsoncxx::builder::stream::open_document;


static const std::string OPQ_DB = "opq";
static const std::string EVENT_COLLECTION = "events";
static const std::string BOX_EVENT_COLLECTION = "box_events";
static const std::string OPQ_BOX_COLLECTION = "opq_boxes";

static const std::string BOX_ID_FIELD = "box_id";
static const std::string EVENT_NUMBER_FIELD = "event_id";
static const std::string EVENT_TYPE_FIELD = "type";
static const std::string EVENT_DESCRIPTION_FIELD = "description";
static const std::string EVENT_BOXES_TRIGGERED_FIELD = "boxes_triggered";
static const std::string EVENT_BOXES_RECEIVED_FIELD = "boxes_received";
static const std::string EVENT_START_FIELD = "target_event_start_timestamp_ms";
static const std::string EVENT_END_FIELD = "target_event_end_timestamp_ms";
static const std::string EVENT_TIME_STAMP_FIELD = "latencies_ms";

static const std::string BOX_EVENT_START_FIELD = "event_start_timestamp_ms";
static const std::string BOX_EVENT_END_FIELD = "event_end_timestamp_ms";
static const std::string BOX_EVENT_WINDOW_TIME_STAMP_FIELD = "window_timestamps_ms";
static const std::string BOX_EVENT_TIME_DATA_FIELD = "data_fs_filename";
static const std::string BOX_EVENT_LOCATION_FIELD = "location";

static const std::string OPQ_BOX_LOCATION_FIELD = "location";




static const std::string GRIDFS_COLLECTION = "fs.files";
static const std::string GRIDFS_COLLECTION_FILENAME_FIELD = "filename";
static const std::string GRIDFS_COLLECTION_METADATA_FIELD = "metadata";
static const std::string GRIDFS_COLLECTION_METADATA_EVENT_ID_FIELD = "event_id";
static const std::string GRIDFS_COLLECTION_METADATA_BOX_ID_FIELD = "box_id";




MongoDriver::MongoDriver(std::string uri) : _client(mongocxx::uri(uri)){
    _db = _client[OPQ_DB];
    _event_collection = _db[EVENT_COLLECTION];
    _data_collection = _db[BOX_EVENT_COLLECTION];
    _box_collection = _db[OPQ_BOX_COLLECTION];
    _gridfs_collection = _db[GRIDFS_COLLECTION];
    _bucket = _db.gridfs_bucket();
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
    bsoncxx::document::element element= result->view()[EVENT_NUMBER_FIELD];
    if (!element) return 1;
    int32_t next_event_number = element.get_int32() + 1;
    if(next_event_number < 0) return 1;
    return next_event_number;

}

bool MongoDriver::create_event(opq::proto::RequestEventMessage &m, uint64_t ts, uint32_t event_num) {
    auto builder = document{};
    builder << EVENT_TYPE_FIELD << opq::proto::RequestEventMessage_TriggerType_Name(m.trigger_type())
            << EVENT_NUMBER_FIELD << (int32_t)event_num
            << EVENT_DESCRIPTION_FIELD << m.description();

    auto box_array = builder << EVENT_BOXES_TRIGGERED_FIELD << open_array;
    std::for_each(m.box_ids().begin(), m.box_ids().end(),
                  [&box_array](int box){box_array << std::to_string(box);});

    box_array << close_array;
    builder << EVENT_BOXES_RECEIVED_FIELD << open_array << close_array;
    builder << EVENT_TIME_STAMP_FIELD << open_array << close_array;
    builder << EVENT_START_FIELD << (int64_t)m.start_timestamp_ms_utc()
            << EVENT_END_FIELD << (int64_t)m.end_timestamp_ms_utc();
    bsoncxx::document::value doc_value = builder << finalize;
    try {
        auto result = _event_collection.insert_one(doc_value.view());
    }
    catch(const mongocxx::write_exception &e){
        syslog(LOG_WARNING, "%s", ("Could not create an event: " + std::string(e.what())).c_str() );
    }
}

bool MongoDriver::append_data_to_event(std::vector<opq::proto::DataMessage> &messages, uint32_t event_num) {
    if (messages.size() == 0)
        return false;
    int32_t id = messages.front().id();

    try {
        _event_collection.update_one(document{}
                                             << EVENT_NUMBER_FIELD << (int32_t) event_num
                                             << finalize,
                                     document{}
                                             << "$push"
                                             << open_document
                                             << EVENT_BOXES_RECEIVED_FIELD << std::to_string(id)
                                             << EVENT_TIME_STAMP_FIELD << (int64_t) chrono_to_mili_now()
                                             << close_document
                                             << finalize);
    }
    catch (const mongocxx::write_exception &e) {
        syslog(LOG_WARNING, "%s", ("Could not create an event: " + std::string(e.what())).c_str() );
    }

    string data_file = "event_" + std::to_string(event_num) + "_" + std::to_string(id);

    auto builder = bsoncxx::builder::stream::document{};
    auto start_time = messages.front().cycles().Get(0).time();
    auto cycle_size = (size_t) messages.back().cycles().size();
    auto end_time = messages.back().cycles().Get(cycle_size - 1).time() + 1000.0/BOX_SAMPLING_RATE*messages.back().cycles().Get(cycle_size - 1).data().size();
    builder << BOX_ID_FIELD << std::to_string(id)
            << BOX_EVENT_START_FIELD << (int64_t) start_time
            << BOX_EVENT_END_FIELD << (int64_t) end_time
            << EVENT_NUMBER_FIELD << (int32_t) event_num;
    auto time_array_context = builder << BOX_EVENT_WINDOW_TIME_STAMP_FIELD << bsoncxx::builder::stream::open_array;
    for (auto &message : messages) {
        for (auto &cycle : message.cycles()) {
            time_array_context << (int64_t) cycle.time();
        }
    }
    time_array_context << close_array;
    builder << BOX_EVENT_TIME_DATA_FIELD << data_file;

    //Fill in location.
    try {
        mongocxx::options::find opts{};
        auto location = _box_collection.find_one(document{} << BOX_ID_FIELD << std::to_string(id) << finalize);
        using namespace std;
        if(location){
            auto element = (*location).view()[OPQ_BOX_LOCATION_FIELD];
            if(element){
                builder << BOX_EVENT_LOCATION_FIELD << element.get_utf8();
            }
        }
    }
    catch (const mongocxx::query_exception &e) {
        syslog(LOG_WARNING, "%s", ("Could not find location: " + std::string(e.what())).c_str() );
    }

    bsoncxx::document::value doc_value = builder << finalize;

    try {
        auto result = _data_collection.insert_one(doc_value.view());
    }
    catch (const mongocxx::write_exception &e) {
        syslog(LOG_WARNING, "%s", ("Could not create an event: " + std::string(e.what())).c_str() );
    }

    auto uploader = _bucket.open_upload_stream(data_file);

    std::vector<uint8_t> file_data;
    for (auto &message : messages) {
        for (auto &cycle : message.cycles()) {
            std::for_each(cycle.data().begin(), cycle.data().end(),
                          [&file_data](auto sample) {
                              file_data.push_back(sample & 0xFF);
                              file_data.push_back(sample >> 8);
                          }
            );
        }
    }
    uploader.write(file_data.data(), file_data.size());
    auto result = uploader.close();

    auto update_doc = document{} << "$set"
                                         << open_document << GRIDFS_COLLECTION_METADATA_FIELD
                                                          << open_document << GRIDFS_COLLECTION_METADATA_EVENT_ID_FIELD << (int)event_num
                                                                           << GRIDFS_COLLECTION_METADATA_BOX_ID_FIELD << std::to_string(id)
                                                          << close_document
                                         << close_document
                    << finalize;


    _gridfs_collection.update_one(document{} <<GRIDFS_COLLECTION_FILENAME_FIELD << data_file << finalize, update_doc.view());

}
