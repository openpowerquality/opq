#!/bin/bash
# Loads the cajipci driver
#

OPQ_KERNEL_PATH=/usr/local/opq/kernel

### BEGIN INIT INFO
# Provides:          opq_driver
# Required-Start:    $remote_fs $syslog
# Required-Stop:     $remote_fs $syslog
# Default-Start:     2 3 4 5
# Default-Stop:      0 1 6
# Short-Description: Loads and sets up opq driver.
# Description:       Enables acquisition
### END INIT INFO

case "$1" in
start)
	cd $OPQ_KERNEL_PATH; ./opq_load.sh
;;

stop)
	cd $OPQ_KERNEL_PATH; ./opq_unload.sh
;;

restart)
  	$0 stop
  	$0 start
;;

status)
              [ -f /dev/opq0 ] && echo "Driver Loaded and ready" || echo "Driver not loaded"
;;

*)
        echo "Usage: $0 {start|stop|restart|status}"
        exit 1
esac
