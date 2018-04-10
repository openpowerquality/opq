#!/bin/bash

# This script builds a distribution of mauka for deployment. The built deployment will have a filename of the form
# mauka.[timestamp].tar.bz2

# Set CWD to opq base directory
cd ../..

# Set up staging directory
STAGING_DIR=mauka.`date +%s`
mkdir -p mauka/deploy/${STAGING_DIR}

# Create a staging area for which this deployment will be built. Clean the old one if it exists.
mkdir -p mauka/deploy/${STAGING_DIR}/mauka

# Copy over required files -- Mauka
cp -r mauka/constants mauka/deploy/${STAGING_DIR}/mauka
cp -r mauka/mongo mauka/deploy/${STAGING_DIR}/mauka
cp -r mauka/plugins mauka/deploy/${STAGING_DIR}/mauka
cp -r mauka/protobuf mauka/deploy/${STAGING_DIR}/mauka
cp mauka/config.json mauka/deploy/${STAGING_DIR}/mauka
cp mauka/OpqMauka.py mauka/deploy/${STAGING_DIR}/mauka
cp mauka/requirements.txt mauka/deploy/${STAGING_DIR}/mauka

# Copy over required files -- Installs scripts and utilities
mkdir -p mauka/deploy/${STAGING_DIR}/scripts
cp mauka/deploy/mauka-cli.sh mauka/deploy/${STAGING_DIR}/scripts
cp mauka/deploy/mauka-log.sh mauka/deploy/${STAGING_DIR}/scripts
cp mauka/deploy/mauka-service.sh mauka/deploy/${STAGING_DIR}/scripts

# Copy deploy-run.sh to deployment root
cp mauka/deploy/deploy-run.sh mauka/deploy/${STAGING_DIR}

# Build deployment distribution
tar cjf mauka/deploy/${STAGING_DIR}.tar.bz2 -C mauka/deploy ${STAGING_DIR}

# Deploy distribution to emilia
scp -P 29862 mauka/deploy/${STAGING_DIR}.tar.bz2 opquser@emilia.ics.hawaii.edu:/home/opquser/mauka/.

# Clean
rm -rf mauka/deploy/${STAGING_DIR}
rm -f mauka/deploy/${STAGING_DIR}.tar.bz2






