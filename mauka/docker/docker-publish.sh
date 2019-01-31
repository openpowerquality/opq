#!/usr/bin/env bash

## Publishes the most recently created Mauka image to DockerHub.
## Reminder: Publishing a new version of this service requires modifying the Docker-Compose .env file found in
## opq/util/docker. See the official OPQ docs for further details.

# Source the Docker-Compose .env file and grab the MAUKA_IMAGE variable.
. ../../util/docker/.env

DOCKER_SRC_IMAGE=opqmauka:latest
DOCKER_DEST_IMAGE=$MAUKA_IMAGE

echo "=> This will tag the '${DOCKER_SRC_IMAGE}' image as '${DOCKER_DEST_IMAGE}' and push to your Docker registry."
echo "=> If you need to change the destination image tag (${DOCKER_DEST_IMAGE}), you can abort this script
and modify the 'MAUKA_IMAGE' variable found in the 'opq/util/docker/.env' file."
echo "=> In addition, please ensure that you are logged into the correct Docker registry account before continuing."

read -p "=> Continue? (y/n): " CONT
if [ "$CONT" = "y" ]; then
  echo "=> Tagging '${DOCKER_SRC_IMAGE}' image as '${DOCKER_DEST_IMAGE}'..."
  docker tag $DOCKER_SRC_IMAGE $DOCKER_DEST_IMAGE

  echo "=> Pushing the '${DOCKER_DEST_IMAGE}' image to registry..."
  docker push $DOCKER_DEST_IMAGE
else
  echo "=> Aborting..."
fi
