#!/usr/bin/env bash

set -x

timestamp=$(date +%Y%m%d_%H%M%S)
mkdir ${timestamp}

cp ../docker-deployment/docker-compose.yml ${timestamp}
cp ../docker-deployment/docker-compose-run.sh ${timestamp}
cp ../docker-deployment/.env ${timestamp}
cp docker-prepare-and-run.sh ${timestamp}

tar czf $timestamp.tar.gz ${timestamp}

rm -rf ${timestamp}

EMILIA_DOCKER_TRANSFER_DIR=/home/opquser/docker/transfers

scp -P 29862 $timestamp.tar.gz opquser@emilia.ics.hawaii.edu:${EMILIA_DOCKER_TRANSFER_DIR}

set +x
