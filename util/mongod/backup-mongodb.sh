#!/bin/bash

DATE_STR=`/bin/date +%d%b%Y`
ARCHIVE=opq.dump.${DATE_STR}.tar.gz

# Delete any old backups
rm -rf /var/opq/backup/mongodb/opq

# Dump the database
/usr/local/bin/mongodump --db opq --gzip --out /var/opq/backup/mongodb

# Compress the output
cd /var/opq/backup/mongodb
/bin/tar czf ${ARCHIVE} opq/

# Upload to google drive
/usr/local/bin/gdrive upload --parent "1K6S8pmlUt6Cc5CWNs_PJyikhdQ9_KXDS" ${ARCHIVE} && rm ${ARCHIVE}