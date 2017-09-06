#include "RedisSerializer.hpp"
#include "Settings.hpp"
#include "util.hpp"

#include <iostream>
#include <string>
#include <thread>
#include <opqdata.hpp>
#include <boost/log/trivial.hpp>

using namespace opq;
using namespace std;

RedisSerializer::RedisSerializer() {
    Settings *set = Settings::Instance();
    _boxId = set->getInt("box_id");

    std::string redisHost = set->getString("redis.host");
    uint16_t redisPort = (uint16_t)set->getInt("redis.port");
    std::string redisPass = set->getString("redis.auth");
    _redisRecordTtlS = set->getInt("redis.ttl.s");
    _redisRecordGcCnt = set->getInt("redis.gc.cnt");
    _measurements_buffer = set->getString("redis.key.measurementsbuffer");
    _trimCnt = 0;
    _ctx = NULL;
    BOOST_LOG_TRIVIAL(info) << "Connecting to redis " + redisHost + " port " + to_string(redisPort);
    while(_ctx == NULL){
        _ctx = redisConnect(redisHost.c_str(), redisPort);
        if (_ctx != NULL && _ctx->err) {
            redisFree(_ctx);
            _ctx = NULL;
        }
        if(_ctx == NULL)
            std::this_thread::sleep_for(std::chrono::milliseconds(1000));
    }
    BOOST_LOG_TRIVIAL(info) << "Connected to redis";

    redisReply* reply;
    if(redisPass != ""){
        reply = (redisReply*)redisCommand(_ctx, "AUTH %s", redisPass.c_str());
        if (reply == NULL || reply->type == REDIS_REPLY_ERROR) {
            BOOST_LOG_TRIVIAL(fatal) << "Could not authenticate with redis!";
            exit(0);
        }
        BOOST_LOG_TRIVIAL(info) << "Authenticated with redis";
        freeReplyObject(reply);
    }

    reply = (redisReply*)redisCommand(_ctx, "FLUSHALL");
    if(reply == NULL || reply->type == REDIS_REPLY_ERROR){
        BOOST_LOG_TRIVIAL(fatal) << "Could not authenticate with redis!";
        exit(0);
    }
    BOOST_LOG_TRIVIAL(info) << "Cleared Redis database";
    freeReplyObject(reply);
}

RedisSerializer::~RedisSerializer() {
    if(_ctx != NULL)
        redisFree(_ctx);
}

void RedisSerializer::sendToRedis(data::OPQMeasurementPtr measurement) {
    string message = util::serialize_to_protobuf(_boxId, measurement);
    if (measurement->timestamps.size() == 0) return;
    uint64_t ts = util::crono_to_mili(measurement->timestamps[0]);
    string score = to_string(ts);

    // Add to buffer
    redisAppendCommand(_ctx, "ZADD %s %s %b", _measurements_buffer.c_str(), score.c_str(), message.c_str(), message.length());

    // Perform GC
    uint64_t endRange;
    if(++_trimCnt == _redisRecordGcCnt) {
        endRange = ts - _redisRecordTtlS * MS_IN_S;
        redisAppendCommand(_ctx, ("ZREMRANGEBYSCORE " +  _measurements_buffer + " -inf " + std::to_string(endRange)).c_str());
        _trimCnt = 0;
    }
    redisReply* reply;
    redisGetReply(_ctx,(void**)&reply);
    if (reply == NULL || reply->type == REDIS_REPLY_ERROR) {
        BOOST_LOG_TRIVIAL(fatal) << "Lost connection with redis";
        exit(0);
    }
    freeReplyObject(reply);
}

RedisSerializer& opq::operator<<(RedisSerializer& redis, data::OPQMeasurementPtr measurement)
{
    redis.sendToRedis(measurement);
    return redis;
}
