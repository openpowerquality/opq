obj-m  += opq.o
opq-objs := opq_main.o

all:
	make -C /lib/modules/$(shell uname -r)/build M=$(PWD) modules

clean:
	make -C /lib/modules/$(shell uname -r)/build M=$(PWD) clean
	rm -f opq.dtbo

opq.dtbo: opq.dts
	    dtc -@ -I dts -O dtb -o opq.dtbo opq.dts

install: opq.ko opq.dtbo
	#root folder
	mkdir -p /usr/local/opq/kernel
	#driver
	cp opq.ko /usr/local/opq/kernel
	#load unload scripts
	cp scripts/opq_load.sh /usr/local/opq/kernel
	chmod +x /usr/local/opq/kernel/opq_load.sh
	cp scripts/opq_unload.sh /usr/local/opq/kernel
	chmod +x /usr/local/opq/kernel/opq_unload.sh
	#init scripts
	cp scripts/init_opq_driver.sh /etc/init.d/opq_driver
	chmod +x /etc/init.d/opq_driver
	sudo update-rc.d opq_driver defaults
	sudo update-rc.d opq_driver enable
	#define device tree overay
	cp opq.dtbo /boot/overlays/
	cp scripts/config.txt /boot
