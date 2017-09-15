#!/usr/bin/env bash

if [[ $EUID -ne 0 ]]; then
   echo "This script must be run as root" 1>&2
   exit 1
fi

set -o xtrace

cp mongod-service.sh /etc/init.d/mongod
update-rc.d mongod defaults

set +o xtrace