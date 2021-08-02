# Copyright (c) 2021 Egor Tensin <Egor.Tensin@gmail.com>
# This file is part of the "cgitize" project.
# For details, see https://github.com/egor-tensin/cgitize.
# Distributed under the MIT License.

import logging

from atlassian.bitbucket.cloud import Cloud
from requests.exceptions import HTTPError

from cgitize.repo import Repo


class Bitbucket:
    def __init__(self, username=None, password=None):
        self._impl = Cloud(username=username, password=password, cloud=True)

    def get_repo(self, repo):
        try:
            return self._impl.repositories.get(repo.id)
        except HTTPError:
            logging.error("Couldn't fetch repository: %s", repo.id)
            raise

    def get_user_repos(self, user):
        try:
            page = 1
            while True:
                params = {'page': page}
                response = self._impl.repositories.get(user.name, params=params)
                yield from iter(response['values'])
                if 'next' not in response:
                    break
                page += 1
        except HTTPError:
            logging.error("Couldn't fetch user repositories: %s", user.name)
            raise

    @staticmethod
    def convert_repo(repo, *args, **kwargs):
        return Repo.from_bitbucket(repo, *args, **kwargs)
