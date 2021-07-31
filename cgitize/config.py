# Copyright (c) 2021 Egor Tensin <Egor.Tensin@gmail.com>
# This file is part of the "cgitize" project.
# For details, see https://github.com/egor-tensin/cgitize.
# Distributed under the MIT License.

import configparser
import importlib
import logging
import os
import sys

from cgitize.repo import Repo, GitHub as GitHubRepo, Bitbucket as BitbucketRepo
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


class Main(Section):
    DEFAULT_OUTPUT_DIR = '/var/tmp/cgitize/output'

    @property
    def output(self):
        return self._get_config_path('output', default=Main.DEFAULT_OUTPUT_DIR)

    @property
    def clone_url(self):
        return self._get_config_value('clone_url', required=False)

    @property
    def default_owner(self):
        return self._get_config_value('owner', required=False)

    @property
    def via_ssh(self):
        return self._get_config_value('ssh', default=True)


class GitHub(Section):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.repositories = Repositories(self.impl.get('repositories', {}), GitHubRepo)

    @property
    def access_token(self):
        access_token = self._get_config_value('access_token', required=False)
        if access_token is not None:
            return access_token
        env_var = 'CGITIZE_GITHUB_ACCESS_TOKEN'
        if env_var in os.environ:
            return os.environ[env_var]
        return None

    def enum_repositories(self):
        return self.repositories.enum_repositories()


class Bitbucket(Section):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.repositories = Repositories(self.impl.get('repositories', {}), BitbucketRepo)

    @property
    def app_password(self):
        app_password = self._get_config_value('app_password', required=False)
        if app_password is not None:
            return app_password
        env_var = 'CGITIZE_BITBUCKET_APP_PASSWORD'
        if env_var in os.environ:
            return os.environ[env_var]
        return None

    def enum_repositories(self):
        return self.repositories.enum_repositories()


class Repositories(Section):
    def __init__(self, impl, repo_cls=Repo):
        super().__init__(impl)
        self.repo_cls = repo_cls

    def enum_repositories(self):
        for k, v in self.impl.items():
            yield self.repo_cls.from_config(v)


class Config:
    DEFAULT_PATH = '/etc/cgitize/cgitize.toml'

    @staticmethod
    def read(path):
        return Config(path)

    def __init__(self, path):
        self.path = os.path.abspath(path)
        with open(self.path, 'rb') as f:
            self.impl = tomli.load(f)
        self.main = Main(self.impl)
        self.repositories = Repositories(self.impl.get('repositories', {}))
        self.github = GitHub(self.impl.get('github', {}))
        self.bitbucket = Bitbucket(self.impl.get('bitbucket', {}))

    def enum_repositories(self):
        yield from self.repositories.enum_repositories()
        yield from self.github.enum_repositories()
        yield from self.bitbucket.enum_repositories()
