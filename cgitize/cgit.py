# Copyright (c) 2018 Egor Tensin <Egor.Tensin@gmail.com>
# This file is part of the "cgitize" project.
# For details, see https://github.com/egor-tensin/cgitize.
# Distributed under the MIT License.

import logging
import os
import shutil

from cgitize.git import Git
from cgitize.utils import chdir


class CGitServer:
    def __init__(self, clone_url):
        self.clone_url = clone_url

    def get_clone_url(self, repo):
        if self.clone_url is None:
            return None
        return self.clone_url.format(repo=repo.url_path)


class CGitRCWriter:
    def __init__(self, cgit_server):
        self.cgit_server = cgit_server

    @staticmethod
    def get_path(repo_dir):
        return os.path.join(repo_dir, 'cgitrc')

    def write(self, repo_dir, repo):
        with open(self.get_path(repo_dir), 'w') as fd:
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


class AgeFile:
    @staticmethod
    def write(repo_dir):
        timestamp = AgeFile.get_age(repo_dir)
        if timestamp:
            os.makedirs(AgeFile.get_dir(repo_dir), exist_ok=True)
            with open(AgeFile.get_path(repo_dir), mode='w') as fd:
                fd.write(f'{timestamp}')

    @staticmethod
    def get_age(repo_dir):
        # https://git.zx2c4.com/cgit/tree/contrib/hooks/post-receive.agefile
        # Except I think that the committer date, not author date  better
        # represents activity.
        with chdir(repo_dir):
            success, output = Git.capture('for-each-ref', '--sort=-committerdate', '--count=1', '--format=%(committerdate:iso8601)')
            if not success:
                logging.error("Couldn't get the timestamp of the newest commit in repository: %s", repo_dir)
                return None
            return output

    @staticmethod
    def get_dir(repo_dir):
        return os.path.join(repo_dir, 'info', 'web')

    @staticmethod
    def get_path(repo_dir):
        return os.path.join(AgeFile.get_dir(repo_dir), 'last-modified')


class CGitRepositories:
    def __init__(self, output_dir, cgit_server, force=False):
        self.dir = self._make_dir(output_dir)
        self.cgitrc = CGitRCWriter(cgit_server)
        self.force = force

    @staticmethod
    def _make_dir(rel_path):
        abs_path = os.path.abspath(rel_path)
        os.makedirs(abs_path, exist_ok=True)
        return abs_path

    def get_repo_dir(self, repo):
        return os.path.join(self.dir, repo.dir)

    def update(self, repo):
        success = self._mirror_or_update(repo)
        if success:
            self.cgitrc.write(self.get_repo_dir(repo), repo)
            AgeFile.write(self.get_repo_dir(repo))
        return success

    def _mirror_or_update(self, repo):
        repo_dir = self.get_repo_dir(repo)

        if not os.path.isdir(repo_dir):
            # The local directory doesn't exist, mirror the new repository.
            return self._mirror(repo)

        with chdir(repo_dir):
            success, output = Git.capture('rev-parse', '--is-inside-work-tree')
            if not success:
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
                logging.warning("Existing repository '%s' doesn't match the specified clone URL: %s", repo.name, repo.clone_url)
                if self.force:
                    # Unless --force was specified, in which case we overwrite
                    # the repository.
                    return self._fix_upstream_url(repo) and self._update_existing(repo)
                return False

            # The local directory contains the local version of the upstream,
            # update it.
            return self._update_existing(repo)

    def _mirror(self, repo):
        logging.info("Mirroring repository '%s' from: %s", repo.name, repo.clone_url)
        repo_dir = self.get_repo_dir(repo)
        if os.path.isdir(repo_dir):
            try:
                shutil.rmtree(repo_dir)
            except Exception as e:
                logging.exception(e)
                return False
        with Git.setup_auth(repo):
            return Git.check('clone', '--mirror', '--quiet', repo.clone_url, repo_dir)

    def _fix_upstream_url(self, repo):
        repo_dir = self.get_repo_dir(repo)
        with chdir(repo_dir):
            return Git.check('remote', 'set-url', 'origin', repo.clone_url)

    def _update_existing(self, repo):
        logging.info("Updating repository '%s'", repo.name)
        repo_dir = self.get_repo_dir(repo)
        with chdir(repo_dir):
            with Git.setup_auth(repo):
                if not Git.check('remote', 'update', '--prune'):
                    return False
            # In case the local repository is not a bare repository, but a
            # full-fledged working copy:
            if Git.check('rev-parse', '--verify', '--quiet', 'origin/master'):
                return Git.check('reset', '--soft', 'origin/master')
            return True
