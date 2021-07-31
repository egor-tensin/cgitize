#!/usr/bin/env bash

set -o errexit -o nounset -o pipefail

script_dir="$( dirname -- "${BASH_SOURCE[0]}" )"
script_dir="$( cd -- "$script_dir" && pwd )"
readonly script_dir
script_name="$( basename -- "${BASH_SOURCE[0]}" )"
readonly script_name

readonly ssh_dir="$script_dir/ssh"
readonly client_key_password='password'

dump() {
    local prefix="${FUNCNAME[0]}"
    [ "${#FUNCNAME[@]}" -gt 1 ] && prefix="${FUNCNAME[1]}"

    local msg
    for msg; do
        echo "$script_name: $prefix: $msg"
    done
}

cleanup() {
    echo
    echo ----------------------------------------------------------------------
    echo Cleaning up
    echo ----------------------------------------------------------------------

    remove_ssh_keys
    kill_ssh_agent
}

generate_ssh_keys() {
    echo
    echo ----------------------------------------------------------------------
    echo Generating SSH keys
    echo ----------------------------------------------------------------------

    mkdir -p -- "$ssh_dir"

    ssh-keygen -t rsa -b 4096 -f "$ssh_dir/client_key" -N "$client_key_password"
    ssh-keygen -t rsa -b 4096 -f "$ssh_dir/server_key" -N ''
}

remove_ssh_keys() {
    rm -rf -- "$ssh_dir"
}

kill_ssh_agent() {
    [ -n "${SSH_AGENT_PID:+x}" ] || return 0
    dump "killing ssh-agent with PID $SSH_AGENT_PID"
    kill "$SSH_AGENT_PID"
}

spawn_ssh_agent() {
    [ -n "${SSH_AGENT_PID:+x}" ] && return 0
    if ! command -v ssh-agent > /dev/null 2>&1; then
        dump "could not find ssh-agent" >&2
        return 1
    fi
    local output
    output="$( ssh-agent -s )"
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

    local key="$ssh_dir/client_key"
    chmod 0600 -- "$key"

    local askpass_path
    askpass_path="$( mktemp --tmpdir="$script_dir" )"

    local askpass_rm
    askpass_rm="$( printf -- 'rm -- %q; trap - RETURN' "$askpass_path" )"
    trap "$askpass_rm" RETURN

    chmod 0700 -- "$askpass_path"

    local echo_password
    echo_password="$( printf -- 'echo %q' "$client_key_password" )"
    echo "$echo_password" > "$askpass_path"

    SSH_ASKPASS="$askpass_path" SSH_ASKPASS_REQUIRE=force DISPLAY= ssh-add "$key" > /dev/null 2>&1 < /dev/null
}

docker_build() {
    echo
    echo ----------------------------------------------------------------------
    echo Building Docker images
    echo ----------------------------------------------------------------------

    docker-compose build
}

setup() {
    generate_ssh_keys
    setup_ssh_agent
    docker_build
}

run_server() {
    echo
    echo ----------------------------------------------------------------------
    echo Running the server
    echo ----------------------------------------------------------------------

    docker-compose up -d server
}

run_client() {
    echo
    echo ----------------------------------------------------------------------
    echo Running the client
    echo ----------------------------------------------------------------------

    if [ -z "${SSH_AUTH_SOCK:+x}" ]; then
        dump 'SSH_AUTH_SOCK is not defined' >&2
        return 1
    fi
    dump "SSH_AUTH_SOCK: $SSH_AUTH_SOCK"
    docker-compose run --rm client
}

run() {
    run_server
    run_client
}

verify() {
    echo
    echo ----------------------------------------------------------------------
    echo Checking the pulled repository
    echo ----------------------------------------------------------------------

    pushd -- "$script_dir/client/output/test_repo" > /dev/null
    git log --oneline
    popd > /dev/null
}

main() {
    trap cleanup EXIT
    pushd -- "$script_dir" > /dev/null
    setup
    run
    verify
    popd > /dev/null
}

main
