#!/usr/bin/env bash

set -o errexit -o nounset -o pipefail
shopt -s inherit_errexit lastpipe

script_name="$( basename -- "${BASH_SOURCE[0]}" )"
readonly script_name

dump() {
    local prefix="${FUNCNAME[0]}"
    [ "${#FUNCNAME[@]}" -gt 1 ] && prefix="${FUNCNAME[1]}"

    local msg
    for msg; do
        echo "$script_name: $prefix: $msg"
    done
}

readonly ssh_dir=/ssh
readonly ssh_client_key="$ssh_dir/client_key"
readonly ssh_client_password='password'

spawn_ssh_agent() {
    if ! command -v ssh-agent > /dev/null 2>&1; then
        dump "could not find ssh-agent" >&2
        return 1
    fi

    local output
    output="$( ssh-agent -s -a "$ssh_dir/agent.sock" )"

    echo "$output"
    eval "$output"

    if [ -z "${SSH_AGENT_PID:+x}" ]; then
        dump "could not start ssh-agent" >&2
        return 1
    fi
}

setup_ssh_agent() {
    echo
    echo ----------------------------------------------------------------------
    echo Setting up ssh-agent
    echo ----------------------------------------------------------------------

    spawn_ssh_agent

    local askpass_path
    askpass_path="$( mktemp )"
    chmod 0700 -- "$askpass_path"

    echo "#!/usr/bin/env sh" >> "$askpass_path"
    printf -- 'echo %q' "$ssh_client_password" >> "$askpass_path"

    SSH_ASKPASS="$askpass_path" SSH_ASKPASS_REQUIRE=force DISPLAY= ssh-add "$ssh_client_key" < /dev/null
}

main() {
    setup_ssh_agent
    exec "$@"
}

main "$@"
