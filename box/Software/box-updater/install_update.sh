#!/bin/bash

if [[ $EUID -ne 0 ]]; then
   echo "This script must be run as root"
   exit 1
fi

# Update box-config-daemon
SERVICE="box-config-daemon.service"
sudo systemctl stop ${SERVICE}
sudo systemctl disable ${SERVICE}

rm -rf /usr/local/box-config-daemon/*
mkdir -p /usr/local/box-config-daemon
cp -R box-config-daemon/* /usr/local/box-config-daemon/.

sudo cp box-config-daemon/${SERVICE} /etc/systemd/system/.
sudo systemctl enable ${SERVICE}

# Update version info
cp VERSION /usr/local/box-config-daemon/.

# Update triggering

# Update kernel

# Update firmware

