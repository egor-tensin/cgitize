# Copyright (c) 2018 Egor Tensin <Egor.Tensin@gmail.com>
# This file is part of the "cgitize" project.
# For details, see https://github.com/egor-tensin/cgitize.
# Distributed under the MIT License.

import abc
import os.path


class Repo:
    @staticmethod
    def extract_repo_name(repo_id):
        return os.path.basename(repo_id)

    def __init__(self, repo_id, clone_url=None, owner=None, desc=None,
                 homepage=None):
        self._repo_id = repo_id
        self._repo_name = self.extract_repo_name(repo_id)
        self._clone_url = clone_url
        self._owner = owner
        self._desc = desc
        self._homepage = homepage

    def fill_defaults(self, config):
        if self._owner is None:
            self._owner = config.default_owner

    def validate(self):
        if self.clone_url is None:
            raise RuntimeError('upstream repository URL must be specified')

    @property
    def repo_id(self):
        return self._repo_id

    @property
    def repo_name(self):
        return self._repo_name

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
        return self.repo_name

    @property
    def homepage(self):
        return self._homepage


class HostedRepo(Repo, abc.ABC):
    def __init__(self, repo_id, owner=None, desc=None, homepage=None,
                 user=None, via_ssh=True):
        super().__init__(repo_id, clone_url=None, owner=owner, desc=desc,
                         homepage=homepage)
        self._user = user
        self._via_ssh = via_ssh

    def fill_defaults(self, config):
        super().fill_defaults(config)
        self._via_ssh = config.via_ssh

    def validate(self):
        super().validate()
        if self.user is None:
            raise RuntimeError(f'neither explicit or default {self.provider_name} username was specified')

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


class GitHub(HostedRepo):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self._access_token = None

    def fill_defaults(self, config):
        super().fill_defaults(config)
        if self._user is None:
            self._user = config.github_username
        self._access_token = config.github_access_token

    @property
    def provider_name(self):
        return 'GitHub'

    @property
    def homepage(self):
        return f'https://github.com/{self.user}/{self.repo_name}'

    @property
    def clone_url_ssh(self):
        return f'ssh://git@github.com/{self.user}/{self.repo_name}.git'

    @property
    def clone_url_https(self):
        if self._access_token is None:
            auth = ''
        else:
            auth = f'{self._access_token}@'
        return f'https://{auth}github.com/{self.user}/{self.repo_name}.git'


class Bitbucket(HostedRepo):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self._app_password = None

    def fill_defaults(self, config):
        super().fill_defaults(config)
        if self._user is None:
            self._user = config.bitbucket_username
        self._app_password = config.bitbucket_app_password

    @property
    def provider_name(self):
        return 'Bitbucket'

    @property
    def homepage(self):
        return f'https://bitbucket.org/{self.user}/{self.repo_name.lower()}'

    @property
    def clone_url_ssh(self):
        return f'ssh://git@bitbucket.org/{self.user}/{self.repo_name}.git'

    @property
    def clone_url_https(self):
        if self._app_password is None:
            auth = ''
        else:
            auth = f'{self.user}:{self._app_password}@'
        return f'https://{auth}bitbucket.org/{self.user}/{self.repo_name}.git'
