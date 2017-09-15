#ifndef TRIGGERING_TIMESERIES_HPP
#define TRIGGERING_TIMESERIES_HPP

#include <cstdlib>
#include <utility>
#include <list>
#include <chrono>
#include <vector>
#include <mutex>
#include "TimeSeries.hpp"
template <typename T>

class TimeSeries{
public:
    TimeSeries(size_t max_entries) {}

    void addLatest(std::chrono::time_point<std::chrono::high_resolution_clock> ts, T item){
        std::lock_guard<std::mutex> guard(_lock);
        _store.push_back(std::make_pair(ts, item));
        if(_max_entries < _store.size())
        {
            _store.pop_front();
        }
    }

    std::vector<T> getTimeRange(std::chrono::time_point<std::chrono::high_resolution_clock> start, std::chrono::time_point<std::chrono::high_resolution_clock> end){
        std::lock_guard<std::mutex> guard(_lock);
        enum SearchState{LookingForStart, LookingForEnd, Done};
        SearchState state = LookingForStart;

        std::vector<T> ret;

        for( auto itr = _store.begin(); itr != _store.end(); ++itr) {
            switch(state){
                case LookingForStart:
                    if((*itr).first >= start){
                        ret.push_back((*itr).second);
                        state = LookingForEnd;
                    }
                    break;
                case LookingForEnd:
                    if((*itr).first >= end)
                        state = Done;
                    else
                        ret.push_back((*itr).second);
                    break;
                case Done:
                    return ret;
            }
        }
    }

private:
    std::list<std::pair <std::chrono::time_point<std::chrono::high_resolution_clock> , T >> _store;
    size_t _max_entries = _max_entries;
    std::mutex _lock;
};
#endif //TRIGGERING_TIMESERIES_HPP
