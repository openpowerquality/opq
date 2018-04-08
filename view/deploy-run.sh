#!/bin/bash

set -x

cd deploy/bundle
cd programs/server
npm install
cd ../..
export MONGO_URL='mongodb://localhost:27017/opq'
export ROOT_URL='http://localhost'
export PORT=3000
export METEOR_SETTINGS=$(cat ../../config/settings.development.json)
echo $METEOR_SETTINGS
node main.js

set +x