#ifndef DATA_BUFFER_HPP
#define DATA_BUFFER_HPP

#include "data_point.hpp"
#include <algorithm>
#include <functional>
#include <cassert>
#include <vector>
#include <mutex>
#include <stdexcept>
#include <boost/circular_buffer.hpp>

template<typename C, typename V, unsigned size>
class DataBuffer {
  DataBuffer(DataBuffer const&) = delete;
  auto operator=(DataBuffer const&) -> DataBuffer& = delete;

  public:
  using time_point = typename C::time_point;
  using buffer = typename boost::circular_buffer<DataPoint<C, V>>;

  class iterator {
    public:
      iterator() {
        std::lock_guard<std::mutex> lock{mtx};
        all.emplace_back(this);
      }

      iterator(iterator const& rhs) : iterator{} { it = rhs.it; }
      iterator(auto const& it) : iterator{} { this->it = it; }

      ~iterator() {
        std::lock_guard<std::mutex> lock{mtx};
        auto it = std::remove(std::begin(all), std::end(all), this);
        all.erase(it, std::end(all));
      }

      auto operator++() { return iterator{it++}; }
      auto operator++(int) { return iterator{++it}; }
      auto operator->() -> DataPoint<C, V> const * { return &(*it); }
      auto operator!=(auto const& rhs) const { return it != rhs.it; }
      auto operator==(auto const& rhs) const { return it == rhs.it; }
      auto operator<(auto const& rhs) const { return it < rhs.it; }

      static auto check(auto const& first) {
        auto it = std::min_element(std::begin(all), std::end(all));
        if (it == std::end(all))
          return true;
        else
          return first < (*it)->it;
      }

    private:
      typename buffer::const_iterator it;
      static std::vector<iterator const*> all;
  };

  DataBuffer() : data_buffer{size} {
    if (instance)
      throw std::runtime_error{"An instance of DataBuffer already exists."};
    else instance = this;
  }

  DataBuffer(DataBuffer&& rhs) : data_buffer{0} {
    *this = std::move(rhs);
  }

  auto operator=(DataBuffer&& rhs) -> DataBuffer const& {
    data_buffer = std::move(rhs.data_buffer);
    instance = this;
    return *this;
  }

  void push_back(DataPoint<C, V> dp) {
    assert( dp.time > data_buffer.back().time );
    std::lock_guard<std::mutex> lock{mtx};
    while (!iterator::check(std::begin(data_buffer)));
    data_buffer.push_back(dp);
  }

  auto get_range(time_point t0, time_point t1) const -> std::pair<iterator, iterator> {
    assert(t0 <= t1);

    auto first = std::lower_bound(std::begin(data_buffer), std::end(data_buffer), t0);
    auto last = std::lower_bound(first, std::end(data_buffer), t1);

    return { iterator{first}, iterator{last} };
  }

  auto begin() const { return iterator{std::begin(data_buffer)}; }
  auto end() const { return iterator{std::end(data_buffer)}; }

  private:
  buffer data_buffer{size};
  static std::mutex mtx;
  static DataBuffer* instance;
};

template<typename C, typename V, unsigned s>
DataBuffer<C, V, s> *DataBuffer<C, V, s>::instance = nullptr;

template<typename C, typename V, unsigned s>
std::vector<typename DataBuffer<C, V, s>::iterator const*> DataBuffer<C, V, s>::iterator::all = {};;

template<typename C, typename V, unsigned s>
std::mutex DataBuffer<C, V, s>::mtx = {};

#endif
