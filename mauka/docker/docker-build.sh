#!/usr/bin/env bash

cd ../..
docker build -t mauka -f mauka/docker/Dockerfile .
