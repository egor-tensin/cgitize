# Copyright (c) 2021 Egor Tensin <Egor.Tensin@gmail.com>
# This file is part of the "cgitize" project.
# For details, see https://github.com/egor-tensin/cgitize.
# Distributed under the MIT License.

from abc import ABC, abstractmethod
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
    DEFAULT_OUTPUT_DIR = '/mnt/cgitize'

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


class ServiceSection(Section, ABC):
    def __init__(self, impl):
        super().__init__(impl)
        self.repositories = RepositoriesSection(self.impl.get('repositories', {}))
        self.users = UsersSection(self.impl.get('users', {}))

    def enum_repositories(self, cfg):
        api = self.connect_to_service()
        for r in self.repositories.enum_repositories():
            r = HostedRepo(r)
            yield api.convert_repo(api.get_repo(r), cfg, r.dir)
        for u in self.users.enum_users():
            for r in api.get_user_repos(u):
                r = api.convert_repo(r, cfg, u.dir)
                if r.name in u.skip:
                    continue
                yield r

    @abstractmethod
    def connect_to_service(self):
        pass


class GitHubSection(ServiceSection):
    def __init__(self, impl):
        super().__init__(impl)
        self.orgs = OrgsSection(self.impl.get('organizations', {}))

    @property
    def token(self):
        return self._get_config_or_env('token', 'CGITIZE_GITHUB_TOKEN')

    @property
    def url_auth(self):
        return self.token

    def enum_repositories(self, cfg):
        yield from super().enum_repositories(cfg)
        api = self.connect_to_service()
        for org in self.orgs.enum_orgs():
            for repo in api.get_org_repos(org):
                repo = api.convert_repo(repo, cfg, org.dir)
                if repo.name in org.skip:
                    continue
                yield repo

    def connect_to_service(self):
        return GitHub(self.token)


def two_part_url_auth(username, password):
    if username is None or password is None:
        return None
    return f'{username}:{password}'


class BitbucketSection(ServiceSection):
    @property
    def token(self):
        return self._get_config_or_env('token', 'CGITIZE_BITBUCKET_TOKEN')

    @property
    def username(self):
        return self._get_config_or_env('username', 'CGITIZE_BITBUCKET_USERNAME')

    @property
    def url_auth(self):
        return two_part_url_auth(self.username, self.token)

    def connect_to_service(self):
        return Bitbucket(self.username, self.token)


class GitLabSection(ServiceSection):
    @property
    def token(self):
        return self._get_config_or_env('token', 'CGITIZE_GITLAB_TOKEN')

    @property
    def username(self):
        return self._get_config_or_env('username', 'CGITIZE_GITLAB_USERNAME')

    @property
    def url_auth(self):
        return two_part_url_auth(self.username, self.token)

    def connect_to_service(self):
        return GitLab(self.token)


class UsersSection(Section):
    def enum_users(self):
        return map(User, self.impl.values())


class OrgsSection(Section):
    def enum_orgs(self):
        return map(Org, self.impl.values())


class RepositoriesSection(Section):
    def enum_repositories(self):
        return self.impl.values()


class User:
    def __init__(self, impl):
        if 'name' not in impl:
            raise ValueError("every user must have a 'name'")
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


class Org(User):
    def __init__(self, impl):
        if 'name' not in impl:
            raise ValueError("every organization must have a 'name'")
        self._impl = impl


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

    def parse_repositories(self):
        yield from self._parse_explicit_repositories()
        yield from self.github.enum_repositories(self)
        yield from self.bitbucket.enum_repositories(self)
        yield from self.gitlab.enum_repositories(self)
