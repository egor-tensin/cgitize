# Copyright (c) 2021 Egor Tensin <Egor.Tensin@gmail.com>
# This file is part of the "cgitize" project.
# For details, see https://github.com/egor-tensin/cgitize.
# Distributed under the MIT License.

import configparser
import importlib
import logging
import os.path
import sys

from cgitize.utils import chdir


class Config:
    DEFAULT_PATH = '/etc/cgitize/cgitize.conf'
    DEFAULT_OUTPUT_DIR = '/var/tmp/cgitize/output'
    DEFAULT_MY_REPOS_PATH = '/etc/cgitize/my_repos.py'

    @staticmethod
    def read(path):
        return Config(path)

    def __init__(self, path):
        self.path = os.path.abspath(path)
        self.impl = configparser.ConfigParser()
        self.impl.read(path)

    def _resolve_relative(self, path):
        if os.path.isabs(path):
            return path
        with chdir(os.path.dirname(self.path)):
            path = os.path.abspath(path)
            return path

    @property
    def output(self):
        path = self.impl.get('DEFAULT', 'output', fallback=Config.DEFAULT_OUTPUT_DIR)
        return self._resolve_relative(path)

    @property
    def clone_url(self):
        return self.impl.get('DEFAULT', 'clone_url', fallback=None)

    @property
    def default_owner(self):
        return self.impl.get('DEFAULT', 'owner', fallback=None)

    @property
    def via_ssh(self):
        return self.impl.getboolean('DEFAULT', 'ssh', fallback=True)

    @property
    def github_username(self):
        return self.impl.get('GITHUB', 'username', fallback=None)

    @property
    def github_access_token(self):
        return self.impl.get('GITHUB', 'access_token', fallback=None)

    @property
    def bitbucket_username(self):
        return self.impl.get('BITBUCKET', 'username', fallback=None)

    @property
    def bitbucket_app_password(self):
        return self.impl.get('BITBUCKET', 'app_password', fallback=None)

    @property
    def my_repos(self):
        path = self.impl.get('DEFAULT', 'my_repos', fallback=Config.DEFAULT_MY_REPOS_PATH)
        return self._resolve_relative(path)

    def import_my_repos(self):
        sys.path.append(os.path.dirname(self.my_repos))
        if not os.path.exists(self.my_repos):
            logging.error("Couldn't find my_repos.py at: %s", self.my_repos)
            return None
        module_name = os.path.splitext(os.path.basename(self.my_repos))[0]
        module = importlib.import_module(module_name)
        return module.MY_REPOS
