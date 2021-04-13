cgitize
=======

[![Test](https://github.com/egor-tensin/cgitize/actions/workflows/test.yml/badge.svg)](https://github.com/egor-tensin/cgitize/actions/workflows/test.yml)

Mirror your git repositories and make them cgit-ready.

Example output can be found at https://egort.name/git/.

Usage
-----

Adjust the sample config in [examples/cgitize.conf] and pass its path as the
`--config` parameter value:

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
The container reads the config from /etc/cgitize/cgitize.conf and writes the
repositories to /var/tmp/cgitize/output.
If SSH is required, the socket should be mapped to
/var/run/cgitize/ssh-agent.sock.

    > docker run -it --rm                                   \
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

    > git remote set-url origin ssh://git@examples.com/username/name.git

Development
-----------

### Linting

Requires [Pylint].

    > pylint cgitize

[Pylint]: https://www.pylint.org/

License
-------

Distributed under the MIT License.
See [LICENSE.txt] for details.

[LICENSE.txt]: LICENSE.txt
