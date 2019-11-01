#!/usr/bin/env bash

echo "Building mauka..."
mkdir -p build
cd ../..
rsync -av --progress mauka mauka/docker/build --exclude mauka/docker --exclude mauka/mauka_native/target
cd mauka/docker
docker build -t mauka .
rm -rf build
echo "Done building mauka."
