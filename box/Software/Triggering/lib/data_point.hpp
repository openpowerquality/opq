#ifndef DATA_POINT_HPP
#define DATA_POINT_HPP

template<typename C, typename V>
struct DataPoint {
  DataPoint(auto t, auto v) : time{t}, value{v} {}
  DataPoint(auto t) : time {t} {}

  auto operator<(DataPoint const& rhs) const -> bool {
    return time < rhs.time;
  }

  typename C::time_point time;
  V value;
};

#endif
