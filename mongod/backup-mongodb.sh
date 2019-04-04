#!/bin/bash

DATE_STR=`/bin/date +%Y-%m-%d`
ARCHIVE=opq.dump.${DATE_STR}.bak

# Dump the database. The resulting archive will be in /var/bak on the host machine.do
docker pull mongo:4.0.5
docker tag mongo:4.0.5 bak-mongo
docker run -it -v /var/bak:/bak --net opq-docker_default --link opq-mongo:bak-mongo --rm mongo mongodump --host mongo --db opq --gzip --archive=/bak/${ARCHIVE}