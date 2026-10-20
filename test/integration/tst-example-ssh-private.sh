test_run() {
    test_example_setup
    test_example_clone_ssh
    test_example_private_include

    test_run_cgitize
    test_verify_error_header_empty

    test_verify_repos \
        lens \
        chromiumembedded/cef \
        graphviz \
        wireguard/wintun \
        goauthentik-dir/authentik \
        goauthentik-dir/client-python \
        github-dir/public \
        github-dir/private \
        bitbucket-dir/public \
        bitbucket-dir/private \
        gitlab-dir/public \
        gitlab-dir/private

    test_verify_origin lens 'git@github.com:ekmett/lens.git'
    test_verify_origin chromiumembedded/cef 'git@ssh.bitbucket.org:chromiumembedded/cef.git'
    test_verify_origin graphviz 'git@gitlab.com:graphviz/graphviz.git'
    test_verify_origin goauthentik-dir/authentik 'git@github.com:goauthentik/authentik.git'
    test_verify_origin goauthentik-dir/client-python 'git@github.com:goauthentik/client-python.git'

    test_verify_origin github-dir/public  'git@github.com:cgitize-test/public.git'
    test_verify_origin github-dir/private 'git@github.com:cgitize-test/private.git'
    test_verify_origin bitbucket-dir/public  'git@ssh.bitbucket.org:cgitize-test-workspace/public.git'
    test_verify_origin bitbucket-dir/private 'git@ssh.bitbucket.org:cgitize-test-workspace/private.git'
    test_verify_origin gitlab-dir/public  'git@gitlab.com:cgitize-test/public.git'
    test_verify_origin gitlab-dir/private 'git@gitlab.com:cgitize-test/private.git'
}
