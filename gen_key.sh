#!/bin/bash

# Put all the public and private key inside target folder
target=".keys"

if [ ! -d ${target} ]; then
    mkdir ${target};
fi

openssl genrsa -out ${target}/private.pem 2048
openssl rsa -in ${target}/private.pem -outform PEM -pubout -out ${target}/public.pem