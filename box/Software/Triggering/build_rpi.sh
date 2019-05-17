#!/bin/bash

export CFLAGS="-I${PWD}/sysroot/include"
export CPPFLAGS="-I${PWD}/sysroot/include"
export LDFLAGS="-L${PWD}/sysroot/lib/"
if [ ! -d "./sysroot" ]; then
	rm -rf zeromq-*
	mkdir sysroot

	wget https://github.com/jedisct1/libsodium/releases/download/1.0.17/libsodium-1.0.17.tar.gz
	tar xzvf libsodium-1.0.17.tar.gz
	cd libsodium-1.0.17
	./configure --host=arm-linux-gnueabihf CC=arm-linux-gnueabihf-g++ CXX=arm-linux-gnueabihf-g++ --prefix ${PWD}/../sysroot 
	make -j 8 
	make install
	cd ..
	rm -r libsodium*
	wget https://github.com/zeromq/libzmq/releases/download/v4.3.1/zeromq-4.3.1.tar.gz
	tar xzvf zeromq-4.3.1.tar.gz
	cd zeromq-4.3.1
	./configure --host=arm-linux-gnueabihf CC=arm-linux-gnueabihf-g++ CXX=arm-linux-gnueabihf-g++ --prefix ${PWD}/../sysroot -with-libsodium=yes
	make -j 8
	make install
	cd ..
	rm -rf zeromq-4.3.*
fi

export PKG_CONFIG_PATH="sysroot/lib/pkgconfig/"
export PKG_CONFIG_ALLOW_CROSS=true
#export PKG_CONFIG_ALL_STATIC=true
export RUSTFLAGS="-L${PWD}/sysroot/lib/ -L/usr/local/arm-bcm2708/arm-linux-gnueabihf/arm-linux-gnueabihf/sysroot/usr/lib -L/usr/local/arm-bcm2708/arm-linux-gnueabihf/arm-linux-gnueabihf/sysroot/lib/ -lsodium -lc"
echo $RUSTFLAGS

cargo build --target=arm-unknown-linux-gnueabihf --release
