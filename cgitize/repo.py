# Copyright (c) 2018 Egor Tensin <Egor.Tensin@gmail.com>
# This file is part of the "cgitize" project.
# For details, see https://github.com/egor-tensin/cgitize.
# Distributed under the MIT License.

import abc
import os.path
from urllib.parse import urlsplit, urlunsplit


class Repo:
    @classmethod
    def from_config(cls, cfg):
        if 'id' not in cfg:
            raise ValueError('every repository must have its id defined')
        return cls(cfg['id'], clone_url=cfg.get('clone_url'),
                   owner=cfg.get('owner'), desc=cfg.get('desc'),
                   homepage=cfg.get('homepage'))

    def __init__(self, name, clone_url=None, owner=None, desc=None,
                 homepage=None):
        self._name = name
        self._clone_url = clone_url
        self._owner = owner
        self._desc = desc
        self._homepage = homepage

    def fill_defaults(self, config):
        if self._owner is None:
            self._owner = config.main.default_owner

    def validate(self):
        if self.clone_url is None:
            raise RuntimeError('upstream repository URL must be specified')

    @property
    def name(self):
        return self._name

    @property
    def clone_url(self):
        return self._clone_url

    @property
    def owner(self):
        return self._owner

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
    def url_auth(self):
        return False


class HostedRepo(Repo, abc.ABC):
    @classmethod
    def from_config(cls, cfg):
        if 'id' not in cfg:
            raise ValueError('every repository must have its id defined')
        return cls(cfg['id'], owner=cfg.get('owner'), desc=cfg.get('desc'),
                   homepage=cfg.get('homepage'))

    @staticmethod
    def split_repo_id(repo_id):
        components = repo_id.split('/')
        if len(components) != 2:
            raise ValueError(f'repository ID must be in the USER/NAME format: {repo_id}')
        user, name = components
        return user, name

    def __init__(self, repo_id, owner=None, desc=None, homepage=None,
                 via_ssh=True):
        user, name = self.split_repo_id(repo_id)
        super().__init__(name, clone_url=None, owner=owner, desc=desc,
                         homepage=homepage)
        self._user = user
        self._via_ssh = via_ssh

    def fill_defaults(self, config):
        super().fill_defaults(config)
        self._via_ssh = config.main.via_ssh

    @property
    def user(self):
        return self._user

    @property
    @abc.abstractmethod
    def provider_name(self):
        pass

    @property
    @abc.abstractmethod
    def clone_url_ssh(self):
        pass

    @property
    @abc.abstractmethod
    def clone_url_https(self):
        pass

    @property
    def clone_url(self):
        if self._via_ssh:
            return self.clone_url_ssh
        return self.clone_url_https

    @property
    def clone_url_with_auth(self):
        if self._via_ssh:
            return self.clone_url_ssh
        auth = self.url_auth
        clone_url = self.clone_url_https
        if not auth:
            return clone_url
        clone_url = urlsplit(clone_url)
        clone_url = clone_url._replace(netloc=f'{auth}@{clone_url.netloc}')
        return urlunsplit(clone_url)


class GitHub(HostedRepo):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self._access_token = None

    def fill_defaults(self, config):
        super().fill_defaults(config)
        self._access_token = config.github.access_token

    @property
    def provider_name(self):
        return 'GitHub'

    @property
    def homepage(self):
        return f'https://github.com/{self.user}/{self.name}'

    @property
    def url_auth(self):
        if self._access_token is None:
            return ''
        return f'{self._access_token}'

    @property
    def clone_url_ssh(self):
        return f'ssh://git@github.com/{self.user}/{self.name}.git'

    @property
    def clone_url_https(self):
        return f'https://github.com/{self.user}/{self.name}.git'


class Bitbucket(HostedRepo):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self._app_password = None

    def fill_defaults(self, config):
        super().fill_defaults(config)
        self._app_password = config.bitbucket.app_password

    @property
    def provider_name(self):
        return 'Bitbucket'

    @property
    def homepage(self):
        return f'https://bitbucket.org/{self.user}/{self.name.lower()}'

    @property
    def url_auth(self):
        if self._app_password is None:
            return ''
        return f'{self.user}:{self._app_password}'

    @property
    def clone_url_ssh(self):
        return f'ssh://git@bitbucket.org/{self.user}/{self.name}.git'

    @property
    def clone_url_https(self):
        return f'https://bitbucket.org/{self.user}/{self.name}.git'
