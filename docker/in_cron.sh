#!/usr/bin/env bash

# Copyright (c) 2021 Egor Tensin <egor@tensin.name>
# This file is part of the "cgitize" project.
# For details, see https://github.com/egor-tensin/cgitize.
# Distributed under the MIT License.

set -o errexit -o nounset -o pipefail
shopt -s inherit_errexit lastpipe

schedule_to_cron() {
    local schedule
    for schedule; do
        case "$schedule" in
            minutely) echo '* * * * *'    ;;
            15min)    echo '*/15 * * * *' ;;
            hourly)   echo '0 * * * *'    ;;
            daily)    echo '0 0 * * *'    ;;
            weekly)   echo '0 0 * * 1'    ;;
            monthly)  echo '0 0 1 * *'    ;;
            *)
                echo "$schedule"
                ;;
        esac
    done
}

setup_cron_task() {
    local schedule
    schedule="${SCHEDULE:-once}"

    if [ "$schedule" = once ]; then
        exec "$@"
    fi

    schedule="$( schedule_to_cron "$schedule" )"

    if [ -n "${SCHEDULE_ON_START:+x}" ]; then
        # Run the task once when the container is started.
        "$@"
    fi

    local crontab
    crontab="$schedule"
    crontab="$crontab$( printf ' %q' "$@" )"

    echo "$crontab" | crontab -
    exec crond -f
}

main() {
    setup_cron_task "$@"
}

main "$@"
