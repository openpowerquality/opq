#!/usr/bin/env bash

ONE_MONTH_AGO=1519084800000

mongodump --db opq --gzip --collection events --query '{"target_event_start_timestamp_ms": {$gte: '"${ONE_MONTH_AGO}"'}}'
mongodump --db opq --gzip --collection box_events --query '{"event_start_timestamp_ms": {$gte: '"${ONE_MONTH_AGO}"'}}'
mongodump --db opq --gzip --collection fs.files --query '{"uploadDate": {$gte: ISODate("2018-02-20T00:00:00Z")}}'
mongodump --db opq --gzip --collection measurements --query '{"timestamp_ms": {$gte: '"${ONE_MONTH_AGO}"'}}'
mongodump --db opq --gzip --collection trends --query '{"timestamp_ms": {$gte: '"${ONE_MONTH_AGO}"'}}'

# Some things it probably makes sense to just dump the entire collection
mongodump --db opq --gzip --collection fs.chunks # Figure out how to query by date
mongodump --db opq --gzip --collection roles
mongodump --db opq --gzip --collection users
mongodump --db opq --gzip --collection opq_boxes
mongodump --db opq --gzip --collection meteor_accounts_loginServiceConfiguration


