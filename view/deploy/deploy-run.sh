#!/bin/bash

echo Make sure node version is $(cat bundle/.node_version.txt)

(cd bundle/programs/server && npm install)
export MONGO_URL='mongodb://localhost:27017/opq'
export ROOT_URL='http://localhost'
export PORT=8888
export METEOR_SETTINGS=$(cat settings.development.json)
nohup node bundle/main > logfile.txt 2>&1 &

