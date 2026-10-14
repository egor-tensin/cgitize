test_run() {
    test_example_setup
    test_example_clone_https

    test_run_cgitize --repo cef
    test_verify_error_header_empty

    test_verify_repos chromiumembedded/cef
    test_verify_no_repos lens wireguard/wintun
}
