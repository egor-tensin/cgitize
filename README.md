cgitize
=======

[![CI](https://github.com/egor-tensin/cgitize/actions/workflows/ci.yml/badge.svg)](https://github.com/egor-tensin/cgitize/actions/workflows/ci.yml)

Self-host your repositories using cgit.

Supports cloning all of your repositories from major hosting providers:

* GitHub,
* Bitbucket,
* GitLab.

Example output can be found at https://git.egort.name/.

Installation
------------

    pip install cgitize

Usage
-----

Pass the path to the config to `cgitize` (/etc/cgitize/cgitize.toml by
default):

    cgitize --config path/to/cgitize.toml

See an example config file at [examples/cgitize.toml].

cgitize uses the `git` executable, which might use `ssh` internally.
Make sure the required keys are loaded to a ssh-agent (or use access
tokens/application passwords).

[examples/cgitize.toml]: examples/cgitize.toml

### Docker

You can run `cgitize` in a Docker container.
A separate image includes a web server with a configured cgit installation.

Please see [docker/README.md](docker/README.md) for details.

Mirror maintenance
------------------

Update the URL of an existing repository mirror:

    git remote set-url origin git@examples.com/username/name.git

Development
-----------

### Virtual environment

Create a virtual environment:

    make venv

Load a REPL:

    make repl

Upgrade virtual environment packages (this will also update requirements.txt):

    make venv/upgrade

### Linting

Requires [Pylint].

    pylint cgitize

[Pylint]: https://www.pylint.org/

License
-------

Distributed under the MIT License.
See [LICENSE.txt] for details.

[LICENSE.txt]: LICENSE.txt
