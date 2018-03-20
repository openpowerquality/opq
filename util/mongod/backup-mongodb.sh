#!/usr/bin/env bash

DATE_STR=`date +%d%b%Y`
ARCHIVE=opq.dump.${DATE_STR}.tar.gz

# Dump the database
/usr/local/bin/mongodump --db opq --gzip --out /var/opq/backup/mongodb

# Compress the output
cd /var/opq/backup/mongodb
/bin/tar czf ${ARCHIVE} opq/

# Upload to google drive
/usr/local/bin/gdrive upload ${ARCHIVE} && rm ${ARCHIVE}