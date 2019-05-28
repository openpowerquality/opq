#!/usr/bin/env bash

# This file contains convenience aliases and methods for working with a running OPQ docker system.

OPQ_DOCKER="/home/opquser/opq-docker"                   # Home dir of deployment
alias docker_names="docker ps --format '{{.Names}}'"    # Lists all of the long names for docker containers, use this to find your short service name.
alias reload=". ~/.bashrc"                              # Reloads the .bashrc script
alias trigger="curl localhost:8080/trigger"             # Generates a trigger on Makai

# Converts a short service name (e.g. mongo, view, mauka) to the full service name as specified in docker
# (e.g. opq-docker_mauka_1).
full_service_name() {
  if [[ "$#" -eq 0 ]]; then
    echo "usage: full_service_name [short_service_name]"
    return 1
  fi
  SHORT_SERVICE=${1}

  if [[ "${SHORT_SERVICE}" == "mongo" ]]; then
    echo "opq-mongo"
  else
    echo "opq-docker_${SHORT_SERVICE}_1"
  fi
}

# Displays the log contents for a given short service name.
docker_log() {
  if [[ "$#" -eq 0 ]]; then
    echo "usage: docker_log short_service_name [options ...]"
    return 1
  fi

  SERVICE=${1}
  shift
  docker logs $(full_service_name ${SERVICE}) "$@"
}

# Allows you to grep the log contents given a short service name and a string to grep for.
docker_grep() {
  if [[ "$#" -ne 2 ]]; then
    echo "usage: docker_grep short_service_name to_grep_for"
    return 1
  fi
  SERVICE=${1}
  CONTENTS=${2}
  docker_log ${SERVICE} 2>&1 | rg -i ${CONTENTS} -B 5 -A 5
}

# Restarts a docker service given its short service name.
docker_restart() {
  if [[ "$#" -eq 0 ]]; then
    echo "usage: docker_restart short_service_name"
    return 1
  fi
  cd ${OPQ_DOCKER}
  SERVICE=${1}
  docker-compose stop ${SERVICE}
  ./docker-compose-run.sh
  cd -
}

# Pulls a specific version of a docker image from docker hub and then restarts that service.
# This is useful when you publish a version without changing the version number and you want to pull and restart that service.
docker_pull_restart() {
  if [[ "$#" -ne 2 ]]; then
    echo "usage: docker_pull_restart short_service_name version"
    return 1
  fi
  cd ${OPQ_DOCKER}
  SERVICE=${1}
  VERSION=${2}
  docker pull openpowerquality/${SERVICE}:${VERSION}
  docker_restart ${SERVICE}
  cd -
}

# Clears the logfile for a given short service name.
docker_delete_log() {
  if [[ "$#" -ne 1 ]]; then
    echo "usage: docker_delete_lot short_service_name"
    return 1
  fi
  cd ${OPQ_DOCKER}
  SERVICE=${1}
  LOG_FILE=$(docker inspect $(full_service_name ${SERVICE}) | rg -i LogPath | cut -d: -f2 | tr -d '"' | tr -d ',')
  echo "" | sudo tee ${LOG_FILE} > /dev/null
}

# Displays the IP address for the docker short service name passed in.
docker_ip() {
  if [[ "$#" -ne 1 ]]; then
    echo "usage: docker_ip short_service_name"
    return 1
  fi
  SERVICE=${1}
  docker inspect -f '{{range .NetworkSettings.Networks}}{{.IPAddress}}{{end}}' $(full_service_name ${SERVICE})
}

# Displays the IP address for all dockerized services.
docker_ips() {
  echo "view: $(docker_ip view)"
  echo "mauka: $(docker_ip mauka)"
  echo "makai: $(docker_ip makai)"
  echo "health: $(docker_ip health)"
  echo "certbot: $(docker_ip certbot)"
  echo "nginx: $(docker_ip nginx)"
  echo "boxupdateserver: $(docker_ip boxupdateserver)"
  echo "mongo: $(docker inspect -f '{{range .NetworkSettings.Networks}}{{.IPAddress}}{{end}}' opq-mongo)"
}

# Displays the number of client connections to MongoDB per client IP address.
mongo_connections() {
  mongo --eval 'db.currentOp(true).inprog.reduce((accumulator, connection) => { ipaddress = connection.client ? connection.client.split(":")[0] : "Internal"; accumulator[ipaddress] = (accumulator[ipaddress] || 0) + 1; accumulator["TOTAL_CONNECTION_COUNT"]++; return accumulator; }, { TOTAL_CONNECTION_COUNT: 0 })'
}

