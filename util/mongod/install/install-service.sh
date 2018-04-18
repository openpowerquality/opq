#!/bin/bash

if [[ $EUID -ne 0 ]]; then
   echo "This script must be run as root" 1>&2
   exit 1
fi

set -x

cp start-mongod.sh /usr/local/bin/mongodb/.
chown opq:opq /usr/local/bin/mongodb/start-mongod.sh
chmod +x /usr/local/bin/mongodb/start-mongod.sh

cp mongod-service.sh /etc/init.d/mongod
chown opq:opq /etc/init.d/mongod
chmod +x /etc/init.d/mongod

update-rc.d mongod defaults
set +x