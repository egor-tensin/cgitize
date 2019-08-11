#!/usr/bin/env bash

set -o errexit -o nounset -o pipefail

script_dir="$( dirname -- "${BASH_SOURCE[0]}" )"
script_dir="$( cd -- "$script_dir" && pwd )"
readonly script_dir

dump() {
    local prefix="${FUNCNAME[0]}"
    [ "${#FUNCNAME[@]}" -gt 1 ] && prefix="${FUNCNAME[1]}"

    local msg
    for msg; do
        echo "$prefix: $msg"
    done
}

check_ssh_agent_running() {
    if [ -z "${SSH_AUTH_SOCK+x}" ]; then
        dump "SSH_AUTH_SOCK isn't defined (ssh-agent not running?)" >&2
        return 1
    fi
}

add_ssh_key() {
    local password_path="$script_dir/password.txt"
    local password
    password="$( cat -- "$password_path" )"

    local askpass_path
    askpass_path="$( mktemp --tmpdir="$script_dir" )"

    local askpass_rm
    askpass_rm="$( printf -- 'rm -f -- %q' "$askpass_path" )"
    trap "$askpass_rm" RETURN

    chmod 0700 -- "$askpass_path"

    local echo_password
    echo_password="$( printf -- 'echo %q' "$password" )"
    echo "$echo_password" > "$askpass_path"

    local key_path="$HOME/.ssh/id_rsa"

    ssh-add -D
    DISPLAY="${DISPLAY-x}" SSH_ASKPASS="$askpass_path" ssh-add "$key_path" < /dev/null
}

main() {
    check_ssh_agent_running
    add_ssh_key
    python3 -m pull.main "$@"
}

main "$@"
