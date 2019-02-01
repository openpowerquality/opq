#!/bin/bash

if [[ $EUID -ne 0 ]]; then
   echo "This script must be run as root"
   exit 1
fi

echo "Running install_update.sh...."

# Update box-config-daemon
echo "Stopping and removing box-config-daemon.service..."
SERVICE="box-config-daemon.service"
#sudo systemctl stop ${SERVICE}
#sudo systemctl disable ${SERVICE}
echo "Done."

echo "Removing old box-config-daemon..."
rm -rf /usr/local/box-config-daemon/*
echo "Done."

echo "Installing box-config-daemon...."
mkdir -p /usr/local/box-config-daemon
cp -R box-config-daemon/* /usr/local/box-config-daemon/.
echo "Done."

echo "Installing box-config-daemon.service..."
sudo cp box-config-daemon/${SERVICE} /etc/systemd/system/.
sudo systemctl enable ${SERVICE}
echo "Done"

# Update version info
echo "Updating VERSION info..."
cp VERSION /usr/local/box-config-daemon/.
echo "Done."

# Update triggering

# Update kernel

# Update firmware

