#!/usr/bin/env bash

# Subdirectory for src files
TIMESTAMP=$(date +%Y%m%d_%H%M%S)
mkdir -p ${TIMESTAMP}

######################
# Build Docker Image #
######################

IMAGE_NAME=opqboxupdateserver

echo "=> Copying box-update-server source files into ${TIMESTAMP}"

cp ../box_update_server.py ./${TIMESTAMP}/
cp ./Dockerfile ./${TIMESTAMP}

cd ${TIMESTAMP}

echo "=> Building Docker image..."

docker build --tag=${IMAGE_NAME} .

echo "=> Deleting all temporary files..."

cd ..

rm -rf ${TIMESTAMP}

echo "=> Docker build complete!"
echo "=> Use the 'docker image ls' command to check that the '${IMAGE_NAME}' image was successfully generated"