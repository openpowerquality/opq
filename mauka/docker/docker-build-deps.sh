#!/usr/bin/env bash

cd ../..
docker build --rm -t mauka-deps -f mauka/docker/mauka-deps/Dockerfile .
