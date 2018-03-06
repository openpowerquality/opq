cmake_minimum_required(VERSION 3.0)
project(health)

set(CMAKE_CXX_FLAGS "${CMAKE_CXX_FLAGS} -std=c++11 -g")

include_directories(${health_SOURCE_DIR}/proto)

execute_process(
	COMMAND mkdir -p proto
	COMMAND protoc -I=../protocol/ --cpp_out=proto/ ../protocol//opq.proto
	WORKING_DIRECTORY ${health_SOURCE_DIR}
)


set(SOURCE_FILES main.cpp proto/opq.pb.cc Statistics.cpp)
add_executable(health ${SOURCE_FILES})
target_link_libraries (health protobuf)
target_link_libraries (health zmqpp)
target_link_libraries (health zmq)
target_link_libraries (health pthread)
