#!/usr/bin/env bash

set -x

timestamp=$(date +%Y%m%d_%H%M%S)
mkdir $timestamp

cp ../docker-compose.yml $timestamp
cp ../docker-compose-run.sh $timestamp
cp ../.env $timestamp

tar czf $timestamp.tar.gz $timestamp

rm -rf $timestamp

scp -P 29862 $timestamp.tar.gz opquser@emilia.ics.hawaii.edu:docker

set +x
