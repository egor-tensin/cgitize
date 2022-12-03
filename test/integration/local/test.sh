#!/usr/bin/env bash

set -o errexit -o nounset -o pipefail
shopt -s inherit_errexit lastpipe

script_dir="$( dirname -- "${BASH_SOURCE[0]}" )"
script_dir="$( cd -- "$script_dir" && pwd )"
readonly script_dir

upstream_repo_dir=
readonly etc_dir="$script_dir/etc"
readonly cgitize_toml_path="$etc_dir/cgitize.toml"
readonly output_dir="$script_dir/output"

success() {
    echo
    echo ----------------------------------------------------------------------
    echo "SUCCESS: ${FUNCNAME[1]}"
    echo ----------------------------------------------------------------------
}

cleanup() {
    echo
    echo ----------------------------------------------------------------------
    echo Cleaning up
    echo ----------------------------------------------------------------------

    echo "Removing upstream repository directory: $upstream_repo_dir"
    rm -rf -- "$upstream_repo_dir"
    echo "Removing etc directory: $etc_dir"
    rm -rf -- "$etc_dir"
    echo "Removing output directory: $output_dir"
    rm -rf -- "$output_dir"
}

setup_upstream_repo() {
    echo
    echo ----------------------------------------------------------------------
    echo Setting up upstream repository
    echo ----------------------------------------------------------------------

    upstream_repo_dir="$( mktemp -d )"
    pushd -- "$upstream_repo_dir" > /dev/null

    git init
    echo '1' > 1.txt
    git add .
    git commit -m 'first commit'
    echo '2' > 2.txt
    git add .
    git commit -m 'second commit'

    popd > /dev/null
}

add_commits() {
    echo
    echo ----------------------------------------------------------------------
    echo Adding new commits
    echo ----------------------------------------------------------------------

    pushd -- "$upstream_repo_dir" > /dev/null

    echo '3' > 3.txt
    git add .
    git commit -m 'third commit'

    popd > /dev/null
}

setup_cgitize_toml() {
    echo
    echo ----------------------------------------------------------------------
    echo cgitize.toml
    echo ----------------------------------------------------------------------

    local conf_dir
    conf_dir="$( dirname -- "$cgitize_toml_path" )"
    mkdir -p -- "$conf_dir"

    cat <<EOF | tee "$cgitize_toml_path"
output_dir = "$output_dir"

[repositories.test_repo]
name = "test_repo"
clone_url = "$upstream_repo_dir"
EOF
}

setup_cgitize() {
    setup_cgitize_toml
}

setup_bare() {
    setup_upstream_repo
    setup_cgitize
}

setup_workdir() {
    setup_bare

    echo
    echo ----------------------------------------------------------------------
    echo Setting up local repository clone
    echo ----------------------------------------------------------------------

    mkdir -p -- "$output_dir"
    git clone --quiet -- "$upstream_repo_dir" "$output_dir/test_repo"
}

cgitize() {
    echo
    echo ----------------------------------------------------------------------
    echo Running cgitize
    echo ----------------------------------------------------------------------

    python3 -m cgitize.main --config "$cgitize_toml_path" --verbose
}

check_contains() {
    if [ "$#" -lt 1 ]; then
        echo "usage: ${FUNCNAME[0]} TEST_STRING [PATTERN...]" >&2
        return 1
    fi

    local test_string="$1"
    shift

    local pattern
    for pattern; do
        # Be careful to _not_ use grep -q, since this fucks stuff up:
        # https://mywiki.wooledge.org/BashPitfalls#pipefail.
        if ! echo "$test_string" | grep --fixed-strings -- "$pattern" > /dev/null; then
            echo "${FUNCNAME[0]}: couldn't find the following pattern: $pattern" >&2
            return 1
        fi
    done
}

verify_commits() {
    # This is fucking stupid, but otherwise stuff like `if verify_commits;`
    # doesn't work: https://stackoverflow.com/q/4072984/514684
    # TODO: figure this out?
    pushd -- "$output_dir" > /dev/null &&
        cd -- test_repo.git &&
        local output &&
        output="$( git log --oneline )" &&
        echo "$output" &&
        check_contains "$output" "$@" &&
        popd > /dev/null
}

verify_initial_commits() {
    echo
    echo ----------------------------------------------------------------------
    echo Checking the initial commits
    echo ----------------------------------------------------------------------

    verify_commits 'first commit' 'second commit'
}

verify_added_commits() {
    echo
    echo ----------------------------------------------------------------------
    echo Checking the added commits
    echo ----------------------------------------------------------------------

    verify_commits 'first commit' 'second commit' 'third commit'
}

test_bare() {
    echo
    echo ======================================================================
    echo "${FUNCNAME[0]}"
    echo ======================================================================

    setup_bare
    cgitize
    verify_initial_commits
    add_commits
    cgitize
    verify_added_commits
    cleanup
    success
}

test_workdir() {
    echo
    echo ======================================================================
    echo "${FUNCNAME[0]}"
    echo ======================================================================

    setup_workdir
    cgitize
    verify_initial_commits
    add_commits
    cgitize
    verify_added_commits
    cleanup
    success
}

test_failure() {
    echo
    echo ======================================================================
    echo "${FUNCNAME[0]}"
    echo ======================================================================

    setup_bare
    cgitize
    verify_initial_commits
    add_commits

    echo
    echo ----------------------------------------------------------------------
    echo Removing upstream repository
    echo ----------------------------------------------------------------------
    rm -rf -- "$upstream_repo_dir"

    if cgitize; then
        echo "cgitize should have failed to pull the upstream repository." >&2
        return 1
    fi
    verify_initial_commits
    if verify_added_commits; then
        echo "The added commits should not have been pulled." >&2
        return 1
    fi
    cleanup
    success
}

main() {
    trap cleanup EXIT
    test_bare
    test_workdir
    test_failure
}

main
