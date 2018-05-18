#!/bin/bash

set -x # echo on

gulp build

rm -rf ../../app/public/semantic-ui
rm -rf ../../app/public/themes
mkdir  ../../app/public/semantic-ui/
cp -r dist/semantic.min.css ../../app/public/semantic-ui/
cp -r dist/themes ../../app/public/themes
