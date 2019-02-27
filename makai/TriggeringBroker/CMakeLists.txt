cmake_minimum_required(VERSION 3.0)
project(TriggeringBroker)

set(CMAKE_CXX_FLAGS "${CMAKE_CXX_FLAGS} --std=c++14")

find_package(PkgConfig)
find_package(libmongocxx)
#pkg_check_modules(LIBMONGOCXX REQUIRED libmongocxx)
include_directories(${LIBMONGOCXX_INCLUDE_DIRS})
link_directories(${LIBMONGOCXX_LIBRARY_DIRS})

set(SOURCE_FILES
        src/broker.cc
        src/config.cc
        lib/config.hpp
        lib/json.hpp)

add_executable(TriggeringBroker ${SOURCE_FILES})

target_link_libraries(TriggeringBroker zmq zmqpp stdc++fs ${LIBMONGOCXX_LIBRARIES})
