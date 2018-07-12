#!/bin/bash
### BEGIN INIT INFO
# Provides:          mauka
# Required-Start:    $remote_fs $network $time $syslog
# Required-Stop:     $remote_fs $network $time $syslog
# Default-Start:     2 3 4 5
# Default-Stop:      0 1 6
# Description:       mauka = Start mauka
### END INIT INFO

PATH=/sbin:/usr/sbin:/bin:/usr/bin:/usr/local/bin
NAME=mauka
RUN_DIR=/var/run

#Paths to service binaries
MAUKA_SERVICE=/usr/local/bin/python3
MAUKA_SCRIPT=/usr/local/bin/opq/mauka/opq_mauka.py
MAUKA_CONFIG=/etc/opq/mauka/config.json
MAUKA_ARGS="${MAUKA_SCRIPT} ${MAUKA_CONFIG}"
MAUKA_LOG=/var/log/opq/mauka.log


#Paths to PID
MAUKA_PIDFILE=${RUN_DIR}/OpqMauka.pid

USER=opq



# Load the VERBOSE setting and other rcS variables
. /lib/init/vars.sh

# Define LSB log_* functions.
# Depend on lsb-base (>= 3.2-14) to ensure that this file is present
# and status_of_proc is working.
. /lib/lsb/init-functions

#
# Function that starts the services
#
do_start()
{
    log_daemon_msg "Starting ${NAME}..."

    echo "Starting OpqMauka"
    start-stop-daemon --start --quiet --background --pidfile ${MAUKA_PIDFILE} --make-pidfile --user ${USER} --chuid ${USER} --startas ${MAUKA_SERVICE} --no-close  -- ${MAUKA_ARGS} >> ${MAUKA_LOG} 2>&1

    log_end_msg $?
}

#
# Function that stops the services
#
do_stop()
{
    log_daemon_msg "Stopping ${NAME}..."
    start-stop-daemon --stop --pidfile ${MAUKA_PIDFILE} --quiet --retry 10
    log_end_msg $?
}


case "$1" in
    start|stop)
        do_${1}
        ;;

    restart)
        do_stop
        do_start
        ;;

    *)
        echo "Usage: $0 {start|stop|restart}"

esac
