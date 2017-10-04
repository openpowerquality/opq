#!/bin/bash

if [[ $EUID -ne 0 ]]; then
    echo "This script must be run as root" 1>&2
    exit 1
fi

if [ $# -ne 2 ]; then
    echo "usage: ./opq-sign.sh [private key] [file]"
    exit 1
fi

PRIVATE_KEY=${1}
FILE=${2}

openssl dgst -binary -sha256 -sign ${PRIVATE_KEY} -out ${FILE}.bin ${FILE}
openssl base64 -in ${FILE}.bin -out ${FILE}.sig
rm ${FILE}.bin
