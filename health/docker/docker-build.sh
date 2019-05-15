#!/usr/bin/env bash

echo "Building health..."
mkdir -p build/health
cp -r ../src build/health
cp ../Cargo.toml build/health
cp run-health.sh build/health
docker build -t healthv2 .
rm -rf build
echo "Done building health."
