#!/bin/bash

if [[ $EUID -ne 0 ]]; then
    echo "This script must be run as root" 1>&2
    exit 1
fi

if [ $# -ne 3 ]; then
    echo "usage: ./opq-sign.sh [public key] [file] [signature]"
    exit 1
fi

PUBLIC_KEY=${1}
FILE=${2}
SIGNATURE=${3}

openssl base64 -d -in ${SIGNATURE} -out ${SIGNATURE}.bin
openssl dgst -sha256 -verify ${PUBLIC_KEY} -signature ${SIGNATURE}.bin ${FILE}
rm ${SIGNATURE}.bin


