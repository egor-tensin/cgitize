Workspace setup
---------------

* Create a virtual Python environment: `make venv`
* Use the virtual environment: `. .venv/bin/activate`
    * Deactivate the environment when you're done: `deactivate`

Testing
-------

N.B.: `make test` is a shortcut for unit tests and the `local` integration
test.

### Unit tests

    make test/unit

You need to set the following environment variables for the authenticated
access tests to work:

* `CGITIZE_BITBUCKET_USERNAME`: `cgitize-test`
* `CGITIZE_BITBUCKET_TOKEN`
* `CGITIZE_GITHUB_USERNAME`: `cgitize-test`
* `CGITIZE_GITHUB_TOKEN`
* `CGITIZE_GITLAB_USERNAME`: `cgitize-test`
* `CGITIZE_GITLAB_TOKEN`

You can run `. test/set_credentials.sh`; it'll ask you to fill in the secrets.

### Integration

* There're three integration tests: `local`, `docker` and `example`.
Run them using

      make test/local
      sudo make test/docker
      make test/example

    * The `example` test uses the forges' APIs and might easily hit their rate
limits.
Use the tokens used for unit tests.
    * Additionally, it tests cloning via SSH (the `clone_via_ssh` setting) too,
so you need to add the secret project-specific SSH key to your agent as well
(make sure it's the only one in the agent; if there's a key associated with
another user, it could get used instead).

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
* For a new major version, update the version in the docker-compose definition
in docker/README.md.
