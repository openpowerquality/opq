#!/bin/bash

HTTP_SERVER_PORT=8151
UPDATES_DIR=/var/opq/box-updates
VERSION=0.1

docker run                                                  \
    --detach                                                \
    --interactive                                           \
    --tty                                                   \
    --name opqboxupdateserver                               \
    --network="host"                                        \
    --expose=${HTTP_SERVER_PORT}                            \
    --publish ${HTTP_SERVER_PORT}:${HTTP_SERVER_PORT}       \
    --volume ${UPDATES_DIR}:${UPDATES_DIR}:ro               \
    --restart always                                        \
                                                            \
    openpowerquality/opqboxupdateserver:${VERSION}          \
    ${HTTP_SERVER_PORT}                                     \
    ${UPDATES_DIR}
