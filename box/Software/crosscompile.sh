#!/usr/bin/env bash
TRIGGERING_BUILD_DIR="./Triggering/build/"
SRC_DIR=$(pwd)

#Building kernel files
cd kernel
	echo Building kernel driver.
	make -C ../../../../../kernel/linux/ CROSS_COMPILE=/home/tusk/vc/build-raspbian-image/kernel/tools/arm-bcm2708/arm-rpi-4.9.3-linux-gnueabihf/bin/arm-linux-gnueabihf- ARCH=arm M=$PWD modules
cd ${SRC_DIR}

#Build protocol files
mkdir -p Triggering/proto
protoc -I ${PROTOCOL_DIR} --cpp_out=Triggering/proto ${PROTOCOL_DIR}${PROTOCOL_FILE}

#build triggering
rm -rf ${TRIGGERING_BUILD_DIR}

if [ ! -d ${TRIGGERING_BUILD_DIR} ]; then
	echo Creating a build directory for the Triggering daemon ${TRIGGERING_BUILD_DIR}
	mkdir -p ${TRIGGERING_BUILD_DIR}
	cd  ${TRIGGERING_BUILD_DIR}
	cmake  ${SRC_DIR}/Triggering -DCMAKE_TOOLCHAIN_FILE=../../../../../arm-linux-gnueabihf.cmake 
	cd ${SRC_DIR}
fi

cd  ${TRIGGERING_BUILD_DIR}
	make -j8
cd ${SRC_DIR}
