#!/usr/bin/env bash

VERSION=${1}

if [[ -z ${VERSION} ]]; then
    echo "version not specified"
    exit 1
fi

./docker-build.sh                                                       \
    && docker tag healthv2:latest openpowerquality/healthv2:${VERSION}  \
    && docker push openpowerquality/healthv2:${VERSION}
