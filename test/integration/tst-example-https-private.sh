test_run() {
    test_example_setup
    test_example_clone_https
    test_example_private_include

    test_run_cgitize
    test_verify_error_header_empty

    test_verify_repos \
        lens \
        chromiumembedded/cef \
        graphviz \
        wireguard/wintun \
        goauthentik-dir/authentik \
        github-dir/public \
        github-dir/private \
        bitbucket-dir/public \
        bitbucket-dir/private \
        gitlab-dir/public \
        gitlab-dir/private

    test_verify_origin lens 'https://github.com/ekmett/lens.git'
    test_verify_origin chromiumembedded/cef 'https://bitbucket.org/chromiumembedded/cef.git'
    test_verify_origin graphviz 'https://gitlab.com/graphviz/graphviz.git'
    test_verify_origin goauthentik-dir/authentik 'https://github.com/goauthentik/authentik.git'

    test_verify_origin github-dir/public  'https://github.com/cgitize-test/public.git'
    test_verify_origin github-dir/private 'https://github.com/cgitize-test/private.git'
    test_verify_origin bitbucket-dir/public  'https://bitbucket.org/cgitize-test-workspace/public.git'
    test_verify_origin bitbucket-dir/private 'https://bitbucket.org/cgitize-test-workspace/private.git'
    test_verify_origin gitlab-dir/public  'https://gitlab.com/cgitize-test/public.git'
    test_verify_origin gitlab-dir/private 'https://gitlab.com/cgitize-test/private.git'
}
