#!/bin/bash

set -x
timestamp=$(date +%Y%m%d_%H%M%S)
mkdir $timestamp
cp app.tar.gz $timestamp
cp deploy-run.sh $timestamp
cd $timestamp
tar xf app.tar.gz
rm app.tar.gz
cd ..
tar czf $timestamp.tar.gz $timestamp
rm -rf $timestamp
scp -P 29862 $timestamp.tar.gz opquser@emilia.ics.hawaii.edu:view

set +x
