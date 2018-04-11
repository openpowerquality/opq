#!/bin/bash

DB_BASE=/var/mongodb/opq
LOG_BASE=/var/log/mongodb
MONGOD=/usr/local/bin/mongodb/bin/mongod

# Start replica sets
${MONGOD} --replSet opq-replica-set --port 27018 --dbpath ${DB_BASE}/rs0 --fork --logpath ${LOG_BASE}/rs0.loq
${MONGOD} --replSet opq-replica-set --port 27019 --dbpath ${DB_BASE}/rs1 --fork --logpath ${LOG_BASE}/rs1.loq
${MONGOD} --replSet opq-replica-set --port 27020 --dbpath ${DB_BASE}/rs2 --fork --logpath ${LOG_BASE}/rs2.loq
