# Copyright (c) 2021 Egor Tensin <Egor.Tensin@gmail.com>
# This file is part of the "cgitize" project.
# For details, see https://github.com/egor-tensin/cgitize.
# Distributed under the MIT License.

import os

import cgitize.utils as utils


GIT_ENV = os.environ.copy()
GIT_ENV['GIT_SSH_COMMAND'] = 'ssh -oBatchMode=yes -oLogLevel=QUIET -oStrictHostKeyChecking=no -oUserKnownHostsFile=/dev/null'


class Git:
    EXE = 'git'

    @staticmethod
    def check(*args, **kwargs):
        return utils.try_run(Git.EXE, *args, env=GIT_ENV, **kwargs)

    @staticmethod
    def capture(*args, **kwargs):
        return utils.try_run_capture(Git.EXE, *args, env=GIT_ENV, **kwargs)
