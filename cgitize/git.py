# Copyright (c) 2021 Egor Tensin <Egor.Tensin@gmail.com>
# This file is part of the "cgitize" project.
# For details, see https://github.com/egor-tensin/cgitize.
# Distributed under the MIT License.

from contextlib import contextmanager
import os

import cgitize.utils as utils


GIT_ENV = os.environ.copy()
GIT_ENV['GIT_SSH_COMMAND'] = 'ssh -oBatchMode=yes -oLogLevel=QUIET -oStrictHostKeyChecking=no -oUserKnownHostsFile=/dev/null'


class Config:
    def __init__(self, path):
        self.path = path

    def exists(self):
        return os.path.exists(self.path)

    def open(self, mode='r'):
        return open(self.path, mode=mode, encoding='utf-8')

    def read(self):
        with self.open(mode='r') as fd:
            return fd.read()

    def write(self, contents):
        with self.open(mode='w') as fd:
            fd.write(contents)

    @contextmanager
    def backup(self):
        old_contents = self.read()
        try:
            yield old_contents
        finally:
            self.write(old_contents)


class Git:
    EXE = 'git'

    @staticmethod
    def check(*args, **kwargs):
        return utils.try_run(Git.EXE, *args, env=GIT_ENV, **kwargs)

    @staticmethod
    def capture(*args, **kwargs):
        return utils.try_run_capture(Git.EXE, *args, env=GIT_ENV, **kwargs)

    @staticmethod
    def get_global_config():
        return Config(os.path.expanduser('~/.gitconfig'))

    @staticmethod
    @contextmanager
    def setup_auth(repo):
        if not repo.url_auth:
            yield
            return
        config = Git.get_global_config()
        with utils.protected_file(config.path):
            with config.backup() as old_contents:
                new_contents = f'''{old_contents}
[url "{repo.clone_url_with_auth}"]
    insteadOf = {repo.clone_url}
'''
                config.write(new_contents)
                yield
