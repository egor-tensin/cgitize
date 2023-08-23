This project supports GitHub, Bitbucket & GitLab.  All of them are,
unfortunately, peculiar in their own way.

Tokens
------

All of the forges support access tokens, of course (although they're called
"app passwords" on Bitbucket).  They can be used to do `git clone https://`
with authentication info in the URL.  For GitHub, it's enough to just specify
the token:

    git clone https://TOKEN@github.com/USER/REPO.git

For Bitbucket & GitLab, however, you need to specify both the user and the
token in the URL:

    git clone https://USER:TOKEN@bitbucket.org/USER/REPO.git

Terminology
-----------

* GitHub has users and organizations; both of which can have repositories.
    * A user can be a collaborator on a different user's repository, while an
organization (I think) can only fully own its repositories.
* Bitbucket has user accounts, workspaces & projects.  User accounts own (or
are invited to) workspaces, which include projects.
    * Not so long ago, when workspaces were introduced, all users got a default
workspace matching their username (with an untitled project).
    * Each repository belongs to a project, which belongs to a workspace.
There can be multiple users collaborating on a workspace, which includes one or
more projects, which include repositories.  What an amazing concept!  I
couldn't be happier to deal with this.
* GitLab sorta has users and organizations (called "groups") here.  I'm pretty
sure they're called "namespaces" really, and are the same as Bitbucket's
"workspaces", but whatever.

API
---

* If you authenticate with GitHub and call `/users/USER/repos` for the
authenticated user, you will [only get public repositories].  Why?  Who knows.
    * You need to call `/user/repos` to include private repositories.
    * You _might_ want to use the `affiliation` parameter to only get owned
repositories.  Otherwise, you'll get all repositories in all orgs you're a
member of, etc.
* For Bitbucket, `/repositories/WORKSPACE` does [include private repositories]
(if you're authenticated, of course).
    * When somebody else invites you to collaborate on a repository, you get
access to a different workspace; this repository is not added to your workspace
or anything.
* GitLab will, helpfully, only return projects [owned by the user] when
`/users/USER/projects` is called.

[only get public repositories]: https://docs.github.com/en/rest/repos/repos?apiVersion=2022-11-28#list-repositories-for-a-user
[call /user/repos]: https://docs.github.com/en/rest/repos/repos?apiVersion=2022-11-28#list-repositories-for-the-authenticated-user
[include private repositories]: https://developer.atlassian.com/cloud/bitbucket/rest/api-group-repositories/#api-repositories-workspace-get
[owned by the user]: https://docs.gitlab.com/ee/api/projects.html#list-user-projects
