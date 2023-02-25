#!/usr/bin/env bash

set -o errexit -o nounset -o pipefail
shopt -s inherit_errexit lastpipe

script_dir="$( dirname -- "${BASH_SOURCE[0]}" )"
script_dir="$( cd -- "$script_dir" && pwd )"
readonly script_dir
script_name="$( basename -- "${BASH_SOURCE[0]}" )"
readonly script_name

readonly ssh_dir="$script_dir/ssh"
readonly client_key_password='password'
readonly output_dir="$script_dir/cgitize/output"
readonly frontend_host=localhost

dump() {
    local prefix="${FUNCNAME[0]}"
    [ "${#FUNCNAME[@]}" -gt 1 ] && prefix="${FUNCNAME[1]}"

    local msg
    for msg; do
        echo "$script_name: $prefix: $msg"
    done
}

success() {
    echo
    echo ----------------------------------------------------------------------
    echo SUCCESS
    echo ----------------------------------------------------------------------
}

cleanup() {
    echo
    echo ----------------------------------------------------------------------
    echo Cleaning up
    echo ----------------------------------------------------------------------

    remove_ssh_keys
    kill_ssh_agent
    docker_cleanup

    rm -rf -- "$output_dir"
    popd > /dev/null
}

_curl() {
    local -a opts=(curl -sS --connect-timeout 5)
    opts+=("$@")

    printf -- '%q ' ${opts[@]+"${opts[@]}"} >&2
    printf '\n' >&2

    ${opts[@]+"${opts[@]}"}
}

curl_document() {
    _curl -L "$@"
}

curl_status_code() {
    _curl -o /dev/null -w '%{http_code}\n' "$@"
}

curl_check_code() {
    if [ "$#" -lt 1 ]; then
        echo "usage: ${FUNCNAME[0]} EXPECTED [CURL_ARG...]" >&2
        return 1
    fi

    local expected
    expected="$1"
    shift

    local actual
    actual="$( curl_status_code "$@" )"

    if [ "$expected" != "$actual" ]; then
        echo "Expected code: $expected, actual code: $actual" >&2
        return 1
    fi
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

    docker-compose build --progress plain
}

docker_cleanup() {
    dump 'cleaning up Docker data'
    docker-compose down --rmi all --volumes
    # Use `docker system prune` as well?
}

setup() {
    generate_ssh_keys
    setup_ssh_agent
    docker_build
}

run_git_server() {
    echo
    echo ----------------------------------------------------------------------
    echo Running the Git server
    echo ----------------------------------------------------------------------

    docker-compose up -d git_server
}

run_cgitize() {
    echo
    echo ----------------------------------------------------------------------
    echo Running cgitize
    echo ----------------------------------------------------------------------

    if [ -z "${SSH_AUTH_SOCK:+x}" ]; then
        dump 'SSH_AUTH_SOCK is not defined' >&2
        return 1
    fi
    dump "SSH_AUTH_SOCK: $SSH_AUTH_SOCK"
    docker-compose run --rm cgitize
}

run_frontend() {
    echo
    echo ----------------------------------------------------------------------
    echo Running the frontend
    echo ----------------------------------------------------------------------

    docker-compose up -d frontend
    sleep 2
}

run() {
    run_git_server
    run_cgitize
    run_frontend
}

verify_git() {
    echo
    echo ----------------------------------------------------------------------
    echo Checking the pulled repository
    echo ----------------------------------------------------------------------

    pushd -- "$script_dir/cgitize/output/test_repo.git" > /dev/null
    git log --oneline
    popd > /dev/null
}

verify_frontend() {
    echo
    echo ----------------------------------------------------------------------
    echo Checking the frontend
    echo ----------------------------------------------------------------------

    local output

    output="$( curl_document "http://$frontend_host/test_repo/" )"
    echo "$output" | grep -o -F -- "<meta name='generator' content='cgit "

    curl_check_code 200 "http://$frontend_host/test_repo/"
    curl_check_code 200 "http://$frontend_host/test_repo/tree/"
}

verify() {
    verify_git
    verify_frontend
}

main() {
    pushd -- "$script_dir" > /dev/null
    trap cleanup EXIT
    setup
    run
    verify
    success
}

main
