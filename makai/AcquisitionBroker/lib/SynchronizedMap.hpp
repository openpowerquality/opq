#ifndef SYNCHRONIZED_MAP_H
#define SYNCHRONIZED_MAP_H

#include <mutex>
#include <unordered_map>

template <class T, class U>
class SynchronizedMap {
	public:
		SynchronizedMap() {};
		auto insert(T key, U value) {
			std::lock_guard<std::mutex> lock(_mtx);
			std::pair<T, U> pair(key, value);
			return _map.insert(pair);
		};
		auto erase(T key) {
			std::lock_guard<std::mutex> lock(_mtx);
			return _map.erase(key);
		};
		auto find(T key) {
			std::lock_guard<std::mutex> lock(_mtx);
			return _map.find(key);
		};
		auto end() {
			std::lock_guard<std::mutex> lock(_mtx);
			return _map.end();
		};
	private:
		std::mutex _mtx;
		std::unordered_map<T, U> _map;

};

#endif
