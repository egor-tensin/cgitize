cgit repos
==========

[![Test](https://github.com/egor-tensin/cgit-repos/workflows/Test/badge.svg)](https://github.com/egor-tensin/cgit-repos/actions?query=workflow%3ATest)

Mirror your git repositories and make them cgit-ready.

Usage
-----

Adjust the config in [examples/cgit-repos.conf] and pass it using the
`--config` parameter:

    > python3 -m cgit.repos.main --config path/to/cgit-repos.conf

The repository list is stored in my_repos.py (the `my_repos` setting in the
config).
See [examples/my_repos.py] for an example.

cgit/repos/main.py calls git, which might call ssh internally.
Make sure the required keys are loaded to a ssh-agent.

[examples/cgit-repos.conf]: examples/cgit-repos.conf
[examples/my_repos.py]: examples/my_repos.py

### Docker

The image is **egortensin/cgit-repos**.
The container reads the config from */etc/cgit-repos/cgit-repos.conf* and
writes the repositories to */var/tmp/cgit-repos/output*.
If SSH is required, the socket should be mapped to
*/var/run/cgit-repos/ssh-agent.sock*.

For example:

    > docker run -it --rm                                      \
        -v "/path/to/config:/etc/cgit-repos:ro"                \
        -v "$SSH_AUTH_SOCK:/var/run/cgit-repos/ssh-agent.sock" \
        -v "/path/to/output:/var/tmp/cgit-repos/output"        \
        egortensin/cgit-repos

### my_repos.py

Change the section to which the repository belongs to using `cp --archive` (so
that the "Idle" column isn't updated):

    > cp --archive -- section1/repo section2/

Update the URL of an existing repository mirror:

    > git remote set-url origin ssh://git@examples.com/username/name.git

Development
-----------

### Docker

To build an image:

    > make docker/build

### Linting

Requires [Pylint].

    > pylint cgit

[Pylint]: https://www.pylint.org/

License
-------

Distributed under the MIT License.
See [LICENSE.txt] for details.

[LICENSE.txt]: LICENSE.txt
