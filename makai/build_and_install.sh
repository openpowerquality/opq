#/bin/bash
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


cd TriggeringService/
bash build.sh
sudo cp build/makai /usr/local/bin
sudo mkdir -p /usr/local/share/opq/makai
sudo cp -r build/plugins /usr/local/share/opq/makai
sudo cp build/makai.json /etc/opq
cd ..

sudo cp acq_broker /etc/init.d/
sudo cp trg_broker /etc/init.d/
sudo cp makai_service /etc/init.d/
sudo update-rc.d acq_broker defaults
sudo update-rc.d trg_broker defaults
sudo update-rc.d makai_service defaults


