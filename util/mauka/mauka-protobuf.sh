#!/usr/bin/env bash

set -o xtrace

BASE_DIR=../..
INPUT_DIR=${BASE_DIR}/protocol
OUTPUT_DIR=${BASE_DIR}/mauka/protobuf

# Compile the latest
protoc -I=${INPUT_DIR} --python_out=${OUTPUT_DIR} ${INPUT_DIR}/opq.proto
protoc -I=${INPUT_DIR} --python_out=${OUTPUT_DIR} ${INPUT_DIR}/mauka.proto

# Copy the latest for reference
cp ${INPUT_DIR}/mauka.proto ${OUTPUT_DIR}/.

set +o xtrace
