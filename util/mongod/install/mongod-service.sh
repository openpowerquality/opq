#!/bin/bash
### BEGIN INIT INFO
# Provides:          mongod
# Required-Start:    $remote_fs $network $time $syslog
# Required-Stop:     $remote_fs $network $time $syslog
# Default-Start:     2 3 4 5
# Default-Stop:      0 1 6
# Description:       Runs mongod with three replica sets
### END INIT INFO

PATH=/sbin:/usr/sbin:/bin:/usr/bin:/usr/local/bin
NAME=mongod
RUN_DIR=/var/run

#Paths to service binaries
MONGOD_SERVICE=/bin/bash
MONGOD_SCRIPT=/usr/local/bin/mongodb/start-mongod.sh
MONGOD_LOG=/var/log/mongodb/mongod-service.log

#Paths to PID
MONGOD_PIDFILE=${RUN_DIR}/mongod.pid

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

    echo "Starting mongod"
    start-stop-daemon --start --quiet --background --pidfile ${MONGOD_PIDFILE} --make-pidfile --user ${USER} --chuid ${USER} --startas ${MONGOD_SERVICE} --no-close  -- ${MONGOD_SCRIPT} >> ${MONGOD_LOG} 2>&1

    log_end_msg $?
}

#
# Function that stops the services
#
do_stop()
{
    log_daemon_msg "Stopping ${NAME}..."
    start-stop-daemon --stop --pidfile ${MONGOD_PIDFILE} --quiet --retry 10
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
