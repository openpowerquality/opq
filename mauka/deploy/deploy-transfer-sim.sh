#!/usr/bin/env bash

if [ -z "$1" ]
    then
    echo "usage: ./deploy-transfer-sim.sh [mauka distribution]"
    exit 1
fi

set -x

DIST=$1

scp -P 3022 ${DIST} pi@localhost:/home/pi/mauka/.

set +x