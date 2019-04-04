#!/bin/bash

# This script first uploads the latest local backup and then deletes all local backups. Then, this script creates a new
# local backup. This allows us to always have one local backup on the server and the previous day's backup
# "in the cloud".

. /home/opquser/backup/upload-and-prune.sh && . /home/opquser/backup-mongodb.sh