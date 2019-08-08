#!/usr/bin/env bash

protoc --python_out=. -I ../../protocol/ mauka.proto opqbox3.proto rustproto.proto

# Update opqbox3_pb2.py to import the rustproto_pb2 source from the correct location.
sed -i 's/import rustproto_pb2 as rustproto__pb2/import protobuf.rustproto_pb2 as rustproto__pb2/' opqbox3_pb2.py
