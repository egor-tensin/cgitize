# Copyright (c) 2018 Egor Tensin <Egor.Tensin@gmail.com>
# This file is part of the "cgit repos" project.
# For details, see https://github.com/egor-tensin/cgit-repos.
# Distributed under the MIT License.

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


class GithubRepo(Repo):
    DEFAULT_USER = None

    def __init__(self, repo_id, clone_url=None, owner=None, desc=None,
                 homepage=None, user=DEFAULT_USER, via_ssh=None):
        if user is None:
            if GithubRepo.DEFAULT_USER is None:
                raise RuntimeError('neither explicit or default GitHub username was provided')
            user = GithubRepo.DEFAULT_USER
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

    @staticmethod
    def build_clone_url_ssh(user, name):
        return f'ssh://git@github.com/{user}/{name}.git'

    @staticmethod
    def build_clone_url_https(user, name):
        return f'https://github.com/{user}/{name}.git'

    @staticmethod
    def build_homepage_url(user, name):
        return f'https://github.com/{user}/{name}'


class BitbucketRepo(Repo):
    DEFAULT_USER = None

    def __init__(self, repo_id, clone_url=None, owner=None, desc=None,
                 homepage=None, user=DEFAULT_USER, via_ssh=None):
        if user is None:
            if BitbucketRepo.DEFAULT_USER is None:
                raise RuntimeError('neither explicit or default Bitbucket username was provided')
            user = BitbucketRepo.DEFAULT_USER
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

    @staticmethod
    def build_clone_url_ssh(user, name):
        return f'ssh://git@bitbucket.org/{user}/{name}.git'

    @staticmethod
    def build_clone_url_https(user, name):
        return f'https://bitbucket.org/{user}/{name}.git'

    @staticmethod
    def build_homepage_url(user, name):
        return f'https://bitbucket.org/{user}/{name.lower()}'
