#!/usr/bin/env bash

mkdir makai-build
cp -r ../../makai makai-build
cp -r ../../protocol makai-build

docker build -t makai .

rm -rf makai-build