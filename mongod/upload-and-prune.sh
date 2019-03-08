#!/usr/bin/env bash

# This script will upload the latest OPQ dump to Google Drive and then delete all old backups.

BACKUPS_DIR=/var/bak

cd ${BACKUPS_DIR}

MOST_RECENT=$(ls opq.dump.*.tar.gz | sort | tail -n 1)

/usr/local/bin/gdrive upload --parent "1K6S8pmlUt6Cc5CWNs_PJyikhdQ9_KXDS" ${MOST_RECENT} && /bin/rm -f opq.dump.*.tar.gz