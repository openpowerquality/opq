#!/usr/bin/env bash

echo "Deploying OPQ Cloud..."

if [[ $EUID -ne 0 ]]; then
   echo "This script must be run as root" 1>&2
   exit 1
fi

set -o xtrace

./mauka/deploy.sh
./makai/deploy.sh
./view/deploy.sh
./health/deploy.sh

set +o xtrace

echo "Finished deploying OPQ Cloud."
