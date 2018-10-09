#!/usr/bin/env bash

if [[ $EUID -ne 0 ]]; then
   echo "This script must be run as root" 1>&2
   exit 1
fi

if [ -z "$1" ]
    then
    echo "usage: ./deploy-install-bundle.sh [mauka distribution bundle]"
    exit 1
fi

set -x

BUNDLE=${1}
DIR=${BUNDLE%%.*}

tar xf ${BUNDLE}
cd ${DIR}
./deploy-install.sh
cd ..
rm -rf ${DIR}

set +x