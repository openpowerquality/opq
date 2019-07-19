#!/usr/bin/env bash

protoc --python_out=. -I ../../protocol/ mauka.proto
protoc --python_out=. -I ../../protocol/ opqbox3.proto
