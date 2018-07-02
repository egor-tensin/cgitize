#!/usr/bin/env bash

set -o errexit -o nounset -o pipefail

script_dir="$( dirname -- "${BASH_SOURCE[0]}" )"
script_dir="$( cd -- "$script_dir" && pwd )"
readonly script_dir

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

if [ -z "${SSH_AUTH_SOCK+x}" ]; then
    echo "SSH_AUTH_SOCK isn't defined (ssh-agent not running?)" >&2
    exit 1
fi
add_ssh_key
"$script_dir/pull.py"
