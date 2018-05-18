#!/bin/bash

# This script installs the Mauka service and utilities to a running system.

if [[ $EUID -ne 0 ]]; then
   echo "This script must be run as root" 1>&2
   exit 1
fi

set -o xtrace

# This installs mauka as a system service to be started at runtime
cp scripts/mauka-service.sh /etc/init.d/mauka
update-rc.d mauka defaults

# Convenience shortcut for accessing mauka command line interface
cp scripts/mauka-cli.sh /usr/local/bin/mauka-cli
chmod +x /usr/local/bin/mauka-cli

# Convenience shortcut for accessing mauka log
cp scripts/mauka-log.sh /usr/local/bin/mauka-log
chmod +x /usr/local/bin/mauka-log

# Clean old version of Mauka if it exists
rm -rf /usr/local/bin/opq/mauka

# Install mauka and configuration
mkdir -p /usr/local/bin/opq
chown -R opq:opq /usr/local/bin/opq
cp -R mauka /usr/local/bin/opq/.
cp mauka/config.json /etc/opq/mauka/config.json

# Setup logs
mkdir -p /var/log/opq
chown -R opq:opq /var/log/opq

set +o xtrace