cgitize
=======

[![Test](https://github.com/egor-tensin/cgitize/workflows/Test/badge.svg)](https://github.com/egor-tensin/cgitize/actions?query=workflow%3ATest)

Mirror your git repositories and make them cgit-ready.

Usage
-----

Adjust the config in [examples/cgitize.conf] and pass it using the
`--config` parameter:

    > python3 -m cgitize.main --config path/to/cgitize.conf

The repository list is stored in my_repos.py (the `my_repos` setting in the
config).
See [examples/my_repos.py] for an example.

cgitize/main.py calls git, which might call ssh internally.
Make sure the required keys are loaded to a ssh-agent.

[examples/cgitize.conf]: examples/cgitize.conf
[examples/my_repos.py]: examples/my_repos.py

### Docker

The image is **egortensin/cgitize**.
The container reads the config from */etc/cgitize/cgitize.conf* and
writes the repositories to */var/tmp/cgitize/output*.
If SSH is required, the socket should be mapped to
*/var/run/cgitize/ssh-agent.sock*.

For example:

    > docker run -it --rm                                   \
        -v "/path/to/config:/etc/cgitize:ro"                \
        -v "$SSH_AUTH_SOCK:/var/run/cgitize/ssh-agent.sock" \
        -v "/path/to/output:/var/tmp/cgitize/output"        \
        egortensin/cgitize

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
