#!/bin/bash
cd AcquisitionBroker/
mkdir -p build
cd build
cmake ..
make -j8
sudo cp AcquisitionBroker /usr/local/bin
cd ../..

cd TriggeringBroker/
mkdir -p build
cd build
cmake ..
make -j8
sudo cp TriggeringBroker /usr/local/bin
cd ../..

cd Makai
cargo build --release
sudo cp target/release/makai /usr/local/bin
cd ..

sudo cp acq_broker /etc/init.d/
sudo cp trg_broker /etc/init.d/
sudo cp makai /etc/init.d/
sudo update-rc.d acq_broker defaults
sudo update-rc.d trg_broker defaults
sudo update-rc.d makai_service defaults


