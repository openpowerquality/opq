#!/bin/bash

rm a.out

g++ --std=c++11 main.cpp \
    -I/usr/local/include/mongocxx/v_noabi \
    -I/usr/local/include/libmongoc-1.0 \
    -I/usr/local/include/bsoncxx/v_noabi \
    -I/usr/local/include/libbson-1.0 \
    -L/usr/local/lib -lmongocxx -lbsoncxx
