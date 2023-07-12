Workspace setup
---------------

* Create a virtual Python environment: `make venv`
* Use the virtual environment: `. .venv/bin/activate`
    * Deactivate the environment when you're done: `deactivate`
* Make sure unit tests work: `make test/unit`

Development
-----------

* Run unit tests: `make test/unit`
* There're three integration tests: `local`, `docker` and `example`.
Run them using

      make test/local
      sudo make test/docker
      make test/example

    * The `example` test uses the forges' APIs and might easily hit rate
limits.
Set environment variables described in [examples/cgitize.toml] to use "access
tokens" and get much higher rate limits.

[examples/cgitize.toml]: examples/cgitize.toml

Upgrading dependencies
----------------------

* Upgrade virtual environment packages: `make venv/upgrade`
* Upgrade base Docker images.
    * Find the current base images using `git grep -P 'FROM \w+:'`
* Upgrade the [cmark-gfm] version used in the [cgitize-frontend Docker image].

[cmark-gfm]: https://github.com/github/cmark-gfm
[cgitize-frontend Docker image]: docker/frontend/Dockerfile

Releases
--------

* Make a git tag for a new minor version using `make tag`.
You can then review it and push using `git push --tags`.
