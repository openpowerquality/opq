#!/usr/bin/env bash
SRC_DIR=$(pwd)
ETC_OPQ_SETTINGS="/etc/opq/settings.set"
ETC_OPQ_DIR="/etc/opq/"

#Installs DSPutill
cd ${DSPutill_DIR}
	echo Installing DSPutill
	sudo python setup.py install
cd ${SRC_DIR}
#Installs WIFIutill
cd ${WIFI_DIR}
	echo Installing WIFIutill
	sudo python setup.py install
cd ${SRC_DIR}

#Check for settings.set
if [ ! -f ${ETC_OPQ_SETTINGS} ]; then
	echo ${ETC_OPQ_SETTINGS} not found
	echo Copying template.set to ${ETC_OPQ_SETTINGS}
	#uses template.set if settings.set doesn't exist
	sudo mkdir -p ${ETC_OPQ_DIR} && sudo cp template.set ${ETC_OPQ_SETTINGS} 
fi

#Copy Triggering Binary
echo Copying Triggering Binary to /usr/local/bin/
sudo cp ./Triggering/build/Triggering /usr/local/bin

#Install Acquisition
echo Installing Acquisition Software
sudo cp ./Acquisition/build/Acquisition /usr/local/bin
cd ${SRC_DIR}


#Create opquser
echo Creating account opquser if it does not exist
if id -u opquser 2>/dev/null; then 
    sudo useradd opquser
else
    echo "User already exists"
fi

#Creating a logging directory
echo Creating logging directories
mkdir -p /var/log/opq
chown opquser /var/log/opq

#Configure the init scripts
cp opq_services /etc/init.d/
chmod +x /etc/init.d/opq_services
update-rc.d opq_services defaults
update-rc.d opq_services enable
