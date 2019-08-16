#!/bin/bash

if [[ -z "${1}" ]]; then
    echo "usage: ./restore-mongodb.sh [path to archive]"
    exit 1
fi

PATH_TO_ARCHIVE=${1}

docker pull mongo:4.0.5
docker tag mongo:4.0.5 bak-mongo
docker run -it -v /var/opq/bak:/var/opq/bak --net opq-docker_default --link opq-mongo:bak-mongo --rm mongo mongorestore --host mongo --gzip --archive=${PATH_TO_ARCHIVE}
