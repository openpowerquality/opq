#ifndef ACQUISITION_REDISSERIALIZER_HPP
#define ACQUISITION_REDISSERIALIZER_HPP
#include <iostream>
#include <string>
#include "opqdata.hpp"

#include <hiredis/hiredis.h>

namespace opq {
    /**
     * @brief This class represents a connector to the local redis database.
     * On creation this object will try to connect to the local redis server in order to use it as a hot transfer.
     * All of the settings are loaded via Settings object. Redis database will be cleared upon connection!
     */
    class RedisSerializer {
    public:
        /**
         * @brief Create a new redis connector. All redis data will be cleared!
         * @return
         */
        RedisSerializer();

        /**
         * @brief Closes the redis connectrion.
         */
        ~RedisSerializer();

        ///Serialize and send a measurement to redis.
        void sendToRedis(data::OPQMeasurementPtr measurement);
    private:
        const int MS_IN_S = 1000;
        redisContext* _ctx;
        int _boxId;
        std::string _measurements_buffer;
        int64_t _redisRecordTtlS;
        int32_t _redisRecordGcCnt;
        int32_t _trimCnt;
    };
    ///Overload the shift right operator for convenience.
    RedisSerializer& operator<<(RedisSerializer& redis, data::OPQMeasurementPtr measurement);
};
#endif //ACQUISITION_REDISSERIALIZER_HPP
