#!/usr/bin/env bash

VERSION=$(date +%s)
DIST=opq-box-update-${VERSION}

mkdir -p ${DIST}

# box-config-daemon
cp -R ../box-config-daemon ${DIST}/.

# Install script
cp install_update.sh ${DIST}/.

# Version info
echo ${VERSION} > ${DIST}/VERSION

# Compress
tar cjf ${DIST}.tar.bz2 ${DIST}

# Cleanup
rm -rf ${DIST}