cgitize
=======

[![Test](https://github.com/egor-tensin/cgitize/actions/workflows/test.yml/badge.svg)](https://github.com/egor-tensin/cgitize/actions/workflows/test.yml)

Mirror your git repositories and make them cgit-ready.

Example output can be found at https://egort.name/git/.

Installation
------------

    pip install cgitize

Usage
-----

cgitize uses two config files.

* cgitize.conf contains all the settings; see example at
[examples/cgitize.conf].
* my_repos.py contains the list of repositories to mirror; see example at
[examples/my_repos.py].

Pass the path to cgitize.conf using the `--config` parameter:

    cgitize --config path/to/cgitize.conf

cgitize uses the `git` executable, which might use `ssh` internally.
Make sure the required keys are loaded to a ssh-agent (or use authentication
tokens).

[examples/cgitize.conf]: examples/cgitize.conf
[examples/my_repos.py]: examples/my_repos.py

### Docker

The image is **egortensin/cgitize**.
The container reads the config from /etc/cgitize/cgitize.conf and writes the
repositories to /var/tmp/cgitize/output.
If SSH is required, the socket should be mapped to
/var/run/cgitize/ssh-agent.sock.

    docker run -it --rm                                     \
        -v "/path/to/config:/etc/cgitize:ro"                \
        -v "$SSH_AUTH_SOCK:/var/run/cgitize/ssh-agent.sock" \
        -v "/path/to/output:/var/tmp/cgitize/output"        \
        egortensin/cgitize

The container executes cgitize inside a cron job.
The `SCHEDULE` environment variable controls the period between cgitize runs.
By default, it's set to `once`, which makes the container exit after the first
run.
You can also set it to `15min`, `hourly`, `daily`, `weekly`, `monthly` or a
custom 5-part cron schedule like `*/5 * * * *`.

Mirror maintenance
------------------

Update the URL of an existing repository mirror:

    git remote set-url origin ssh://git@examples.com/username/name.git

Development
-----------

### Packaging

The [packaging tutorial] (as it was in April 2021) on python.org was used to
make a PyPI package.
Basically, it looks to me like the Python ecosystem is currently moving from
the older setup.py to the newer setup.cfg/pyproject.toml.
It's still a bit clunky: you have to install the `build` package, placeholder
setup.py is required for `pip install -e` to work, etc.

[packaging tutorial]: https://packaging.python.org/tutorials/packaging-projects

### Linting

Requires [Pylint].

    pylint cgitize

[Pylint]: https://www.pylint.org/

License
-------

Distributed under the MIT License.
See [LICENSE.txt] for details.

[LICENSE.txt]: LICENSE.txt
