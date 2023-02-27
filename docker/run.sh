#!/usr/bin/env bash

# Copyright (c) 2023 Egor Tensin <Egor.Tensin@gmail.com>
# This file is part of the "cgitize" project.
# For details, see https://github.com/egor-tensin/cgitize.
# Distributed under the MIT License.

set -o errexit -o nounset -o pipefail
shopt -s inherit_errexit lastpipe

script_dir="$( dirname -- "${BASH_SOURCE[0]}" )"
script_dir="$( cd -- "$script_dir" && pwd )"
readonly script_dir

readonly src_dir=/usr/src
readonly cfg_path=/etc/cgitize/cgitize.toml

secure_repo_dir() {
    local dir
    dir="$( "$script_dir/get_output_dir.py" -- "$cfg_path" )"

    chmod -- o-rwx "$dir"

    # This is required so that nginx can access the directory.
    # nginx uses a fixed UID:
    # https://github.com/nginxinc/docker-nginx/blob/4785a604aa40e0b0a69047a61e28781a2b0c2069/mainline/alpine-slim/Dockerfile#L16
    chown -- :101 "$dir"
}

setup() {
    secure_repo_dir
}

run() {
    cd -- "$src_dir"
    exec python3 -m cgitize.main "$@"
}

main() {
    setup
    run "$@"
}

main "$@"
