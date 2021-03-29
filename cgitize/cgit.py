# Copyright (c) 2018 Egor Tensin <Egor.Tensin@gmail.com>
# This file is part of the "cgitize" project.
# For details, see https://github.com/egor-tensin/cgitize.
# Distributed under the MIT License.

from contextlib import contextmanager
import logging
import os
import os.path
import shutil
import stat

from cgitize.git import Git
from cgitize.utils import chdir


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


class CGitServer:
    def __init__(self, clone_url):
        self.clone_url = clone_url

    def get_clone_url(self, repo):
        if self.clone_url is None:
            return None
        return self.clone_url.format(repo_id=repo.repo_id)


class CGitRCWriter:
    def __init__(self, cgit_server):
        self.cgit_server = cgit_server

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
        cgit_clone_url = self.cgit_server.get_clone_url(repo)
        if cgit_clone_url is not None:
            clone_urls.append(cgit_clone_url)
        if not clone_urls:
            return None
        clone_urls = ' '.join(clone_urls)
        return clone_urls


class CGitRepositories:
    def __init__(self, dir, cgit_server):
        self.dir = self._make_dir(dir)
        self.cgitrc = CGitRCWriter(cgit_server)

    @staticmethod
    def _make_dir(rel_path):
        abs_path = os.path.abspath(rel_path)
        os.makedirs(abs_path, exist_ok=True)
        return abs_path

    def get_repo_dir(self, repo):
        return os.path.join(self.dir, repo.repo_id)

    def get_cgitrc_path(self, repo):
        return os.path.join(self.get_repo_dir(repo), 'cgitrc')

    def update(self, repo):
        success = self._mirror_or_update(repo)
        if success:
            self.cgitrc.write(self.get_cgitrc_path(repo), repo)
        return success

    def _mirror_or_update(self, repo):
        repo_dir = self.get_repo_dir(repo)

        if not os.path.isdir(repo_dir):
            # The local directory doesn't exist, mirror the new repository.
            return self._mirror(repo)

        with chdir(repo_dir):
            if not Git.check('rev-parse', '--is-inside-work-tree'):
                # Overwrite the existing directory if it's not a Git repository.
                logging.warning('Local directory is not a repository, going to overwrite it: %s', repo_dir)
                return self._mirror(repo)

            success, output = Git.capture('config', '--get', 'remote.origin.url')
            if not success:
                # Every repository managed by this script should have the
                # 'origin' remote. If it doesn't, it's trash. Overwrite the
                # existing directory, mirroring the repository in it.
                logging.warning("Local repository doesn't have remote 'origin', going to overwrite it: %s", repo_dir)
                return self._mirror(repo)

            if f'{repo.clone_url}\n' != output:
                # Jeez, there's a proper local repository in the target
                # directory already with a different upstream; something's
                # wrong, fix it manually.
                logging.warning("Existing repository '%s' doesn't match the specified clone URL: %s", repo.repo_id, repo.clone_url)
                return False

            # The local directory contains the local version of the upstream,
            # update it.
            return self._update_existing(repo)

    def _mirror(self, repo):
        logging.info("Mirroring repository '%s' from: %s", repo.repo_id, repo.clone_url)
        repo_dir = self.get_repo_dir(repo)
        if os.path.isdir(repo_dir):
            try:
                shutil.rmtree(repo_dir)
            except Exception as e:
                logging.exception(e)
                return False
        with setup_git_auth(repo):
            return Git.check('clone', '--mirror', '--quiet', repo.clone_url, repo_dir)

    def _update_existing(self, repo):
        logging.info("Updating repository '%s'", repo.repo_id)
        repo_dir = self.get_repo_dir(repo)
        with chdir(repo_dir):
            with setup_git_auth(repo):
                if not Git.check('remote', 'update', '--prune'):
                    return False
            # In case the local repository is not a bare repository, but a
            # full-fledged working copy:
            if Git.check('rev-parse', '--verify', '--quiet', 'origin/master'):
                return Git.check('reset', '--soft', 'origin/master')
            return True
