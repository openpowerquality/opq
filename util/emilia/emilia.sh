#!/usr/bin/env bash

if [ -z "$1" ]; then
    echo "usage: ./emilia.sh [username]"
    exit 1
fi

USERNAME=$1
SERVER="emilia.ics.hawaii.edu"
SSH_PORT=29862
MONGO_PORT=27017

# Pass -N -f if you only want to forward port and have ssh go into background
ssh -p ${SSH_PORT} ${USERNAME}@${SERVER} -L ${MONGO_PORT}:${SERVER}:${MONGO_PORT}