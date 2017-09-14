cmake_minimum_required(VERSION 3.0)
project(MakaiReader)

set(CMAKE_CXX_FLAGS "${CMAKE_CXX_FLAGS} -std=c++11 -g")

include_directories(${MakaiReader_SOURCE_DIR}/proto)

if(EXISTS ${MakaiReader_SOURCE_DIR}/proto)
    execute_process(
            WORKING_DIRECTORY ${MakaiReader_SOURCE_DIR}/proto
            COMMAND git pull
    )
else()
    execute_process(
        WORKING_DIRECTORY ${MakaiReader_SOURCE_DIR}
        COMMAND git clone https://github.com/openpowerquality/opq-proto.git proto
)
endif()
execute_process(
        COMMAND protoc -I=proto/ --cpp_out=proto/ proto/opq.proto
        WORKING_DIRECTORY ${MakaiReader_SOURCE_DIR}
)


set(SOURCE_FILES main.cpp proto/opq.pb.cc)
add_executable(MakaiReader ${SOURCE_FILES})
target_link_libraries (MakaiReader protobuf)
target_link_libraries (MakaiReader zmqpp)
target_link_libraries (MakaiReader zmq)
