#!/usr/bin/env bash

cp mongod-service.sh /etc/init.d/mongod
update-rc.d mongod defaults
service mongod start
