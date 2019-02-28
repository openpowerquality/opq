#!/usr/bin/env bash

set -x

dist_dir=$(date +%Y%m%d_%H%M%S)
mkdir ${dist_dir}
dist=${dist_dir}.tar.bz2

cp ../docker-deployment/docker-compose.yml ${dist_dir}
cp ../docker-deployment/docker-compose-run.sh ${dist_dir}
cp ../docker-deployment/.env ${dist_dir}
cp docker-prepare-and-run.sh ${dist_dir}

tar cjfv ${dist} ${dist_dir}

rm -rf ${dist_dir}

EMILIA_DOCKER_TRANSFER_DIR=/home/opquser/docker/transfers

scp -P 29862 ${dist} opquser@emilia.ics.hawaii.edu:${EMILIA_DOCKER_TRANSFER_DIR}

ssh -p 29862 opquser@emilia.ics.hawaii.edu "cd ${EMILIA_DOCKER_TRANSFER_DIR};tar xfv ${dist};cd ${dist_dir};bash docker-prepare-and-run.sh"

set +x
