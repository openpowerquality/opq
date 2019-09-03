#!/usr/bin/env bash

VERSION=${1}

if [[ -z ${VERSION} ]]; then
    echo "version not specified"
    exit 1
fi

./docker-build.sh                                                   \
    && docker tag makai:latest openpowerquality/makai:${VERSION}    \
    && docker push openpowerquality/makai:${VERSION}
