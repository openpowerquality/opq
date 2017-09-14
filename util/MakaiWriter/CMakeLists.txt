cmake_minimum_required(VERSION 3.0)
project(MakaiWriter)

set(CMAKE_CXX_STANDARD 11)

include_directories(${MakaiWriter_SOURCE_DIR}/proto)

if(EXISTS ${MakaiWriter_SOURCE_DIR}/proto)
    execute_process(
            WORKING_DIRECTORY ${MakaiWriter_SOURCE_DIR}/proto
            COMMAND git pull
    )
else()
    execute_process(
        WORKING_DIRECTORY ${MakaiWriter_SOURCE_DIR}
        COMMAND git clone https://github.com/openpowerquality/opq-proto.git proto
)
endif()
execute_process(
        COMMAND protoc -I=proto/ --cpp_out=proto/ proto/opq.proto
        WORKING_DIRECTORY ${MakaiWriter_SOURCE_DIR}
)


set(SOURCE_FILES main.cpp proto/opq.pb.cc proto/opq.pb.h)
add_executable(MakaiWriter ${SOURCE_FILES})
target_link_libraries (MakaiWriter protobuf)
target_link_libraries (MakaiWriter zmqpp)
target_link_libraries (MakaiWriter zmq)
