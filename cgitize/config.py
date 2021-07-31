# Copyright (c) 2021 Egor Tensin <Egor.Tensin@gmail.com>
# This file is part of the "cgitize" project.
# For details, see https://github.com/egor-tensin/cgitize.
# Distributed under the MIT License.

import configparser
import importlib
import logging
import os
import sys

from cgitize.bitbucket import Bitbucket
from cgitize.github import GitHub
from cgitize.repo import Repo
from cgitize.utils import chdir

import tomli


class Section:
    def __init__(self, impl):
        self.impl = impl

    def _get_config_value(self, key, required=True, default=None):
        if required and default is None:
            if not key in self.impl:
                raise RuntimeError(f'configuration value is missing: {key}')
        return self.impl.get(key, default)

    def _get_config_path(self, *args, **kwargs):
        return os.path.abspath(self._get_config_value(*args, **kwargs))

    def _get_config_or_env(self, key, env_name):
        val = self._get_config_value(key, required=False)
        if val is not None:
            return val
        if env_name in os.environ:
            return os.environ[env_name]
        return None


class MainSection(Section):
    DEFAULT_OUTPUT_DIR = '/var/tmp/cgitize/output'

    @property
    def output(self):
        return self._get_config_path('output', default=MainSection.DEFAULT_OUTPUT_DIR)

    @property
    def clone_url(self):
        return self._get_config_value('clone_url', required=False)

    @property
    def default_owner(self):
        return self._get_config_value('owner', required=False)

    @property
    def via_ssh(self):
        return self._get_config_value('ssh', default=True)


class GitHubSection(Section):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.repositories = RepositoriesSection(self.impl.get('repositories', {}))

    @property
    def access_token(self):
        return self._get_config_or_env('access_token', 'CGITIZE_GITHUB_ACCESS_TOKEN')

    @property
    def url_auth(self):
        return self.access_token


class BitbucketSection(Section):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.repositories = RepositoriesSection(self.impl.get('repositories', {}))

    @property
    def app_password(self):
        return self._get_config_or_env('app_password', 'CGITIZE_BITBUCKET_APP_PASSWORD')

    @property
    def username(self):
        return self._get_config_or_env('username', 'CGITIZE_BITBUCKET_USERNAME')

    @property
    def url_auth(self):
        username = self.username
        password = self.app_password
        if username is None or password is None:
            return None
        return f'{username}:{password}'


class RepositoriesSection(Section):
    def enum_repositories(self):
        return self.impl.values()


class Config:
    DEFAULT_PATH = '/etc/cgitize/cgitize.toml'

    @staticmethod
    def read(path):
        return Config(path)

    def __init__(self, path):
        self.path = os.path.abspath(path)
        with open(self.path, 'rb') as f:
            self.impl = tomli.load(f)
        self.main = MainSection(self.impl)
        self.repositories = RepositoriesSection(self.impl.get('repositories', {}))
        self.github = GitHubSection(self.impl.get('github', {}))
        self.bitbucket = BitbucketSection(self.impl.get('bitbucket', {}))

    def _parse_explicit_repositories(self):
        for r in self.repositories.enum_repositories():
            yield Repo.from_config(r, self)

    def _parse_github_repositories(self):
        github = GitHub(self.github.access_token)
        for r in self.github.repositories.enum_repositories():
            yield Repo.from_github(github.get_repo(r), self)

    def _parse_bitbucket_repositories(self):
        bitbucket = Bitbucket(self.bitbucket.username, self.bitbucket.app_password)
        for r in self.bitbucket.repositories.enum_repositories():
            yield Repo.from_bitbucket(bitbucket.get_repo(r), self)

    def parse_repositories(self):
        yield from self._parse_explicit_repositories()
        yield from self._parse_github_repositories()
        yield from self._parse_bitbucket_repositories()
