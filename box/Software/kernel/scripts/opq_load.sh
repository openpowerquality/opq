#!/bin/bash
export module="opq_chardev"
export device="opq"
export mode="777"
export group="opquser"

# invoke insmod with all arguments we got
# and use a pathname, as insmod doesn't look in . by default
/sbin/rmmod $device &> /dev/null 
/sbin/insmod ${device}.ko $* || exit 1

# retrieve major number
major=$(awk -v MODULE=$module '$2==MODULE {print $1;}' /proc/devices)
echo $major
# Remove stale nodes and replace them, then give gid and perms
# Usually the script is shorter, it's scull that has several devices in it.

rm -f /dev/${device}0
mknod /dev/${device}0 c $major 0
chgrp $group /dev/${device}0
chmod $mode  /dev/${device}0
