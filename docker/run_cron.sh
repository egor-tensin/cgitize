#!/usr/bin/env bash

# Copyright (c) 2021 Egor Tensin <Egor.Tensin@gmail.com>
# This file is part of the "cgitize" project.
# For details, see https://github.com/egor-tensin/cgitize.
# Distributed under the MIT License.

set -o errexit -o nounset -o pipefail
shopt -s inherit_errexit lastpipe

schedule_to_cron() {
    local schedule
    for schedule; do
        case "$schedule" in
            15min)   echo '*/15 * * * *' ;;
            hourly)  echo '0 * * * *'    ;;
            daily)   echo '0 0 * * *'    ;;
            weekly)  echo '0 0 * * 1'    ;;
            monthly) echo '0 0 1 * *'    ;;
            *)
                echo "$schedule"
                ;;
        esac
    done
}

make_task_script() {
    echo "#!/bin/bash
cd -- "$( pwd )" && $( printf -- ' %q' "$@" )"
}

setup_cron_task() {
    local schedule
    schedule="${SCHEDULE:-once}"

    if [ "$schedule" = once ]; then
        exec "$@"
    fi

    schedule="$( schedule_to_cron "$schedule" )"

    make_task_script "$@" > /task.sh
    chmod +x /task.sh

    if [ -n "$SCHEDULE_ON_START" ]; then
        # Run the task once when the container is started.
        /task.sh
    fi

    local crontab
    crontab="$schedule /task.sh
# This is the new crontab."

    echo "$crontab" | crontab -
    exec crond -f
}

main() {
    setup_cron_task "$@"
}

main "$@"
