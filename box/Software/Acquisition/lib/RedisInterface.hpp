#ifndef REDISSCRAPER_REDISINTERFACE_HPP
#define REDISSCRAPER_REDISINTERFACE_HPP

#include <redox.hpp>
#include <vector>
#include <string>
#include <stdint.h>

class RedisInterface {
public:
    RedisInterface();
    ~RedisInterface();
    std::vector<std::string> getMeasurementsForRange(uint64_t start, uint64_t end);
private:
    redox::Redox rdx;
    std::string redis_buffer_key;
};


#endif //REDISSCRAPER_REDISINTERFACE_HPP
