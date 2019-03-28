#!/usr/bin/env bash

VERSION=${1}

if [[ -z ${VERSION} ]]; then
    echo "version not specified"
    exit 1
fi

./docker-build.sh                                                   \
    && docker tag mauka:latest openpowerquality/mauka:${VERSION}    \
    && docker push openpowerquality/mauka:${VERSION}