#!/bin/sh

if [-z "$TOR_PASSWORD"]; then
    echo "Can't start daemon without a proper password"
    exit 1

fi
HASH=$(tor --hash-password "$TOR_PASSWORD" | tail -n 1)
echo "HashedControlPassword $HASH" >> /etc/tor/torrc

exec tor -f /etc/tor/torrc