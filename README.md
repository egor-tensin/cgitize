cgit repos
==========

Mirror a list of git repositories and make them available for consumption by
cgit.

Usage
-----

Update the config in [examples/cgit-repos.conf] and pass it using the
`--config` parameter:

    > python3 -m pull.main --config path/to/cgit-repos.conf

The repository list is stored in my_repos.py (the `my_repos` setting in the
config).
See [examples/my_repos.py] for an example.

pull/main.py calls git, which might call ssh internally.
Make sure the required keys are loaded to the ssh-agent.

[examples/cgit-repos.conf]: examples/cgit-repos.conf
[examples/my_repos.py]: examples/my_repos.py

### Docker

The image is `egortensin/pull-cgit-repos`.
The container reads the config from /etc/cgit-repos/cgit-repos.conf and updates
the repositories in /var/tmp/cgit-repos/output.
If SSH is required, the socket should be mapped to
/var/run/cgit-repos/ssh-agent.sock.

For example:

    > docker run -it --rm                                      \
        -v "/path/to/config:/etc/cgit-repos:ro"                \
        -v "$SSH_AUTH_SOCK:/var/run/cgit-repos/ssh-agent.sock" \
        -v "/path/to/output:/var/tmp/cgit-repos/output"        \
        egortensin/pull-cgit-repos

Development
-----------

### Docker

To build an image:

    > docker build -t egortensin/pull-cgit-repos .

### Linting

Requires [Pylint].

    > pylint pull

[Pylint]: https://www.pylint.org/

License
-------

Distributed under the MIT License.
See [LICENSE.txt] for details.

[LICENSE.txt]: LICENSE.txt
