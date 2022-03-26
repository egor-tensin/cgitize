#!/usr/bin/env bash

set -o errexit -o nounset -o pipefail

spawn-fcgi \
    -u nginx \
    -g nginx \
    -M 0755 \
    -F 10 \
    -s /run/fcgiwrap.sock \
    /usr/sbin/fcgiwrap

exec nginx -g 'daemon off;'
