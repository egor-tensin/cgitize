#!/usr/bin/env bash

set -o errexit -o nounset -o pipefail

# Honestly, I have no idea how this works, I just copy-pasted it from
# somewhere.

spawn-fcgi \
    -u nginx \
    -g nginx \
    -M 0755 \
    -F 10 \
    -s /run/fcgiwrap.sock \
    /usr/sbin/fcgiwrap

exec nginx -g 'daemon off;'
