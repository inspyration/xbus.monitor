#!/bin/sh

auth_host=$1
auth_port=$2
pyramid_host=$3
pyramid_port=$4

if [ ! -d out ]; then
    mkdir out
else
    rm -f out/*
fi

openssl genrsa -out out/privkey.pem 2048
openssl req -new -x509 -key out/privkey.pem -out data/cacert.pem -days 1095
openssl dhparam -outform PEM -out data/dhparam.pem 1024

cd data

python gen_metadata_xml.py $pyramid_host:$pyramid_port

cd -

rm -f data/*.pem

wget $auth_host:$auth_port/idp/saml2/metadata -nv -O out/idp_meta.xml
