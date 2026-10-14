# Copyright (c) 2026 Egor Tensin <egor@tensin.name>
# This file is part of the "cgitize" project.
# For details, see https://github.com/egor-tensin/cgitize
# Distributed under the MIT License.

export GIT_CONFIG_NOSYSTEM=true
#export GIT_CONFIG_GLOBAL=/dev/null

test_run_cgitize() {
    local cmd=(python3 -m cgitize.main --config "$test_config_path" "$@")
    log_run "${cmd[@]}"
    PYTHONPATH="$tests_dir/../.." "${cmd[@]}"
}

test_verify_repos() {
    local repo
    for repo; do
        log "Verifying repository: $repo..."

        local repo_dir
        repo_dir="$test_output_dir/$repo.git"
        GIT_DIR="$repo_dir" git rev-parse HEAD > /dev/null
        log 'HEAD is fine.'

        if test -s "$repo_dir/info/web/last-modified"; then
            log 'last-modified is fine.'
        else
            fail 'last-modified is missing!'
            return 1
        fi
    done
}

test_verify_no_repos() {
    local repo
    for repo; do
        log "Verifying repository doesn't exist: $repo"

        local repo_dir
        repo_dir="$test_output_dir/$repo.git"

        if [ -e "$repo_dir" ]; then
            fail "Exists, but it shouldn't"
            return 1
        fi
    done
}

test_verify_origin() {
    if [ "$#" -ne 2 ]; then
        log "usage: ${FUNCNAME[0]} REPO URL"
        return 1
    fi

    local repo="$1"
    local expected="$2"

    log "Verifying origin for $repo..."

    local repo_dir
    repo_dir="$test_output_dir/$repo.git"

    local actual
    actual="$( GIT_DIR="$repo_dir" git config --get remote.origin.url )"

    if [ "$expected" != "$actual" ]; then
        fail "Origin doesn't match!"
        fail_details "Expected: $expected"
        fail_details "Actual:   $actual"
        return 1
    fi
}

test_verify_error_header_empty() {
    log 'Verifying the error header...'
    if [ -s "$test_output_dir/error.html" ]; then
        fail "The error header should be empty"
        return 1
    fi
}

test_verify_error_header() {
    log 'Verifying the error header...'

    local msg="Some repositories couldn't be updated"

    if ! grep -F -- "$msg" "$test_output_dir/error.html" > /dev/null; then
        fail "The error header doesn't contain the required error"
        fail_details "Expected error: $msg"
        return 1
    fi
}
