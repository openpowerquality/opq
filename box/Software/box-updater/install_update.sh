#!/bin/bash

if [[ $EUID -ne 0 ]]; then
   echo "This script must be run as root"
   exit 1
fi

# Update box-config-daemon
killall python3
rm -rf /usr/local/box-config-daemon/*
mkdir -p /usr/local/box-config-daemon
cp -R box-config-daemon /usr/local/box-config-daemon/.

# Update triggering

# Update box-updater
rm -rf /usr/local/box-updater/*
mkdir -p /usr/local/box-updater

# Update kernel

# Update firmware

