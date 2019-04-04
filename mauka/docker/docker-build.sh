#!/usr/bin/env bash

echo "Building mauka..."
mkdir -p build
cd ../..
rsync -av --progress mauka mauka/docker/build --exclude mauka/docker
cd mauka/docker
docker build -t mauka .
rm -rf build
echo "Done building mauka."