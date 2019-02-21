#!/usr/bin/env bash

############################
# Create Meteor App Bundle #
############################

timestamp=$(date +%Y%m%d_%H%M%S)
mkdir $timestamp

# Invoke the 'meteor build' command while inside the view/app directory. We include the --directory option, which
# produces a bundle directory instead of a tarball.
# Note: We invoke 'meteor npm install' to ensure that the app's packages are available before we invoke 'meteor build'.
echo "=> Installing app's npm packages, then building Meteor app bundle..."
(cd ../app && meteor npm install && meteor build ../docker/$timestamp --directory --architecture os.linux.x86_64)
echo "=> Meteor build complete"

# Retrieve and print the Meteor bundle's Node version
app_node_version=$(<./$timestamp/bundle/.node_version.txt)
echo "=> This Meteor bundle uses the following Node version: ${app_node_version}"
echo "=> Please ensure that the Dockerfile utilizes a base Node image with matching versions"


######################
# Build Docker Image #
######################

IMAGE_NAME=view

echo "=> Building Docker image..."

# Copy our reference Dockerfile into the newly generated Meteor bundle directory.
cp Dockerfile $timestamp/bundle
cd $timestamp/bundle

# Create Docker image
docker build --tag=${IMAGE_NAME} .

# We can delete the entire $timestamp directory since it's no longer needed. Everything we need is in the Docker image!
echo "=> Deleting all temporary files..."
cd ../../
rm -rf $timestamp

echo "=> Docker build complete!"
echo "=> Use the 'docker image ls' command to check that the '${IMAGE_NAME}' image was successfully generated"
