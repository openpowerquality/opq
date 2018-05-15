#!/usr/bin/env bash

if [ -z "$1" ]
    then
    echo "usage: ./deploy-transfer-emilia.sh [mauka distribution]"
    exit 1
fi

set -x

DIST=$1

scp -P 29862 ${DIST} opquser@emilia.ics.hawaii.edu:/home/opquser/mauka/.

set +x