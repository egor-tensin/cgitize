# Copyright (c) 2021 Egor Tensin <Egor.Tensin@gmail.com>
# This file is part of the "cgitize" project.
# For details, see https://github.com/egor-tensin/cgitize.
# Distributed under the MIT License.

import logging

from github import Github, GithubException

from cgitize.repo import Repo


class GitHub:
    def __init__(self, token):
        self._impl = Github(token)

    def get_repo(self, repo):
        try:
            return self._impl.get_repo(repo.id)
        except GithubException:
            logging.error("Couldn't fetch repository: %s", repo.id)
            raise

    def get_user_repos(self, user):
        try:
            return self._impl.get_user(user.name).get_repos()
        except GithubException:
            logging.error("Couldn't fetch user repositories: %s", user.name)
            raise

    def get_org_repos(self, org):
        try:
            return self._impl.get_organization(org.name).get_repos()
        except GithubException:
            logging.error("Couldn't fetch organization repositories: %s", org.name)
            raise

    @staticmethod
    def convert_repo(repo, *args, **kwargs):
        return Repo.from_github(repo, *args, **kwargs)
