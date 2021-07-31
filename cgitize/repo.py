# Copyright (c) 2018 Egor Tensin <Egor.Tensin@gmail.com>
# This file is part of the "cgitize" project.
# For details, see https://github.com/egor-tensin/cgitize.
# Distributed under the MIT License.

from cgitize.utils import url_remove_auth, url_replace_auth


class Repo:
    @staticmethod
    def from_config(src, config):
        if 'name' not in src:
            raise ValueError('every repository must have a name')
        name = src['name']
        desc = src.get('desc')
        homepage = src.get('homepage')
        owner = src.get('owner', config.main.default_owner)
        if 'clone_url' not in src:
            raise ValueError('every repository must have a clone URL')
        clone_url = src['clone_url']
        return Repo(name, clone_url, owner=owner, desc=desc, homepage=homepage)

    @staticmethod
    def from_github(src, config):
        name = src.name
        desc = src.description
        homepage = src.html_url
        owner = src.owner.name

        https_url = src.clone_url
        ssh_url = src.ssh_url
        clone_url = ssh_url if config.main.via_ssh else https_url
        url_auth = None if config.main.via_ssh else config.github.url_auth

        return Repo(name, clone_url, owner=owner, desc=desc, homepage=homepage,
                    url_auth=url_auth)

    @staticmethod
    def from_bitbucket(src, config):
        name = src['name']
        desc = src['description']
        homepage = src['links']['html']['href']
        owner = src['owner']['display_name']

        https_urls = [link for link in src['links']['clone'] if link['name'] == 'https']
        if len(https_urls) != 1:
            raise RuntimeError(f"no https:// clone URL for repository '{name}'?!")
        # Bitbucket leaves the username in the URL... Sigh.
        https_url = url_remove_auth(https_urls[0]['href'])

        ssh_urls = [link for link in src['links']['clone'] if link ['name'] == 'ssh']
        if len(ssh_urls) != 1: raise RuntimeError(f"no ssh:// clone URL for repository '{name}'?!")
        ssh_url = ssh_urls[0]['href']

        clone_url = ssh_url if config.main.via_ssh else https_url
        url_auth = None if config.main.via_ssh else config.bitbucket.url_auth

        return Repo(name, clone_url, owner=owner, desc=desc, homepage=homepage,
                    url_auth=url_auth)

    def __init__(self, name, clone_url, owner=None, desc=None, homepage=None,
                 url_auth=None):
        self._name = name
        self._desc = desc
        self._homepage = homepage
        self._owner = owner
        self._clone_url = clone_url
        self._url_auth = url_auth

    @property
    def name(self):
        return self._name

    @property
    def desc(self):
        if self._desc is not None:
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
