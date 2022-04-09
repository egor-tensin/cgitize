#!/bin/sh

set -e

# Honestly, I have no idea how this works, I just copy-pasted it from
# somewhere.

spawn-fcgi \
    -u nginx \
    -g nginx \
    -M 0755 \
    -F 10 \
    -s /run/fcgiwrap.sock \
    /usr/bin/fcgiwrap

exec nginx -g 'daemon off;'
