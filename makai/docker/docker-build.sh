#!/usr/bin/env bash

mkdir -p makai-build/makai

cp -r ../AcquisitionBroker makai-build/makai
cp -r ../TriggeringBroker makai-build/makai
cp -r ../TriggeringService makai-build/makai
cp -r ../../protocol makai-build
cp run-makai.sh makai-build/makai

docker build -t makai .

rm -rf makai-build