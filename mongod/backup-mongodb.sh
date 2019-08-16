#!/bin/bash

DATE_STR=`/bin/date +%Y-%m-%d`
WORK_DIR=/var/opq/bak
ARCHIVE=opq.dump.${DATE_STR}.bak

# Dump the database. The resulting archive will be in /var/opq/bak on the host machine.do
docker pull mongo:4.0.5
docker tag mongo:4.0.5 bak-mongo
docker run -it -v ${WORK_DIR}:${WORK_DIR} --net opq-docker_default --link opq-mongo:bak-mongo --rm mongo mongodump --host mongo --db opq --gzip --archive=${WORK_DIR}/${ARCHIVE}

# Upload to Google Drive and cleanup
/usr/local/bin/gdrive upload --parent "1K6S8pmlUt6Cc5CWNs_PJyikhdQ9_KXDS" ${WORK_DIR}/${ARCHIVE} \
  && rm ${WORK_DIR}/${ARCHIVE}
