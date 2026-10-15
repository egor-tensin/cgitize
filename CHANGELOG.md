v9.0
====

### Breaking changes

* Docker images: SSH agent should now be mapped to /ssh/agent.sock (instead of
/ssh-agent.sock).

v9.1
----

* The global ~/.gitconfig is no longer used for HTTPS authentication.
Instead, a temporary file is used.
* Internally, `git` is now executed with the `GIT_CONFIG_NOSYSTEM` and
`GIT_CONFIG_GLOBAL` environment variables set.
This might break existing setups in some way.

v8.0
====

### Breaking changes

* Since Bitbucket deprecated "app passwords", an Atlassian API token is now
required in place of those.
    * In cgitize.toml, the field `bitbucket.username` is replaced with
`bitbucket.email`, since the API tokens are tied to the Atlassian account now.

v7.0
====

### Breaking changes

* For forge users, only publicly visible repositories are fetched by default.
    * New fields in cgitize.toml `{github,bitbucket,gitlab}.users.*.{public,private}`
control whether to fetch public or private repositories, or both.
    * The `public` field is set to `true` by default; `private` is `false`.

v6.0
====

* Major version bumps for the dependencies.
* Otherwise, no breaking changes.

v5.0
====

### Breaking changes

* GitHub: private user repositories are also cloned now.
    * This change is consistent with how Gitlab and Bitbucket backend work.
    * If `github.token` is set in cgitize.toml, `github.username` must also be
set.

v5.1
----

### New features

* In case of an error, a message is displayed in the frontend's header.

v4.0
====

### Breaking changes

* Fields `access_token` & `app_password` in cgitize.toml renamed to simply
`token`.
* Repositories are cloned into directories with the ".git" suffix now.

v3.0
====

* The latest release that I'm still not too lazy to look up.
