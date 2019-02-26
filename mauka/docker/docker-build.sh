#!/usr/bin/env bash

# First, check if the deps have been built
if [[ -z "$(docker images -q mauka-deps:latest 2> /dev/null)" ]]; then
  echo "Building mauka-deps..."
  ./docker-build-deps.sh
  echo "Done building mauka-deps."
else
  echo "mauka-deps found locally, no need build."
fi

# Now build mauka
echo "Building mauka..."
cd ../..
docker build -t mauka -f mauka/docker/Dockerfile .
echo "Done building mauka."