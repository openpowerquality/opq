#!/bin/bash
export device="opq"

# invoke insmod with all arguments we got
# and use a pathname, as insmod doesn't look in . by default
/sbin/rmmod $device &> /dev/null 


rm -f /dev/${device}0
