#!/bin/bash

echo Make sure node version is $(cat bundle/.node_version.txt)

(cd bundle/programs/server && npm install)
export MONGO_URL='mongodb://localhost:27017/opq'
export ROOT_URL='http://localhost'
export PORT=8888
export METEOR_SETTINGS=$(cat settings.development.json)

# This is the normal way to start up OPQView
# nohup node bundle/main > logfile.txt 2>&1 &

# Due to node problem producing segfault, start OPQView using patched node in Meteor 1.6.1.1 for now.
# https://github.com/meteor/meteor/blob/devel/History.md#v1611-2018-04-02
nohup meteor node bundle/main > logfile.txt 2>&1 &

