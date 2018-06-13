#!/bin/bash

# This script will creates a dated dump of the OPQ database.

DATE_STR=`/bin/date +%Y-%m-%d`
ARCHIVE=opq.dump.${DATE_STR}.tar.gz
BACKUPS_DIR=/home/opquser/backups

# Dump the database
/usr/local/bin/mongodump --db opq --gzip --out ${BACKUPS_DIR}

# Compress the output
cd ${BACKUPS_DIR}
/bin/tar czf ${ARCHIVE} opq/

# Delete the uncompressed output
/bin/rm -rf opq/
