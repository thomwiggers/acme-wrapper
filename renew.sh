#!/bin/bash
set -e

if [ "$1" == "" ]; then
    echo "You need to specify the domain"
    exit 1
fi

DIR=/etc/letsencrypt-certs/$1
ACMEDIR=/var/www/letsencrypt
ACMEPATH=${0%/*}

openssl x509 -noout -in $DIR/certificate.crt -checkend 846000 && exit || true
echo "RENEWING $1"
>&2 echo "RENEWING $1"
date
python $ACMEPATH/acme-tiny/acme_tiny.py --account-key $ACMEPATH/account.key --csr $DIR/request.csr --acme-dir /var/www/letsencrypt > $DIR/certificate.crt || exit
cat $DIR/certificate.crt $DIR/../intermediate.pem > $DIR/chained.pem
systemctl reload nginx
