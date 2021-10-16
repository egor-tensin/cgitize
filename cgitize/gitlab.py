# Copyright (c) 2021 Egor Tensin <Egor.Tensin@gmail.com>
# This file is part of the "cgitize" project.
# For details, see https://github.com/egor-tensin/cgitize.
# Distributed under the MIT License.

import logging

import gitlab

from cgitize.repo import Repo


class Gitlab:
    def __init__(self, access_token):
        self._impl = gitlab.Gitlab('https://gitlab.com', private_token=access_token)

    def get_repo(self, repo):
        try:
            return self._impl.projects.get(repo.id)
        except gitlab.exceptions.GitlabGetError:
            logging.error("Couldn't fetch repository: %s", repo.id)
            raise

    def get_user_repos(self, user):
        try:
            # Strictly speaking, Gitlab supports the /users/:username/projects
            # endpoint, which means you shouldn't need to fetch the user first,
            # but I don't think python-gitlab 2.10.0 supports that?
            users = self._impl.users.list(username=user.name)
            if not users:
                raise RuntimeError(f"Couldn't find Gitlab user: {user.name}")
            assert len(users) == 1
            user = users[0]
            return user.projects.list()
        except gitlab.exceptions.GitlabGetError:
            logging.error("Couldn't fetch user repositories: %s", user.name)
            raise

    @staticmethod
    def convert_repo(repo, *args, **kwargs):
        return Repo.from_gitlab(repo, *args, **kwargs)
