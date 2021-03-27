# Copyright (c) 2018 Egor Tensin <Egor.Tensin@gmail.com>
# This file is part of the "cgitize" project.
# For details, see https://github.com/egor-tensin/cgitize.
# Distributed under the MIT License.

import abc
import os.path


class Repo:
    DEFAULT_OWNER = None
    DEFAULT_VIA_SSH = True

    @staticmethod
    def extract_repo_name(repo_id):
        return os.path.basename(repo_id)

    def __init__(self, repo_id, clone_url, owner=None, desc=None,
                 homepage=None):
        self.repo_id = repo_id
        self.repo_name = self.extract_repo_name(repo_id)
        self.clone_url = clone_url
        if owner is None:
            owner = Repo.DEFAULT_OWNER
        self.owner = owner
        if desc is None:
            if homepage is not None:
                desc = homepage
            elif clone_url is not None:
                desc = clone_url
            else:
                desc = self.repo_name
        self.desc = desc
        self.homepage = homepage


class HostedRepo(Repo, abc.ABC):
    def __init__(self, repo_id, clone_url=None, owner=None, desc=None,
                 homepage=None, user=None, via_ssh=None):
        user = user or self.get_default_user()
        if user is None:
            raise RuntimeError(f'neither explicit or default {self.provider_name()} username was provided')
        name = Repo.extract_repo_name(repo_id)
        if clone_url is None:
            if via_ssh is None:
                via_ssh = Repo.DEFAULT_VIA_SSH
            if via_ssh:
                clone_url = self.build_clone_url_ssh(user, name)
            else:
                clone_url = self.build_clone_url_https(user, name)
        if homepage is None:
            homepage = self.build_homepage_url(user, name)
        super().__init__(repo_id, clone_url, owner=owner, desc=desc,
                         homepage=homepage)

    @abc.abstractmethod
    def provider_name(self):
        pass

    @abc.abstractmethod
    def get_default_user(self):
        pass

    @abc.abstractmethod
    def build_clone_url_ssh(self, user, name):
        pass

    @abc.abstractmethod
    def build_clone_url_https(self, user, name):
        pass

    @abc.abstractmethod
    def build_homepage_url(self, user, name):
        pass


class GithubRepo(HostedRepo):
    DEFAULT_USER = None

    def provider_name(self):
        return 'GitHub'

    def get_default_user(self):
        return GithubRepo.DEFAULT_USER

    def build_clone_url_ssh(self, user, name):
        return f'ssh://git@github.com/{user}/{name}.git'

    def build_clone_url_https(self, user, name):
        return f'https://github.com/{user}/{name}.git'

    def build_homepage_url(self, user, name):
        return f'https://github.com/{user}/{name}'


class BitbucketRepo(HostedRepo):
    DEFAULT_USER = None

    def provider_name(self):
        return 'Bitbucket'

    def get_default_user(self):
        return BitbucketRepo.DEFAULT_USER

    def build_clone_url_ssh(self, user, name):
        return f'ssh://git@bitbucket.org/{user}/{name}.git'

    def build_clone_url_https(self, user, name):
        return f'https://bitbucket.org/{user}/{name}.git'

    def build_homepage_url(self, user, name):
        return f'https://bitbucket.org/{user}/{name.lower()}'
