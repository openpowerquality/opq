#!/bin/bash

if [[ -z "$1" ]]
  then
    echo "Updates endpoint not supplied."
    echo "usage: ./updater.sh [updates endpoint]"
    exit 1
fi

UPDATES_ENDPOINT=${1}

sudo rm -rf /tmp/opq
mkdir -p /tmp/opq
cd /tmp/opq

echo "Deleting any old updates..."
rm -rf opq-box-update-*
echo "Done."

echo "Downloading latest update..."
wget ${UPDATES_ENDPOINT}/latest -O update.tar.bz2
echo "Done."

echo "Extracting contents..."
tar xf update.tar.bz2
echo "Done"

echo "Running update script..."
cd opq-box-update-*
echo "Found update version $(<VERSION)"
sudo ./install_update.sh
echo "Done"

echo "Cleaning up..."
cd ..
rm -rf opq-box-update*
rm -rf update.tar.bz2
echo "Done."

echo "Rebooting..."
sudo reboot


