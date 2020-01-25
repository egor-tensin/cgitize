cgit repos
==========

[![Travis (.com) branch](https://img.shields.io/travis/com/egor-tensin/cgit-repos/master?label=Tests)](https://travis-ci.com/egor-tensin/cgit-repos)
[![Docker Cloud Build Status](https://img.shields.io/docker/cloud/build/egortensin/pull-cgit-repos?label=Docker)](https://hub.docker.com/repository/docker/egortensin/pull-cgit-repos/builds)

Mirror a list of git repositories and make them available for consumption by
cgit.

Usage
-----

Adjust the config in [examples/cgit-repos.conf] and pass it using the
`--config` parameter:

    > python3 -m pull.main --config path/to/cgit-repos.conf

The repository list is stored in my_repos.py (the `my_repos` setting in the
config).
See [examples/my_repos.py] for an example.

pull/main.py calls git, which might call ssh internally.
Make sure the required keys are loaded to a ssh-agent.

[examples/cgit-repos.conf]: examples/cgit-repos.conf
[examples/my_repos.py]: examples/my_repos.py

### Docker

The image is **egortensin/pull-cgit-repos**.
The container reads the config from */etc/cgit-repos/cgit-repos.conf* and
writes the repositories to */var/tmp/cgit-repos/output*.
If SSH is required, the socket should be mapped to
*/var/run/cgit-repos/ssh-agent.sock*.

For example:

    > docker run -it --rm                                      \
        -v "/path/to/config:/etc/cgit-repos:ro"                \
        -v "$SSH_AUTH_SOCK:/var/run/cgit-repos/ssh-agent.sock" \
        -v "/path/to/output:/var/tmp/cgit-repos/output"        \
        egortensin/pull-cgit-repos

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
