#!/bin/bash

cwd=$(pwd)

rm -rf build
mkdir -p build/plugins

echo "Building makai daemon"
cd makai
	cargo build --release -q
	cp target/release/makai "$cwd/build"
	cp makai.json "$cwd/build"
cd ..


echo "Building plugins"
for f in plugins/*
do
	echo "$f"
	if [ -d "$f" ]; then
		cd "$f"
		       	cargo build --release -q
			cp target/release/*.so "$cwd/build/plugins"
	       	cd "$cwd"
	fi
done
