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
	cmake  ${SRC_DIR}/Triggering
	cd ${SRC_DIR}
fi

cd  ${TRIGGERING_BUILD_DIR}
	make Triggering
cd ${SRC_DIR}

if [ ! -d ${ACQUISITION_BUILD_DIR} ]; then
	echo Creating a build directory for the Acquisition daemon ${ACQUISITION_BUILD_DIR}
	mkdir -p ${ACQUISITION_BUILD_DIR}
	cd  ${ACQUISITION_BUILD_DIR}
	cmake ${SRC_DIR}/Acquisition
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

#Create Docs Directory and Generate Documentation
if [ ! -d ${TRIGGERING_DOCS_DIR} ]; then
	echo Creating a docs directory for Triggering ${TRIGGERING_DOCS_DIR}
	mkdir -p ${TRIGGERING_DOCS_DIR}
fi

exit 0;

cd ${TRIGGERING_DOCS_DIR}
	echo Creating Doxygen Config file for Triggering
	doxygen -s -g
	echo Editing Project Name, Input Source, and Disabling Latex Output
	sed -i 's;PROJECT_NAME           = "My Project";PROJECT_NAME           = "Triggering";' Doxyfile
	sed -i 's;INPUT                  =;INPUT                  = ../../Triggering/lib;' Doxyfile
	sed -i 's;GENERATE_LATEX         = YES;GENERATE_LATEX         = NO;' Doxyfile
	echo Generating Documentation for Triggering in ${TRIGGERING_DOCS_DIR}
	doxygen Doxyfile >> /dev/null
cd ${SRC_DIR}

#Create Firmware Documentation Directory and Generate Documentation
if [ ! -d ${FIRMWARE_DOCS_DIR} ]; then
	echo Creating docs directory for Firmware ${FIRMWARE_DOCS_DIR}
	mkdir -p ${FIRMWARE_DOCS_DIR}
fi

cd ${FIRMWARE_DOCS_DIR}
	echo Creating Doxygen Config file for Firmware
	doxygen -s -g
	echo Editing Project Name, Input Source, and Disabling Latex Output
	sed -i 's;PROJECT_NAME           = "My Project";PROJECT_NAME           = "Firmware";' Doxyfile
	sed -i 's;INPUT                  =;INPUT                  = ../../../Firmware/Inc/peripheral_config.h ../../../Firmware/Inc/runtime_config.h;' Doxyfile
	sed -i 's;GENERATE_LATEX         = YES;GENERATE_LATEX         = NO;' Doxyfile
	echo Generating Documentation for Firmware in ${FIRMWARE_DOCS_DIR}
	doxygen Doxyfile >> /dev/null
cd ${SRC_DIR}


