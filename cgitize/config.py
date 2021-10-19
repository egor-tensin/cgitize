# Copyright (c) 2021 Egor Tensin <Egor.Tensin@gmail.com>
# This file is part of the "cgitize" project.
# For details, see https://github.com/egor-tensin/cgitize.
# Distributed under the MIT License.

import os

import tomli

from cgitize.bitbucket import Bitbucket
from cgitize.github import GitHub
from cgitize.gitlab import GitLab
from cgitize.repo import Repo


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
    DEFAULT_OUTPUT_DIR = '/var/tmp/cgitize'

    @property
    def output_dir(self):
        return self._get_config_path('output_dir', default=MainSection.DEFAULT_OUTPUT_DIR)

    @property
    def clone_url(self):
        return self._get_config_value('clone_url', required=False)

    @property
    def clone_via_ssh(self):
        return self._get_config_value('clone_via_ssh', default=True)

    @property
    def default_owner(self):
        return self._get_config_value('owner', required=False)


class GitHubSection(Section):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.users = UsersSection(self.impl.get('users', {}))
        self.repositories = RepositoriesSection(self.impl.get('repositories', {}))

    @property
    def access_token(self):
        return self._get_config_or_env('access_token', 'CGITIZE_GITHUB_ACCESS_TOKEN')

    @property
    def url_auth(self):
        return self.access_token


def two_part_url_auth(username, password):
        if username is None or password is None:
            return None
        return f'{username}:{password}'


class BitbucketSection(Section):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.users = UsersSection(self.impl.get('users', {}))
        self.repositories = RepositoriesSection(self.impl.get('repositories', {}))

    @property
    def app_password(self):
        return self._get_config_or_env('app_password', 'CGITIZE_BITBUCKET_APP_PASSWORD')

    @property
    def username(self):
        return self._get_config_or_env('username', 'CGITIZE_BITBUCKET_USERNAME')

    @property
    def url_auth(self):
        return two_part_url_auth(self.username, self.app_password)

    def enum_repositories(self):
        return map(HostedRepo, self.repositories.enum_repositories())


class GitLabSection(Section):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.users = UsersSection(self.impl.get('users', {}))
        self.repositories = RepositoriesSection(self.impl.get('repositories', {}))

    @property
    def access_token(self):
        return self._get_config_or_env('access_token', 'CGITIZE_GITLAB_ACCESS_TOKEN')

    @property
    def username(self):
        return self._get_config_or_env('username', 'CGITIZE_GITLAB_USERNAME')

    @property
    def url_auth(self):
        return two_part_url_auth(self.username, self.access_token)


class UsersSection(Section):
    def enum_users(self):
        return self.impl.values()


class RepositoriesSection(Section):
    def enum_repositories(self):
        return self.impl.values()


class User:
    def __init__(self, impl):
        if 'name' not in impl:
            raise ValueError("every user must have 'name'")
        self._impl = impl

    @property
    def name(self):
        return self._impl['name']

    @property
    def dir(self):
        return self._impl.get('dir')

    @property
    def skip(self):
        return self._impl.get('skip', [])


class HostedRepo:
    def __init__(self, impl):
        if 'id' not in impl:
            raise ValueError("every hosted repository must have 'id'")
        self._impl = impl

    @property
    def id(self):
        return self._impl['id']

    @property
    def dir(self):
        return self._impl.get('dir')


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
        self.gitlab = GitLabSection(self.impl.get('gitlab', {}))

    def _parse_explicit_repositories(self):
        for r in self.repositories.enum_repositories():
            yield Repo.from_config(r, self)

    def _parse_hosted_repositories(self, cfg, api):
        for r in cfg.repositories.enum_repositories():
            r = HostedRepo(r)
            yield api.convert_repo(api.get_repo(r), self, r.dir)
        for u in cfg.users.enum_users():
            u = User(u)
            for r in api.get_user_repos(u):
                r = api.convert_repo(r, self, u.dir)
                if r.name in u.skip:
                    continue
                yield r

    def _parse_github_repositories(self):
        github = GitHub(self.github.access_token)
        return self._parse_hosted_repositories(self.github, github)

    def _parse_bitbucket_repositories(self):
        bitbucket = Bitbucket(self.bitbucket.username, self.bitbucket.app_password)
        return self._parse_hosted_repositories(self.bitbucket, bitbucket)

    def _parse_gitlab_repositories(self):
        gitlab = GitLab(self.gitlab.access_token)
        return self._parse_hosted_repositories(self.gitlab, gitlab)

    def parse_repositories(self):
        yield from self._parse_explicit_repositories()
        yield from self._parse_github_repositories()
        yield from self._parse_bitbucket_repositories()
        yield from self._parse_gitlab_repositories()
