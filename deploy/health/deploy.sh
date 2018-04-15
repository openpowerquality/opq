#!/usr/bin/env bash

echo "Deploying Health..."

if [[ $EUID -ne 0 ]]; then
   echo "This script must be run as root" 1>&2
   exit 1
fi

set -o xtrace

# Deploy stuff goes here.

set +o xtrace
