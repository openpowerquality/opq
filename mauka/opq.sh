#!/bin/bash
### BEGIN INIT INFO
# Provides:          opqmauka_service
# Required-Start:    $remote_fs $network $time $syslog
# Required-Stop:     $remote_fs $network $time $syslog
# Default-Start:     2 3 4 5
# Default-Stop:      0 1 6
# Description:       opqmauka_service = Start opqmauka services (mongod, opqmauka, opqmauka broker)
### END INIT INFO

PATH=/sbin:/usr/sbin:/bin:/usr/bin:/usr/local/bin
NAME=mongod_service
RUN_DIR=/var/run

#Paths to service binaries
MONGOD_SERVICE=/usr/local/bin/mongod
MONGOD_ARGS="--config /etc/mongod/mongod.conf"

MAUKA_SERVICE=/usr/bin/python3
MAUKA_SCRIPT=/usr/local/bin/opq/OpqMauka/OpqMauka.py
MAUKA_CONFIG=/etc/opq/opqmauka.config.json
MAUKA_ARGS="${MAUKA_SCRIPT} ${MAUKA_CONFIG}"

MAUKA_BROKER_SERVICE=/usr/local/bin/opq/Mauka_broker
MAUKA_BROKER_CONFIG=/etc/opq/opqmauka.broker.config.json
MAUKA_BROKER_ARGS=${MAUKA_BROKER_CONFIG}

#Paths to PID
MONGOD_PIDFILE=${RUN_DIR}/mongod.pid
MAUKA_PIDFILE=${RUN_DIR}/OpqMauka.pid
MAUKA_BROKER_PIDFILE=${RUN_DIR}/OpqMaukaBroker.pid

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
    #Starts opqwifi as root, if not already running
    echo "Starting mongod"
    start-stop-daemon --start --quiet --background --pidfile ${MONGOD_PIDFILE} --make-pidfile --user ${USER} --chuid ${USER} --startas ${MONGOD_SERVICE} -- ${MONGOD_ARGS}

    echo "Starting OpqMauka Broker"
    start-stop-daemon --start --quiet --background --pidfile ${MAUKA_BROKER_PIDFILE} --make-pidfile --user ${USER} --chuid ${USER} --startas ${MAUKA_BROKER_SERVICE} -- ${MAUKA_BROKER_ARGS}

    echo "Starting OpqMauka"
    start-stop-daemon --start --quiet --background --pidfile ${MAUKA_PIDFILE} --make-pidfile --user ${USER} --chuid ${USER} --startas ${MAUKA_SERVICE} -- ${MAUKA_ARGS}

    log_end_msg $?
}

#
# Function that stops the services
#
do_stop()
{
    log_daemon_msg "Stopping ${NAME}..."
    start-stop-daemon --stop --pidfile ${MONGOD_PIDFILE} --quiet --retry 10
    start-stop-daemon --stop --pidfile ${MAUKA_BROKER_PIDFILE} --quiet --retry 10
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
