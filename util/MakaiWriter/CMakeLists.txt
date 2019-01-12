cmake_minimum_required(VERSION 3.0)
project(MakaiWriter)

set(CMAKE_CXX_STANDARD 11)

include_directories(${MakaiWriter_SOURCE_DIR}/proto)

execute_process(
	COMMAND mkdir -p proto
        COMMAND protoc -I=../../protocol/ --cpp_out=proto/ ../../protocol//opqbox3.proto
        WORKING_DIRECTORY ${MakaiWriter_SOURCE_DIR}
)


set(SOURCE_FILES main.cpp proto/opqbox3.pb.cc proto/opqbox3.pb.h)
add_executable(MakaiWriter ${SOURCE_FILES})
target_link_libraries (MakaiWriter protobuf)
target_link_libraries (MakaiWriter zmqpp)
target_link_libraries (MakaiWriter zmq)
