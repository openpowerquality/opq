#!/usr/bin/env bash

export MONGO_URL='mongodb://localhost:27017/opq'
export ROOT_URL='http://localhost'
export PORT=8888
export METEOR_SETTINGS=$(cat ./settings.production.json)

docker run \
    --network="host" \
    --env MONGO_URL \
    --env ROOT_URL \
    --env PORT \
    --env METEOR_SETTINGS \
    -p 8888:8888 \
    -d \
    aghalarp/opqview-test:v1