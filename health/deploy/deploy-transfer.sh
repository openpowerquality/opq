#!/bin/bash

set -x
timestamp=$(date +%Y%m%d_%H%M%S)
mkdir $timestamp
cp deploy-run.sh $timestamp
cp ../health.py $timestamp
cp ../config.json $timestamp
cp ../protobuf/ $timestamp -r
tar czf $timestamp.tar.gz $timestamp
rm -rf $timestamp
scp -P 29862 $timestamp.tar.gz opquser@emilia.ics.hawaii.edu:health

set +x
