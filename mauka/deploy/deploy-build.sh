#!/bin/bash

set -x

# This script builds a distribution of mauka for deployment. The built deployment will have a filename of the form
# mauka.[timestamp].tar.bz2

# Set CWD to opq base directory
cd ../..

# Set up staging directory
TIMESTAMP=$(date +%Y%m%d_%H%M%S)
mkdir -p mauka/deploy/${TIMESTAMP}

# Create a staging area for which this deployment will be built. Clean the old one if it exists.
mkdir -p mauka/deploy/${TIMESTAMP}/mauka

# Copy over required files -- Mauka
cp -r mauka/constants mauka/deploy/${TIMESTAMP}/mauka
cp -r mauka/mongo mauka/deploy/${TIMESTAMP}/mauka
cp -r mauka/plugins mauka/deploy/${TIMESTAMP}/mauka
cp -r mauka/protobuf mauka/deploy/${TIMESTAMP}/mauka
cp mauka/config.json mauka/deploy/${TIMESTAMP}/mauka
cp mauka/OpqMauka.py mauka/deploy/${TIMESTAMP}/mauka
cp mauka/requirements.txt mauka/deploy/${TIMESTAMP}/mauka

# Copy over required files -- Installs scripts and utilities
mkdir -p mauka/deploy/${TIMESTAMP}/scripts
cp mauka/deploy/mauka-cli.sh mauka/deploy/${TIMESTAMP}/scripts
cp mauka/deploy/mauka-log.sh mauka/deploy/${TIMESTAMP}/scripts
cp mauka/deploy/mauka-service.sh mauka/deploy/${TIMESTAMP}/scripts

# Copy deploy-run.sh to deployment root
cp mauka/deploy/deploy-run.sh mauka/deploy/${TIMESTAMP}

# Build deployment distribution
tar cvjf mauka/deploy/${TIMESTAMP}.tar.bz2 -C mauka/deploy ${TIMESTAMP}

## Deploy distribution to emilia
#scp -P 29862 mauka/deploy/${TIMESTAMP}.tar.bz2 opquser@emilia.ics.hawaii.edu:/home/opquser/mauka/.
#
# Clean
rm -rf mauka/deploy/${TIMESTAMP}

set +x




