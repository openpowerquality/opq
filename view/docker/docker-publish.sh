#!/usr/bin/env bash

# Source the Docker-Compose .env file and grab the VIEW_IMAGE variable.
. ../../util/docker/.env

DOCKER_SRC_IMAGE=opqview:latest
DOCKER_DEST_IMAGE=$VIEW_IMAGE

echo "=> This will tag the '${DOCKER_SRC_IMAGE}' image as '${DOCKER_DEST_IMAGE}' and push to your Docker registry."
echo "=> If you need to change the destination image tag (${DOCKER_DEST_IMAGE}), you can abort this script
and modify the 'VIEW_IMAGE' variable found in the 'opq/util/docker/.env' file."
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