cmake_minimum_required(VERSION 3.0)
project(Acquisition)
include_directories(${Acquisition_SOURCE_DIR}/lib)
include_directories(${Acquisition_SOURCE_DIR}/proto)

set(CMAKE_CXX_FLAGS "${CMAKE_CXX_FLAGS} -std=c++14 -DBOOST_LOG_DYN_LINK")

set(SOURCE_FILES
        src/main.cpp
        src/Settings.cpp
        src/RedisInterface.cpp
        lib/RedisInterface.hpp
        src/ZmqInterface.cpp
        lib/ZmqInterface.hpp
        lib/Settings.hpp
        proto/opq.pb.cc
        proto/opq.pb.h)
add_executable(Acquisition ${SOURCE_FILES})

TARGET_LINK_LIBRARIES(Acquisition protobuf redox hiredis ev pthread boost_log zmqpp zmq rt dl)
