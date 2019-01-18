#!/usr/bin/env bash

DIST=opq-box-update-$(date +%s)

mkdir -p ${DIST}

# box-config-daemon
cp -R ../box-config-daemon ${DIST}/.

# box-updater


# install script
cp install_update.sh ${DIST}/.

# Compress
tar cjf ${DIST}.tar.bz2 ${DIST}

# Cleanup
rm -rf ${DIST}