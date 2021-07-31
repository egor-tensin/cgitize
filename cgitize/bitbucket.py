# Copyright (c) 2021 Egor Tensin <Egor.Tensin@gmail.com>
# This file is part of the "cgitize" project.
# For details, see https://github.com/egor-tensin/cgitize.
# Distributed under the MIT License.

import logging

from atlassian.bitbucket.cloud import Cloud
from requests.exceptions import HTTPError


class Bitbucket:
    def __init__(self, username=None, password=None):
        self._impl = Cloud(username=username, password=password, cloud=True)

    def get_repo(self, repo):
        if 'id' not in repo:
            raise ValueError('every Bitbucket repository must have an ID')
        repo_id = repo['id']
        try:
            return self._impl.repositories.get(repo_id)
        except HTTPError:
            logging.error("Couldn't fetch repository: %s", repo_id)
            raise
