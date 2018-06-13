#!/bin/bash

DATE_STR=`/bin/date +%Y-%m-%d`
ARCHIVE=opq.dump.${DATE_STR}.tar.gz
BACKUPS_DIR=/home/opquser/backups

# Dump the database
/usr/local/bin/mongodump --db opq --gzip --out ${BACKUPS_DIR}

# Compress the output
cd ${BACKUPS_DIR}
/bin/tar czf ${ARCHIVE} opq/

# Delete the uncompressed output
rm -rf opq/

## Upload to google drive
#/usr/local/bin/gdrive upload --parent "1K6S8pmlUt6Cc5CWNs_PJyikhdQ9_KXDS" ${ARCHIVE} && rm ${ARCHIVE}