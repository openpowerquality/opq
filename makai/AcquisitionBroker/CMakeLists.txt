cmake_minimum_required(VERSION 3.0)
project(AcquisitionBroker)

set(CMAKE_CXX_FLAGS "${CMAKE_CXX_FLAGS} -std=c++14")
include_directories(${AcquisitionBroker_SOURCE_DIR}/proto)
include_directories(${AcquisitionBroker_SOURCE_DIR}/lib)

execute_process(
        COMMAND mkdir -p proto
	COMMAND	protoc -I=../../protocol/ --cpp_out=proto/ ../../protocol//opq.proto
	COMMAND	protoc -I=../../protocol/ --cpp_out=proto/ ../../protocol//opqbox3.proto
        WORKING_DIRECTORY ${AcquisitionBroker_SOURCE_DIR}
)

find_package(PkgConfig)
pkg_check_modules(LIBBSONXX REQUIRED libbsoncxx)
pkg_check_modules(LIBMONGOCXX REQUIRED libmongocxx)
include_directories(${LIBMONGOCXX_INCLUDE_DIRS} ${LIBBSONCXX_INCLUDE_DIRS})
link_directories(${LIBMONGOCXX_LIBRARY_DIRS} ${LIBBSONCXX_LIBRARY_DIRS})

set(SOURCE_FILES
        src/new_broker.cpp
        src/config.cc
        lib/config.h
        lib/json.hpp
        src/DataHandler.cc
        lib/DataHandler.h
        proto/opq.pb.cc
        proto/opq.pb.h
	proto/opqbox3.pb.cc
	proto/opqbox3.pb.h
        lib/util.h
        src/RequestHandler.cc
        lib/RequestHandler.h src/MongoDriver.cc lib/MongoDriver.h
	lib/SynchronizedMap.hpp)

add_executable(AcquisitionBroker ${SOURCE_FILES})

target_link_libraries(AcquisitionBroker zmq zmqpp stdc++fs protobuf pthread 
        ${LIBMONGOCXX_LIBRARIES} ${LIBBSONCXX_LIBRARIES})
