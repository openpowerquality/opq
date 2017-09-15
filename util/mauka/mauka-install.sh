#!/usr/bin/env bash

if [[ $EUID -ne 0 ]]; then
   echo "This script must be run as root" 1>&2
   exit 1
fi

set -o xtrace

cp mauka-service.sh /etc/init.d/mauka
update-rc.d mauka defaults

cd ../..
cp -R mauka /usr/local/bin/opq/.
cp mauka/config.json /etc/opq/mauka/config.json

set +o xtrace
