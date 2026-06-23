# Copyright (c) 2018 Egor Tensin <egor@tensin.name>
# This file is part of the "cgitize" project.
# For details, see https://github.com/egor-tensin/cgitize.
# Distributed under the MIT License.

from enum import Enum
import os.path

from cgitize.utils import url_remove_auth, url_replace_auth


class Visibility(Enum):
    ALL = "all"
    PUBLIC = "public"
    PRIVATE = "private"

    def __str__(self):
        return self.name

    @staticmethod
    def from_config(public, private):
        if public and private:
            return Visibility.ALL
        if not public and not private:
            raise RuntimeError(
                "you need to fetch either public or private repos, or both"
            )
        if public:
            return Visibility.PUBLIC
        return Visibility.PRIVATE

    def to_bitbucket_arg(self):
        # https://developer.atlassian.com/cloud/bitbucket/rest/intro/#filtering
        # https://developer.atlassian.com/cloud/bitbucket/rest/api-group-repositories/#api-group-repositories
        if self is Visibility.ALL:
            return None
        if self is Visibility.PUBLIC:
            return "is_private=False"
        if self is Visibility.PRIVATE:
            return "is_private=True"
        raise NotImplementedError(f"not implemented visibility level: {self}")

    def to_github_arg(self):
        # https://docs.github.com/en/rest/repos/repos?apiVersion=2026-03-10#list-repositories-for-the-authenticated-user
        if self is Visibility.ALL:
            return None
        if self is Visibility.PUBLIC:
            return "public"
        if self is Visibility.PRIVATE:
            return "private"
        raise NotImplementedError(f"not implemented visibility level: {self}")

    def to_gitlab_arg(self):
        # https://python-gitlab.readthedocs.io/en/stable/gl_objects/projects.html#projects
        if self is Visibility.ALL:
            return None
        if self is Visibility.PUBLIC:
            return "public"
        if self is Visibility.PRIVATE:
            return "private"
        raise NotImplementedError(f"not implemented visibility level: {self}")


class Repo:
    @staticmethod
    def from_config(src, config):
        if "name" not in src:
            raise ValueError("every repository must have 'name'")
        name = src["name"]
        desc = src.get("desc")
        homepage = src.get("homepage")
        owner = src.get("owner", config.main.default_owner)
        if "clone_url" not in src:
            raise ValueError("every repository must have 'clone_url'")
        clone_url = src["clone_url"]
        subdir = src.get("dir")
        return Repo(
            name, clone_url, owner=owner, desc=desc, homepage=homepage, subdir=subdir
        )

    @staticmethod
    def from_github(src, config, subdir=None):
        name = src.name
        desc = src.description
        homepage = src.html_url
        owner = src.owner.name

        https_url = src.clone_url
        ssh_url = src.ssh_url

        clone_url = ssh_url
        url_auth = None
        if not config.main.clone_via_ssh:
            clone_url = https_url
            url_auth = config.github.url_auth

        return Repo(
            name,
            clone_url,
            owner=owner,
            desc=desc,
            homepage=homepage,
            url_auth=url_auth,
            subdir=subdir,
        )

    @staticmethod
    def from_bitbucket(src, config, subdir=None):
        name = src.name
        desc = src.description
        homepage = src.get_link("html")
        owner = src.data["owner"]["display_name"]

        https_urls = [
            link for link in src.data["links"]["clone"] if link["name"] == "https"
        ]
        if len(https_urls) != 1:
            raise RuntimeError(f"no https:// clone URL for repository '{name}'?!")
        # Bitbucket leaves the username in the URL... Sigh.
        api_auth, https_url = url_remove_auth(https_urls[0]["href"])

        ssh_urls = [
            link for link in src.data["links"]["clone"] if link["name"] == "ssh"
        ]
        if len(ssh_urls) != 1:
            raise RuntimeError(f"no ssh:// clone URL for repository '{name}'?!")
        ssh_url = ssh_urls[0]["href"]

        clone_url = ssh_url
        url_auth = None
        if not config.main.clone_via_ssh:
            clone_url = https_url
            url_auth = config.bitbucket.url_auth
            # Bitbucket, since deprecating app passwords, now requires that
            # users authenticate with their Atlassian email & API token.
            # Unfortunately (sigh...), if you want to clone a repo via HTTPS,
            # you can't use the very same email + token combo in the URL, you
            # have to use your username (double sigh...).  Luckily, for some
            # reason, Bitbucket leaves the relevant username in the API response.
            url_auth = api_auth[0], url_auth[1]

        return Repo(
            name,
            clone_url,
            owner=owner,
            desc=desc,
            homepage=homepage,
            url_auth=url_auth,
            subdir=subdir,
        )

    @staticmethod
    def from_gitlab(src, config, subdir=None):
        name = src.name
        desc = src.description
        homepage = src.web_url
        owner = src.namespace["name"]

        https_url = src.http_url_to_repo
        ssh_url = src.ssh_url_to_repo

        clone_url = ssh_url
        url_auth = None
        if not config.main.clone_via_ssh:
            clone_url = https_url
            url_auth = config.gitlab.url_auth

        return Repo(
            name,
            clone_url,
            owner=owner,
            desc=desc,
            homepage=homepage,
            url_auth=url_auth,
            subdir=subdir,
        )

    def __init__(
        self,
        name,
        clone_url,
        owner=None,
        desc=None,
        homepage=None,
        url_auth=None,
        subdir=None,
    ):
        self._name = name
        self._desc = desc
        self._homepage = homepage
        self._owner = owner
        self._clone_url = clone_url
        self._url_auth = url_auth
        self._dir = subdir

    @property
    def name(self):
        return self._name

    @property
    def namegit(self):
        return f"{self.name}.git"

    @property
    def desc(self):
        if self._desc is not None and self._desc:
            return self._desc
        if self.homepage:
            return self.homepage
        if self.clone_url:
            return self.clone_url
        return self.name

    @property
    def homepage(self):
        return self._homepage

    @property
    def owner(self):
        return self._owner

    @property
    def clone_url(self):
        return self._clone_url

    @property
    def url_auth(self):
        return self._url_auth

    @property
    def clone_url_with_auth(self):
        if not self.url_auth:
            return self.clone_url
        return url_replace_auth(self.clone_url, self.url_auth)

    def _with_dir(self, s):
        if self._dir is None:
            return s
        return os.path.join(self._dir, s)

    @property
    def dir(self):
        return self._with_dir(self.namegit)

    @property
    def url_path(self):
        return self._with_dir(self.name)
