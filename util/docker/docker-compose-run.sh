#!/usr/bin/env bash

# Set environment variables for Docker-Compose

# OPQView Env Vars
export MONGO_URL='mongodb://localhost:27017/opq'
export ROOT_URL='http://localhost'
export PORT=8888
export METEOR_SETTINGS=$(cat ./settings.production.json)

# Startup Docker-Compose. Note: Be sure that docker-compose.yml is same directory as this script.
docker-compose up -d