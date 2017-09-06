#!/usr/bin/env bash
TRIGGERING_BUILD_DIR="./Triggering/build/"
ACQUISITION_BUILD_DIR="./Acquisition/build/"
TRIGGERING_DOCS_DIR="./docs/Triggering"
FIRMWARE_DIR="../Firmware"
FIRMWARE_DOCS_DIR="./docs/Firmware"
DSPutill_DIR="./DSPutill/"
WIFI_DIR="./opqwifi/"
SRC_DIR=$(pwd)

#Building kernel files
cd kernel
	echo Building kernel driver.
	make >> /dev/null
cd ${SRC_DIR}

#Build protocol files
rm -rf proto
git clone https://github.com/openpowerquality/opq-proto.git proto
mkdir -p Triggering/proto
mkdir -p Acquisition/proto
protoc -I=proto/ --cpp_out=Triggering/proto proto/opq.proto
protoc -I=proto/ --cpp_out=Acquisition/proto proto/opq.proto

#build triggering
rm -rf ${TRIGGERING_BUILD_DIR}
rm -rf ${ACQUISITION_BUILD_DIR}

if [ ! -d ${TRIGGERING_BUILD_DIR} ]; then
	echo Creating a build directory for the Triggering daemon ${TRIGGERING_BUILD_DIR}
	mkdir -p ${TRIGGERING_BUILD_DIR}
	cd  ${TRIGGERING_BUILD_DIR}
	cmake  ${SRC_DIR}/Triggering -DCMAKE_TOOLCHAIN_FILE=../../../../arm-linux-gnueabihf.cmake 
	cd ${SRC_DIR}
fi

cd  ${TRIGGERING_BUILD_DIR}
	make
cd ${SRC_DIR}

if [ ! -d ${ACQUISITION_BUILD_DIR} ]; then
	echo Creating a build directory for the Acquisition daemon ${ACQUISITION_BUILD_DIR}
	mkdir -p ${ACQUISITION_BUILD_DIR}
	cd  ${ACQUISITION_BUILD_DIR}
	cmake ${SRC_DIR}/Acquisition  -DCMAKE_TOOLCHAIN_FILE=../../../../arm-linux-gnueabihf.cmake
	cd ${SRC_DIR}
fi

cd  ${ACQUISITION_BUILD_DIR}
	make
cd ${SRC_DIR}


#Build Firmware files
cd ${FIRMWARE_DIR}
	cmake .
	echo Building test files
	make tests >> /dev/null
	echo Building opq.bin
	make opq.bin >> /dev/null
cd ${SRC_DIR}



