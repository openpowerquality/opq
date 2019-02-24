#!/usr/bin/env bash

# Helper script that copies (and overwrites existing) deployment files to the dedicated deployment directory on Emilia,
# then invoking the docker-compose-run.sh script to initiate (re)deployment. Note that Docker-Compose is intelligent
# enough to detect the difference of deployment files and will only re-deploy the necessary containers for us.

DOCKER_DEPLOY_DIR=/home/opquser/docker/deployment

cp docker-compose.yml ${DOCKER_DEPLOY_DIR}
cp docker-compose-run.sh ${DOCKER_DEPLOY_DIR}
cp .env ${DOCKER_DEPLOY_DIR}
cp init-letsencrypt.sh ${DOCKER_DEPLOY_DIR}
cp data/nginx/app.conf ${DOCKER_DEPLOY_DIR}/data/nginx

cd ${DOCKER_DEPLOY_DIR} && ./docker-compose-run.sh
