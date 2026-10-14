test_run() {
    test_basic_setup
    test_run_cgitize --verbose
    test_basic_verify_commits \
        'committing 1.txt' \
        'committing 2.txt'

    # Add new commits
    test_basic_make_commit
    test_basic_make_commit

    # Pick up new commits
    test_run_cgitize --verbose
    test_basic_verify_commits \
        'committing 1.txt' \
        'committing 2.txt' \
        'committing 3.txt' \
        'committing 4.txt'

    test_verify_error_header_empty
}
