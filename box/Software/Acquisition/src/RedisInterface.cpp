
#include "RedisInterface.hpp"
#include "Settings.hpp"

using redox::Redox;
using redox::Command;
using namespace std;

RedisInterface::RedisInterface() {
    auto settings = opq::Settings::Instance();
    auto redisPass = settings->getString("redis.auth");
    auto redis_host = settings->getString("redis.host");
    int redis_port = settings->getInt("redis.port");
    if(!rdx.connect(redis_host, redis_port)) {
        throw runtime_error("Could not connect to Redis");
    }
    if(redisPass != "") {
        auto &c = rdx.commandSync<string>({"AUTH", redisPass});
        if (!c.ok()) {
            throw runtime_error("Could not connect to Redis");
        }
        c.free();
    }
    redis_buffer_key = settings->getString("redis.key.measurementsbuffer");
}

RedisInterface::~RedisInterface() {
    rdx.disconnect();
}

std::vector<std::string> RedisInterface::getMeasurementsForRange(uint64_t start, uint64_t end) {
    vector<string> out;
    auto& c = rdx.commandSync <vector <string> > ({"ZRANGEBYSCORE",redis_buffer_key, to_string(start), to_string(end)});
    if (c.ok()){
        out =  c.reply();
        //cout << start << " " << end << " " <<  out.size() << endl;
    }
    else{
        cout << "Redis call failed" << endl;
    }
    c.free();
    return out;
}