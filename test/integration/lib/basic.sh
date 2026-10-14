# Copyright (c) 2026 Egor Tensin <egor@tensin.name>
# This file is part of the "cgitize" project.
# For details, see https://github.com/egor-tensin/cgitize
# Distributed under the MIT License.

test_basic_setup() {
    test_repo_dir="$test_root_dir/repo"
    test_output_dir="$test_root_dir/output"
    test_config_path="$test_root_dir/cgitize.toml"
    test_mirror_name=repo_mirror
    test_mirror_dir="$test_output_dir/$test_mirror_name.git"

    log "Repo directory: $test_repo_dir"
    log "Output directory: $test_output_dir"
    log "Config path: $test_config_path"

    mkdir -- "$test_repo_dir"
    git -C "$test_repo_dir" init -q
    git -C "$test_repo_dir" config user.name 'Test user'
    git -C "$test_repo_dir" config user.email 'test@example.com'

    test_basic_make_commit
    test_basic_make_commit

    cat > "$test_config_path" <<EOF
output_dir = "$test_output_dir"

[repositories.repo]
name = "$test_mirror_name"
clone_url = "$test_repo_dir"
EOF
}

_test_commit_counter=0

test_basic_make_commit() {
    _test_commit_counter=$((_test_commit_counter + 1))

    local file
    file="$_test_commit_counter.txt"
    echo "$_test_commit_counter" > "$test_repo_dir/$file"

    log "Commiting file $file in $test_repo_dir..."

    touch -- "$test_repo_dir/file"
    git -C "$test_repo_dir" add "$file"
    git -C "$test_repo_dir" commit -q -m "committing $file"
}

test_basic_verify_commits() {
    log "Verifying commits in $test_mirror_dir..."

    local msg
    git -C "$test_mirror_dir" log --reverse --pretty=tformat:%s |
        while IFS= read -r msg; do
            if [ "$#" -eq 0 ]; then
                fail "Unexpected commit found: $msg"
                return 1
            fi
            if [ "$msg" != "$1" ]; then
                fail "Unexpected commit found: $msg"
                fail_details "Expected commit: $1"
                return 1
            fi
            shift
        done

    if [ "$#" -ne 0 ]; then
        fail "Missing commit: $1"
        return 1
    fi
}
