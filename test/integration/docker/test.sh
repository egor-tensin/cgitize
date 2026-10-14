#!/usr/bin/env bash

set -o errexit -o nounset -o pipefail
shopt -s inherit_errexit lastpipe

script_dir="$( dirname -- "${BASH_SOURCE[0]}" )"
script_dir="$( cd -- "$script_dir" && pwd )"
readonly script_dir
script_name="$( basename -- "${BASH_SOURCE[0]}" )"
readonly script_name

# This is still required with older Compose versions to use TARGETARCH:
export DOCKER_BUILDKIT=1

readonly output_dir="$script_dir/output"
readonly frontend_host=127.0.0.1

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

docker_build() {
    echo
    echo ----------------------------------------------------------------------
    echo Building Docker images
    echo ----------------------------------------------------------------------

    docker compose --progress plain build
}

docker_cleanup() {
    dump 'cleaning up Docker data'
    docker compose down --rmi all --volumes
    # Use `docker system prune` as well?
}

setup() {
    docker_build
}

run_git_server() {
    echo
    echo ----------------------------------------------------------------------
    echo Running the Git server
    echo ----------------------------------------------------------------------

    docker compose up -d git_server
}

run_cgitize() {
    echo
    echo ----------------------------------------------------------------------
    echo Running cgitize
    echo ----------------------------------------------------------------------

    docker compose run --rm cgitize
}

run_frontend() {
    echo
    echo ----------------------------------------------------------------------
    echo Running the frontend
    echo ----------------------------------------------------------------------

    docker compose up -d frontend
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

    pushd -- "$script_dir/output/test_repo.git" > /dev/null
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
