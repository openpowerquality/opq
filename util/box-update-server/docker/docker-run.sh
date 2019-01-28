#!/bin/bash

docker run
    --detach                                                \
    --interactive                                           \
    --tty                                                   \
    --name opqboxupdateserver                               \
    --network="host"                                        \
    --expose=8151                                           \
    --publish 8151:8151                                     \
    --volume /var/opq/box-updates:/var/opq/box-updates:ro   \
    --restart always                                        \
    openpowerquality/opqboxupdateserver:0.1                 \
    8151                                                    \
    /var/opq/box-updates
