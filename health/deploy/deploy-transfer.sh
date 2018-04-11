#!/bin/bash

set -x
timestamp=$(date +%Y%m%d_%H%M%S)
mkdir $timestamp
cp ../health.py $timestamp
cp ../config.json $timestamp
# figure out what to put into deploy file for protobuf.
cp ../protobuf/ $timestamp -r
cd ..
tar czf $timestamp.tar.gz $timestamp
rm -rf $timestamp
scp -P 29862 $timestamp.tar.gz opquser@emilia.ics.hawaii.edu:view

set +x
