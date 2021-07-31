# Copyright (c) 2021 Egor Tensin <Egor.Tensin@gmail.com>
# This file is part of the "cgitize" project.
# For details, see https://github.com/egor-tensin/cgitize.
# Distributed under the MIT License.

import logging

from github import Github, GithubException


class GitHub:
    def __init__(self, access_token):
        self._impl = Github(access_token)

    def get_repo(self, repo):
        if 'id' not in repo:
            raise ValueError('every GitHub repository must have an ID')
        repo_id = repo['id']
        try:
            return self._impl.get_repo(repo_id)
        except GithubException:
            logging.error("Couldn't fetch repository: %s", repo_id)
            raise
