#!/bin/bash

if [[ $EUID -ne 0 ]]; then
   echo "This script must be run as root" 1>&2
   exit 1
fi

set -x

cp mongod-service.sh /etc/init.d/mongod
chown opq:opq /etc/init.d/mongod
chmod +x /etc/init.d/mongod

update-rc.d mongod defaults
/etc/init.d/mongod start

set +x