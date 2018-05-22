#!/bin/bash

if [[ $EUID -ne 0 ]]; then
   echo "This script must be run as root" 1>&2
   exit 1
fi

set -x

# Make sure curl is installed
apt-get install -y curl

# Download generic linux 64bit mongodb distribution
DIST=mongodb-linux-x86_64-3.6.3
curl -O https://fastdl.mongodb.org/linux/${DIST}.tgz

# Extract
tar xvf ${DIST}.tgz

# Install to usr local bin
INSTALL_DIR=/usr/local/bin/mongodb
mkdir -p ${INSTALL_DIR}
cp -R -n ${DIST}/* ${INSTALL_DIR}

# Make sure log directory is available
mkdir -p /var/log/mongodb
chown -R opq:opq /var/log/mongodb

# Update environment
echo 'export PATH='${INSTALL_DIR}'/bin:$PATH' >> /home/opquser/.profile

# Ensure data paths exists
DB_BASE=/var/mongodb/opq
mkdir -p ${DB_BASE}/rs0
mkdir -p ${DB_BASE}/rs1
mkdir -p ${DB_BASE}/rs2

# Update permissions
chown -R opq:opq ${DB_BASE}

echo "If you want mongo on your path, reload with \". ~/.profile\""

set +x
