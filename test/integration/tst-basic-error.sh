test_run() {
    test_basic_setup
    test_run_cgitize --verbose
    test_basic_verify_commits \
        'committing 1.txt' \
        'committing 2.txt'

    # Add new commits
    test_basic_make_commit
    test_basic_make_commit

    rm -rf -- "$test_repo_dir"

    # Must fail to pick up new commits
    test_run_cgitize --verbose || true
    test_basic_verify_commits \
        'committing 1.txt' \
        'committing 2.txt'

    test_verify_error_header
}
