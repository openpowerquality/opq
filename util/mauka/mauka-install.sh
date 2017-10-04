#!/usr/bin/env bash

if [[ $EUID -ne 0 ]]; then
   echo "This script must be run as root" 1>&2
   exit 1
fi

set -o xtrace

cp mauka-service.sh /etc/init.d/mauka
update-rc.d mauka defaults

cp mauka-cli.sh /usr/local/bin/mauka-cli
chmod +x /usr/local/bin/mauka-cli

cp mauka-log.sh /usr/local/bin/mauka-log
chmod +x /usr/local/bin/mauka-log

mkdir -p /usr/local/bin/opq
chown -R opq:opq /usr/local/bin/opq
cd ../..
cp -R mauka /usr/local/bin/opq/.
cp mauka/config.json /etc/opq/mauka/config.json

mkdir -p /var/log/opq
chown -R opq:opq /var/log/opq

set +o xtrace
