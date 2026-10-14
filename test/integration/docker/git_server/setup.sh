#!/usr/bin/env bash

set -o errexit -o nounset -o pipefail
shopt -s inherit_errexit lastpipe

readonly ssh_dir=/ssh
readonly ssh_client_password='password'

configure_git() {
    echo
    echo ----------------------------------------------------------------------
    echo Configuring git
    echo ----------------------------------------------------------------------

    git config --global user.name 'John Doe'
    git config --global user.email 'John.Doe@example.com'
    git config --global init.defaultBranch main
}

generate_ssh_keys() {
    echo
    echo ----------------------------------------------------------------------
    echo Generating SSH keys
    echo ----------------------------------------------------------------------

    mkdir -p -- "$ssh_dir"

    ssh-keygen -t rsa -b 4096 -f "$ssh_dir/client_key" -N "$ssh_client_password"
    ssh-keygen -t rsa -b 4096 -f "$ssh_dir/server_key" -N ''

    mkdir ~/.ssh

    cp "$ssh_dir/server_key"     /etc/ssh/ssh_host_ed25519_key
    cp "$ssh_dir/server_key.pub" /etc/ssh/ssh_host_ed25519_key.pub
    cp "$ssh_dir/client_key.pub" ~/.ssh/authorized_keys

    chmod 0600 -- /etc/ssh/ssh_host_ed25519_key
    chmod 0700 -- ~/.ssh/
    chmod 0600 -- ~/.ssh/authorized_keys
}

readonly repo_path="$HOME/test_repo"

create_repo() {
    echo
    echo ----------------------------------------------------------------------
    echo Setting up upstream repository
    echo ----------------------------------------------------------------------

    mkdir -p -- "$repo_path"
    pushd -- "$repo_path" > /dev/null
    git init
    echo '1' > 1.txt
    git add .
    git commit -m 'first commit'
    echo '2' > 2.txt
    git add .
    git commit -m 'second commit'
    popd > /dev/null
}

main() {
    configure_git
    generate_ssh_keys
    create_repo
}

main
