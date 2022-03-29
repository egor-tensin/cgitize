cgitize
=======

[![CI](https://github.com/egor-tensin/cgitize/actions/workflows/ci.yml/badge.svg)](https://github.com/egor-tensin/cgitize/actions/workflows/ci.yml)

Mirror your git repositories and make them cgit-ready.
Supports cloning all of your repositories from major hosting providers:

* GitHub,
* Bitbucket,
* GitLab.

Example output can be found at https://egort.name/git/.

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

Please see [docker/README.md](docker/README.md).

Mirror maintenance
------------------

Update the URL of an existing repository mirror:

    git remote set-url origin git@examples.com/username/name.git

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
