#!/usr/bin/env bash

# Copyright (c) 2021 Egor Tensin <Egor.Tensin@gmail.com>
# This file is part of the "cgitize" project.
# For details, see https://github.com/egor-tensin/cgitize.
# Distributed under the MIT License.

set -o errexit -o nounset -o pipefail

schedule="${SCHEDULE:-once}"

case "$schedule" in
    once)    exec "$@" ;;
    15min)   schedule='*/15 * * * *' ;;
    hourly)  schedule='0 * * * *'    ;;
    daily)   schedule='0 0 * * *'    ;;
    weekly)  schedule='0 0 * * 1'    ;;
    monthly) schedule='0 0 1 * *'    ;;
    *) ;;
esac

script="#!/bin/bash
cd /usr/src &&$( printf -- ' %q' "$@" )"

echo "$script" > /task.sh
chmod +x /task.sh

crontab="$schedule /task.sh
# This is the new crontab."

echo "$crontab" | crontab -

crond -f
