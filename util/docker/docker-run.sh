#!/usr/bin/env bash

cd ../..
docker run           \
    --network="host" \
    -p 8911:8911     \
    -p 12000:12000   \
    -p 9881:9881     \
    -p 9899:9899     \
    -p 9882:9882     \
    -p 9883:9883     \
    -p 9884:9884     \
    --restart always \
    opq
