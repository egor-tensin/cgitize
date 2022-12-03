#!/usr/bin/env bash

# Copyright (c) 2021 Egor Tensin <Egor.Tensin@gmail.com>
# This file is part of the "cgitize" project.
# For details, see https://github.com/egor-tensin/cgitize.
# Distributed under the MIT License.

set -o errexit -o nounset -o pipefail

readonly base_dir=/usr/src
readonly cfg_path=/etc/cgitize/cgitize.toml

secure_repo_dir() {
    local dir
    dir="$( /get_output_dir.py -- "$cfg_path" )"
    chmod -- o-rwx "$dir"

    # This is required so that nginx can access the directory.
    # nginx uses a fixed UID:
    # https://github.com/nginxinc/docker-nginx/blob/4785a604aa40e0b0a69047a61e28781a2b0c2069/mainline/alpine-slim/Dockerfile#L16
    chown -- :101 "$dir"
}

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
cd -- "$base_dir" &&$( printf -- ' %q' "$@" )"
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

    # Run the task once when the container is started, regardless of schedule.
    /task.sh

    local crontab
    crontab="$schedule /task.sh
# This is the new crontab."

    echo "$crontab" | crontab -
    exec crond -f
}

main() {
    secure_repo_dir
    setup_cron_task "$@"
}

main "$@"
