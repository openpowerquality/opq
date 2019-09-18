#!/bin/bash

export RUSTC_WRAPPER=~/.cargo/bin/sccache
sccache --start-server

echo "Building AcquisitionBroker"
cd ../AcquisitionBroker
cargo build --release

echo "Building EventService"
cd ../EventService
cargo build --release

echo "Building TriggeringBroker"
cd ../TriggeringBroker
cargo build --relase

echo "Building TriggeringService"
cd ../TriggeringService
cargo build --release

echo "Building TriggeringService plugin health"
cd plugins/health
cargo build --release

echo "Building TriggeringService plugin mongo"
cd ../mongo
cargo build --release

echo "Building TriggeringService plugin napali_trigger"
cd ../napali_trigger
cargo build --release

echo "Building TriggeringService plugin print"
cd ../print
cargo build --release

echo "Building TriggeringService plugin threshold_trigger"
cd ../threshold_trigger
cargo build --release

sccache --stop-server