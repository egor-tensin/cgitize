# Copyright (c) 2026 Egor Tensin <egor@tensin.name>
# This file is part of the "cgitize" project.
# For details, see https://github.com/egor-tensin/cgitize
# Distributed under the MIT License.

_sed_config() {
    if [ "$#" -ne 1 ]; then
        log "usage: ${FUNCNAME[0]} EXPR"
        return 1
    fi

    sed -i -E -e "$1" -- "$test_config_path"
}

_test_example_setup_config() {
    test_config_path="$test_root_dir/cgitize.toml"
    log "Config path: $test_config_path"

    cp -- "$tests_dir/../../examples/cgitize.toml" "$test_config_path"

    _sed_config 's@^output_dir = .*$@output_dir = "'"$test_output_dir"'"@'
    test_example_clone_ssh
    test_example_private_skip
}

_check_var() {
    local var
    for var; do
        if [ -z "${!var:+x}" ]; then
            fail "Variable not set: $var"
            return 1
        fi
    done
}

test_example_setup() {
    _check_var \
        CGITIZE_GITHUB_USERNAME \
        CGITIZE_GITHUB_TOKEN \
        CGITIZE_BITBUCKET_EMAIL \
        CGITIZE_BITBUCKET_TOKEN \
        CGITIZE_GITLAB_USERNAME \
        CGITIZE_GITLAB_TOKEN

    test_output_dir="$test_root_dir/output"
    log "Output directory: $test_output_dir"

    _test_example_setup_config
}

test_example_clone_ssh() {
    _sed_config 's/^clone_via_ssh = (true|false)$/clone_via_ssh = true/'
}

test_example_clone_https() {
    _sed_config 's/^clone_via_ssh = (true|false)$/clone_via_ssh = false/'
}

test_example_private_include() {
    _sed_config 's/^private = (true|false)$/private = true/'
}

test_example_private_skip() {
    _sed_config 's/^private = (true|false)$/private = false/'
}
