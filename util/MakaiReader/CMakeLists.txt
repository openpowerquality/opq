cmake_minimum_required(VERSION 3.0)
project(MakaiReader)

set(CMAKE_CXX_FLAGS "${CMAKE_CXX_FLAGS} -std=c++11 -g")

include_directories(${MakaiReader_SOURCE_DIR}/proto)

execute_process(
	COMMAND mkdir -p proto
	COMMAND protoc -I=../../protocol/ --cpp_out=proto/ ../../protocol//opqbox3.proto	
	WORKING_DIRECTORY ${MakaiReader_SOURCE_DIR}
)


set(SOURCE_FILES main.cpp proto/opqbox3.pb.cc)
add_executable(MakaiReader ${SOURCE_FILES})
target_link_libraries (MakaiReader protobuf)
target_link_libraries (MakaiReader zmqpp)
target_link_libraries (MakaiReader zmq)
