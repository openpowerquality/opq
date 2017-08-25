#!/usr/bin/env bash

if [[ $EUID -ne 0 ]]; then
   echo "This script must be run as root" 1>&2
   exit 1
fi

set -o xtrace

# Download latest .proto file amd compile it
cd ./protobuf/
rm *.proto*
wget https://raw.githubusercontent.com/openpowerquality/opq-proto/master/opq.proto
protoc opq.proto --python_out=.
cd -

# Compile the broker
cd ./MaukaBroker/
make
cd -

# Make sure directories exist
mkdir -p /etc/opq
mkdir -p /usr/local/bin/opq/OpqMauka

# Stop current service
service opqmauka stop

# Install OpqMauka broker
cp ./MaukaBroker/config.json /etc/opq/opqmauka.broker.config.json
cp ./MaukaBroker/Mauka_broker /usr/local/bin/opq/.

# Install OpqMauka
cp config.json /etc/opq/opqmauka.config.json
cp OpqMauka.py /usr/local/bin/opq/OpqMauka/.
cp -R mongo/ /usr/local/bin/opq/OpqMauka/.
cp -R plugins/ /usr/local/bin/opq/OpqMauka/.
cp -R protobuf/ /usr/local/bin/opq/OpqMauka/.

# Install service
cp opq.sh /etc/init.d/opqmauka
update-rc.d opqmauka defaults

# Start service
service opqmauka start

set +o xtrace


