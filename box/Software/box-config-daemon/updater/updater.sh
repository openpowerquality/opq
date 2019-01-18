#!/bin/bash

if [[ -z "$1" ]]
  then
    echo "Updates endpoint not supplied."
    echo "usage: ./updater.sh [updates endpoint]"
    exit 1
fi

UPDATES_ENDPOINT=${1}

echo "Deleting any old updates..."
rm -rf opq-box-update-*
echo "Done."

echo "Downloading latest update..."
curl -JLO ${UPDATES_ENDPOINT}/latest
echo "Done."

echo "Extracting contents..."
tar xf opq-box-update-*.tar.bz2
echo "Done"

echo "Running update script..."
cd opq-box-update-*
echo "Found update version $(<version)"
./install_update.sh
echo "Done"

echo "Cleaning up..."
cd ..
rm -rf opq-box-update*
echo "Done."

echo "Rebooting..."
sudo reboot


