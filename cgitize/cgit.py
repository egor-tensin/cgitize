# Copyright (c) 2018 Egor Tensin <Egor.Tensin@gmail.com>
# This file is part of the "cgitize" project.
# For details, see https://github.com/egor-tensin/cgitize.
# Distributed under the MIT License.

from contextlib import contextmanager
from enum import Enum
import logging
import os
import os.path
import shutil
import stat

import cgitize.utils as utils


GIT_ENV = os.environ.copy()
GIT_ENV['GIT_SSH_COMMAND'] = 'ssh -oBatchMode=yes -oLogLevel=QUIET -oStrictHostKeyChecking=no -oUserKnownHostsFile=/dev/null'


def git(*args, **kwargs):
    return utils.run('git', *args, env=GIT_ENV, **kwargs)


def git_stdout(*args, **kwargs):
    return utils.check_output('git', *args, env=GIT_ENV, **kwargs)


@contextmanager
def setup_git_auth(repo):
    if not repo.url_auth:
        yield
        return
    config_path = os.path.expanduser('~/.gitconfig')
    exists = os.path.exists(config_path)
    if exists:
        old_permissions = stat.S_IMODE(os.stat(config_path).st_mode)
        new_permissions = stat.S_IRUSR | stat.S_IWUSR # 0x600
        os.chmod(config_path, new_permissions)
        with open(config_path, encoding='utf-8', mode='r') as fd:
            old_contents = fd.read()
    else:
        old_contents = ''
    new_contents = f'''{old_contents}
[url "{repo.clone_url_with_auth}"]
    insteadOf = {repo.clone_url}
'''
    with open(config_path, encoding='utf-8', mode='w') as fd:
        fd.write(new_contents)
    try:
        yield
    finally:
        if exists:
            with open(config_path, encoding='utf-8', mode='w') as fd:
                fd.write(old_contents)
            os.chmod(config_path, old_permissions)
        else:
            os.unlink(config_path)


class CGit:
    def __init__(self, clone_url):
        self.clone_url = clone_url

    def get_clone_url(self, repo):
        if self.clone_url is None:
            return None
        return self.clone_url.format(repo_id=repo.repo_id)


class CGitRC:
    def __init__(self, cgit):
        self.cgit = cgit

    def write(self, path, repo):
        with open(path, 'w') as fd:
            self._write_field(fd, 'clone-url', self._build_clone_url(repo))
            self._write_field(fd, 'owner', repo.owner)
            self._write_field(fd, 'desc', repo.desc)
            self._write_field(fd, 'homepage', repo.homepage)

    @staticmethod
    def _write_field(fd, field, value):
        if value is None:
            return
        fd.write(f'{field}={value}\n')

    def _build_clone_url(self, repo):
        clone_urls = []
        if repo.clone_url is not None:
            clone_urls.append(repo.clone_url)
        cgit_clone_url = self.cgit.get_clone_url(repo)
        if cgit_clone_url is not None:
            clone_urls.append(cgit_clone_url)
        if not clone_urls:
            return None
        clone_urls = ' '.join(clone_urls)
        return clone_urls


class Output:
    def __init__(self, output_dir, cgit):
        self.output_dir = self._make_dir(output_dir)
        self.cgitrc = CGitRC(cgit)

    @staticmethod
    def _make_dir(rel_path):
        abs_path = os.path.abspath(rel_path)
        os.makedirs(abs_path, exist_ok=True)
        return abs_path

    def get_repo_dir(self, repo):
        return os.path.join(self.output_dir, repo.repo_id)

    def get_cgitrc_path(self, repo):
        return os.path.join(self.get_repo_dir(repo), 'cgitrc')

    def pull(self, repo):
        success = False
        verdict = self.judge(repo)
        if verdict is RepoVerdict.SHOULD_MIRROR:
            success = self.mirror(repo)
        elif verdict is RepoVerdict.SHOULD_UPDATE:
            success = self.update(repo)
        elif verdict is RepoVerdict.CANT_DECIDE:
            success = False
        else:
            raise NotImplementedError(f'Unknown repository verdict: {verdict}')
        if success:
            self.cgitrc.write(self.get_cgitrc_path(repo), repo)
        return success

    def judge(self, repo):
        repo_dir = self.get_repo_dir(repo)
        if not os.path.isdir(repo_dir):
            return RepoVerdict.SHOULD_MIRROR
        with utils.chdir(repo_dir):
            if not git('rev-parse', '--is-inside-work-tree', discard_output=True):
                logging.warning('Not a repository, so going to mirror: %s', repo_dir)
                return RepoVerdict.SHOULD_MIRROR
            success, output = git_stdout('config', '--get', 'remote.origin.url')
            if not success:
                # Every repository managed by this script should have the
                # 'origin' remote. If it doesn't, it's trash.
                return RepoVerdict.SHOULD_MIRROR
            if f'{repo.clone_url}\n' != output:
                logging.warning("Existing repository '%s' URL doesn't match the specified clone" \
                                " URL: %s", repo.repo_id, repo.clone_url)
                return RepoVerdict.CANT_DECIDE
            # Looks like a legit clone of the specified remote.
            return RepoVerdict.SHOULD_UPDATE

    def mirror(self, repo):
        logging.info("Mirroring repository '%s' from: %s", repo.repo_id,
                     repo.clone_url)
        repo_dir = self.get_repo_dir(repo)
        if os.path.isdir(repo_dir):
            try:
                shutil.rmtree(repo_dir)
            except Exception as e:
                logging.exception(e)
                return False
        with setup_git_auth(repo):
            return git('clone', '--mirror', repo.clone_url, repo_dir)

    def update(self, repo):
        logging.info("Updating repository '%s'", repo.repo_id)
        repo_dir = self.get_repo_dir(repo)
        with utils.chdir(repo_dir):
            with setup_git_auth(repo):
                if not git('remote', 'update', '--prune'):
                    return False
            if git('rev-parse', '--verify', '--quiet', 'origin/master', discard_output=True):
                if not git('reset', '--soft', 'origin/master'):
                    return False
            return True


class RepoVerdict(Enum):
    SHOULD_MIRROR = 1
    SHOULD_UPDATE = 2
    CANT_DECIDE = 3
