#!/usr/bin/env bash

set -o errexit -o nounset -o pipefail
shopt -s inherit_errexit lastpipe

script_dir="$( dirname -- "${BASH_SOURCE[0]}" )"
script_dir="$( cd -- "$script_dir" && pwd )"
readonly script_dir

readonly cgitize_toml_path="$script_dir/../../../examples/cgitize.toml"
readonly output_dir='/tmp/cgitize'

success() {
    echo
    echo ----------------------------------------------------------------------
    echo "SUCCESS: ${FUNCNAME[1]}"
    echo ----------------------------------------------------------------------
}

clone_via_ssh_true() {
    sed -i -E -e 's/^clone_via_ssh = (true|false)$/clone_via_ssh = true/' -- "$cgitize_toml_path"
}

clone_via_ssh_false() {
    sed -i -E -e 's/^clone_via_ssh = (true|false)$/clone_via_ssh = false/' -- "$cgitize_toml_path"
}

cleanup() {
    echo
    echo ----------------------------------------------------------------------
    echo Cleaning up
    echo ----------------------------------------------------------------------

    echo "Removing output directory: $output_dir"
    rm -rf -- "$output_dir"
    echo "Reverting clone_via_ssh settings: $cgitize_toml_path"
    clone_via_ssh_false
}

cgitize() {
    echo
    echo ----------------------------------------------------------------------
    echo Running cgitize
    echo ----------------------------------------------------------------------

    python3 -m cgitize.main --config "$cgitize_toml_path" "$@"
}

setup_ssh() {
    clone_via_ssh_true
}

setup_https() {
    clone_via_ssh_false
}

verify_origin() {
    if [ "$#" -ne 2 ]; then
        echo "usage: ${FUNCNAME[0]} REPO URL" >&2
        return 1
    fi

    local repo="$1"
    local expected="$2"

    echo
    echo ----------------------------------------------------------------------
    echo "Verifying origin: $repo"
    echo ----------------------------------------------------------------------

    local repo_dir="$output_dir/$repo.git"

    local actual
    actual="$( GIT_DIR="$repo_dir" git config --get remote.origin.url )"

    if [ "$expected" = "$actual" ]; then
        echo 'It matches.'
    else
        echo "It doesn't match!"
        echo "    Expected: $expected"
        echo "    Actual:   $actual"
        return 1
    fi
}

verify_repos() {
    local repo
    for repo; do
        echo
        echo ----------------------------------------------------------------------
        echo "Verifying repository: $repo"
        echo ----------------------------------------------------------------------

        local repo_dir="$output_dir/$repo.git"
        GIT_DIR="$repo_dir" git rev-parse HEAD > /dev/null
        echo 'HEAD is fine.'

        if test -f "$repo_dir/info/web/last-modified"; then
            echo 'last-modified is fine.'
        else
            echo 'last-modified is missing!'
            return 1
        fi
    done
}

verify_no_repos() {
    local repo
    for repo; do
        echo
        echo ----------------------------------------------------------------------
        echo "Verifying repository doesn't exist: $repo"
        echo ----------------------------------------------------------------------

        local repo_dir="$output_dir/$repo.git"
        if [ -e "$repo_dir" ]; then
            echo "Exists, but it shouldn't."
            return 1
        fi
    done
}

test_ssh() {
    echo
    echo ======================================================================
    echo "${FUNCNAME[0]}"
    echo ======================================================================

    setup_ssh
    cgitize
    verify_repos \
        lens \
        chromiumembedded/cef \
        inkscape \
        wireguard/wintun \
        browserify-dir/browserify \
        github-dir/cgitize-test-repository \
        bitbucket-dir/cgitize-test-repository \
        gitlab-dir/cgitize-test-repository
    verify_origin lens 'git@github.com:ekmett/lens.git'
    verify_origin chromiumembedded/cef 'git@bitbucket.org:chromiumembedded/cef.git'
    verify_origin inkscape 'git@gitlab.com:inkscape/inkscape.git'
    verify_origin browserify-dir/browserify 'git@github.com:browserify/browserify.git'
    verify_origin github-dir/cgitize-test-repository 'git@github.com:egor-tensin/cgitize-test-repository.git'
    verify_origin bitbucket-dir/cgitize-test-repository 'git@bitbucket.org:egor-tensin/cgitize-test-repository.git'
    verify_origin gitlab-dir/cgitize-test-repository 'git@gitlab.com:egor-tensin/cgitize-test-repository.git'
    cleanup
    success
}

test_https() {
    echo
    echo ======================================================================
    echo "${FUNCNAME[0]}"
    echo ======================================================================

    setup_https
    cgitize
    verify_repos \
        lens \
        chromiumembedded/cef \
        inkscape \
        wireguard/wintun \
        github-dir/cgitize-test-repository \
        bitbucket-dir/cgitize-test-repository \
        gitlab-dir/cgitize-test-repository
    verify_origin lens 'https://github.com/ekmett/lens.git'
    verify_origin chromiumembedded/cef 'https://bitbucket.org/chromiumembedded/cef.git'
    verify_origin inkscape 'https://gitlab.com/inkscape/inkscape.git'
    verify_origin browserify-dir/browserify 'https://github.com/browserify/browserify.git'
    verify_origin github-dir/cgitize-test-repository 'https://github.com/egor-tensin/cgitize-test-repository.git'
    verify_origin bitbucket-dir/cgitize-test-repository 'https://bitbucket.org/egor-tensin/cgitize-test-repository.git'
    verify_origin gitlab-dir/cgitize-test-repository 'https://gitlab.com/egor-tensin/cgitize-test-repository.git'
    cleanup
    success
}

test_one_repo() {
    echo
    echo ======================================================================
    echo "${FUNCNAME[0]}"
    echo ======================================================================

    setup_https
    cgitize --repo cef
    verify_repos chromiumembedded/cef
    verify_no_repos lens wireguard/wintun
    cleanup
    success
}

main() {
    trap cleanup EXIT
    test_ssh
    test_https
    test_one_repo
}

main
