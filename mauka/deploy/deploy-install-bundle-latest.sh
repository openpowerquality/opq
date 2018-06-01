#!/usr/bin/env bash

if [[ $EUID -ne 0 ]]; then
   echo "This script must be run as root" 1>&2
   exit 1
fi

set -x

LATEST_BUNDLE=$(ls *.tar.bz2 | sort | tail -n 1)
./deploy-install-bundle.sh ${LATEST_BUNDLE}

set +x