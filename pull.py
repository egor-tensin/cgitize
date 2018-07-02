#!/usr/bin/env python3

import contextlib
from enum import Enum
import logging
import os
import os.path
import shutil
import socket
import sys
import subprocess

env = os.environ.copy()
env['GIT_SSH_COMMAND'] = 'ssh -oStrictHostKeyChecking=no -oBatchMode=yes'

CGIT_CLONE_USER = 'egor'
CGIT_CLONE_HOST = 'tensin-ext1.home'
CGIT_CLONE_IP = '127.0.0.1'

REPOS_DIR = 'repos'

DEFAULT_OWNER = 'Egor Tensin'
DEFAULT_GITHUB_USER = 'egor-tensin'
DEFAULT_BITBUCKET_USER = 'egor-tensin'


def set_up_logging():
    logging.basicConfig(
        level=logging.DEBUG,
        datefmt='%Y-%m-%d %H:%M:%S',
        format='%(asctime)s | %(levelname)s | %(message)s')


def make_dir(rel_path):
    script_path = os.path.abspath(__file__)
    script_dir = os.path.dirname(script_path)
    abs_path = os.path.join(script_dir, rel_path)
    os.makedirs(abs_path, exist_ok=True)
    return abs_path


@contextlib.contextmanager
def chdir(new_cwd):
    old_cwd = os.getcwd()
    os.chdir(new_cwd)
    try:
        yield
    finally:
        os.chdir(old_cwd)


def extract_repo_name(repo_id):
    return os.path.basename(repo_id)


def check_output(*args, stdout=subprocess.PIPE):
    result = subprocess.run(args, stdout=stdout, stderr=subprocess.STDOUT,
                            env=env, encoding='utf-8')
    try:
        result.check_returncode()
        if result.stdout is None:
            logging.debug('%s', args)
        else:
            logging.debug('%s\n%s', args, result.stdout)
        return result.returncode == 0, result.stdout
    except subprocess.CalledProcessError as e:
        logging.error('%s\n%s', e, e.output)
        return e.returncode == 0, e.output


def run(*args, discard_output=False):
    if discard_output:
        success, _ = check_output(*args, stdout=subprocess.DEVNULL)
    else:
        success, _ = check_output(*args)
    return success


class RepoVerdict(Enum):
    SHOULD_MIRROR = 1
    SHOULD_UPDATE = 2
    CANT_DECIDE = 3


class Repo:
    def __init__(self, repo_id, clone_url, owner=None, desc=None,
                 homepage=None):
        self.repo_id = repo_id
        self.repo_name = extract_repo_name(repo_id)
        self.repo_dir = os.path.join(REPOS_DIR, self.repo_id)
        self.clone_url = clone_url
        if owner is None:
            owner = DEFAULT_OWNER
        self.owner = owner
        if desc is None:
            if homepage is not None:
                desc = homepage
            elif clone_url is not None:
                desc = clone_url
            else:
                desc = self.repo_name
        self.desc = desc
        self.homepage = homepage

    def write_cgitrc(self):
        with open(self.get_cgitrc_path(), 'w') as fd:
            self.write_cgitrc_field(fd, 'clone-url', self.build_cgitrc_clone_url())
            self.write_cgitrc_field(fd, 'owner', self.owner)
            self.write_cgitrc_field(fd, 'desc', self.desc)
            self.write_cgitrc_field(fd, 'homepage', self.homepage)

    def build_cgitrc_clone_url(self):
        clone_urls = []
        if self.clone_url is not None:
            clone_urls.append(self.clone_url)
        clone_urls.append(self.build_cgit_clone_url())
        clone_urls = ' '.join(clone_urls)
        return clone_urls

    def write_cgitrc_field(self, fd, field, value):
        if value is None:
            return
        fd.write(f'{field}={value}\n')

    def build_cgit_clone_url(self):
        return f'http://{CGIT_CLONE_USER}@{CGIT_CLONE_IP}:8080/git/{self.repo_id}'

    def get_cgitrc_path(self):
        return os.path.join(self.repo_dir, 'cgitrc')

    def pull(self):
        success = False
        verdict = self.judge()
        if verdict is RepoVerdict.SHOULD_MIRROR:
            success = self.mirror()
        elif verdict is RepoVerdict.SHOULD_UPDATE:
            success = self.update()
        elif verdict is RepoVerdict.CANT_DECIDE:
            success = False
        else:
            raise NotImplementedError(f'Unknown repository verdict: {verdict}')
        if success:
            self.write_cgitrc()
        return success

    def judge(self):
        if not os.path.isdir(self.repo_dir):
            return RepoVerdict.SHOULD_MIRROR
        with chdir(self.repo_dir):
            if not run('git', 'rev-parse', '--is-inside-work-tree', discard_output=True):
                # What is this directory?
                return RepoVerdict.SHOULD_MIRROR
            success, output = check_output('git', 'config', '--get', 'remote.origin.url')
            if not success:
                # Every repository managed by this script should have the
                # 'origin' remote. If it doesn't, it's trash.
                return RepoVerdict.SHOULD_MIRROR
            if f'{self.clone_url}\n' != output:
                logging.warning("Existing repository '%s' URL doesn't match" \
                                " the specified clone URL: %s", self.repo_id,
                                self.clone_url)
                return RepoVerdict.CANT_DECIDE
            # Looks like a legit clone of the specified remote.
            return RepoVerdict.SHOULD_UPDATE

    def mirror(self):
        logging.info("Mirroring repository '%s' from: %s", self.repo_id,
                     self.clone_url)
        if os.path.isdir(self.repo_dir):
            try:
                shutil.rmtree(self.repo_dir)
            except Exception as e:
                logging.exception(e)
                return False
        return run('git', 'clone', '--mirror', self.clone_url, self.repo_dir)

    def update(self):
        logging.info("Updating repository '%s'", self.repo_id)
        with chdir(self.repo_dir):
            return run('git', 'remote', 'update', '--prune')


class GithubRepo(Repo):
    def __init__(self, repo_id, clone_url=None, owner=None, desc=None,
                 homepage=None, github_user=DEFAULT_GITHUB_USER):
        if clone_url is None:
            clone_url = self.build_clone_url(github_user, repo_id)
        if homepage is None:
            homepage = self.build_homepage_url(github_user, repo_id)
        super().__init__(repo_id, clone_url, owner=owner, desc=desc,
                         homepage=homepage)

    @staticmethod
    def build_clone_url(user, repo_id):
        name = extract_repo_name(repo_id)
        return f'ssh://git@github.com/{user}/{name}.git'

    @staticmethod
    def build_homepage_url(user, repo_id):
        name = extract_repo_name(repo_id)
        return f'https://github.com/egor-tensin/{name}'


class BitbucketRepo(Repo):
    def __init__(self, repo_id, clone_url=None, owner=None, desc=None,
                 homepage=None, bitbucket_user=DEFAULT_BITBUCKET_USER):
        if clone_url is None:
            clone_url = self.build_clone_url(bitbucket_user, repo_id)
        if homepage is None:
            homepage = self.build_homepage_url(bitbucket_user, repo_id)
        super().__init__(repo_id, clone_url, owner=owner, desc=desc,
                         homepage=homepage)

    @staticmethod
    def build_clone_url(user, repo_id):
        name = extract_repo_name(repo_id)
        return f'ssh://git@bitbucket.org/{user}/{name}.git'

    @staticmethod
    def build_homepage_url(user, repo_id):
        name = extract_repo_name(repo_id)
        return f'https://bitbucket.org/egor-tensin/{name.lower()}'


repos = (
    GithubRepo('personal/aes-tools'),
    GithubRepo('personal/blog'),
    GithubRepo('personal/chess-games'),
    GithubRepo('personal/cmake-common'),
    GithubRepo('personal/config-links'),
    GithubRepo('personal/cv'),
    GithubRepo('personal/egor-tensin.github.io'),
    GithubRepo('personal/filters'),
    GithubRepo('personal/linux-home'),
    GithubRepo('personal/linux-status'),
    GithubRepo('personal/notes'),
    GithubRepo('personal/pdb-repo'),
    GithubRepo('personal/privilege-check'),
    GithubRepo('personal/simple-interpreter'),
    GithubRepo('personal/sorting-algorithms'),
    GithubRepo('personal/vk-scripts'),
    GithubRepo('personal/windows-env'),
    GithubRepo('personal/windows-home'),
    GithubRepo('personal/windows-tmp'),
    GithubRepo('personal/windows7-drivers'),
    GithubRepo('personal/writable-dirs'),

    BitbucketRepo('etc/etc-tensin-laptop1'),
    BitbucketRepo('etc/etc-tensin-laptop2'),
    BitbucketRepo('etc/etc-tensin-pc1'),
    BitbucketRepo('etc/etc-tensin-raspi1'),
    BitbucketRepo('etc/etc-tensin-raspi2'),
    BitbucketRepo('fr24/fr24-cover-letter'),
    BitbucketRepo('fr24/fr24-home'),
    BitbucketRepo('fr24/fr24-tmp'),
    BitbucketRepo('netwrix/etc-wiki'),
    BitbucketRepo('netwrix/netwrix-copyright'),
    BitbucketRepo('netwrix/netwrix-lab'),
    BitbucketRepo('netwrix/netwrix-logs'),
    #BitbucketRepo('netwrix/netwrix-webapi'),
    BitbucketRepo('netwrix/netwrix-xml'),
    BitbucketRepo('netwrix/netwrix.sh'),
    BitbucketRepo('netwrix/wiki-backup'),
    BitbucketRepo('shadow'),
    BitbucketRepo('staging/361_Tensin_E_D_report'),
    BitbucketRepo('staging/361_Tensin_E_D_slides'),
    BitbucketRepo('staging/461_Tensin_E_D_report'),
    BitbucketRepo('staging/461_Tensin_E_D_slides'),
    BitbucketRepo('staging/cgit-repos'),
    BitbucketRepo('staging/deposit-calculator'),
    BitbucketRepo('staging/raspi-temp-client'),
    BitbucketRepo('staging/raspi-temp-server'),
    BitbucketRepo('staging/x64-decoder'),

    Repo('fr24/key_mgmt', 'ssh://egor@tensin-raspi2/~/tmp/key_mgmt.git'),
    Repo('fr24/openfortivpn', 'ssh://egor@tensin-raspi2/~/tmp/openfortivpn.git'),
)


def main():
    set_up_logging()
    try:
        global REPOS_DIR
        REPOS_DIR = make_dir(REPOS_DIR)
        global CGIT_CLONE_IP
        CGIT_CLONE_IP = socket.gethostbyname(CGIT_CLONE_HOST)
        success = True
        for repo in repos:
            if not repo.pull():
                success = False
        if success:
            logging.info('All repositories were updated successfully')
            return 0
        else:
            logging.warning("Some repositories couldn't be updated!")
            return 1
    except Exception as e:
        logging.exception(e)
        raise


if __name__ == '__main__':
    sys.exit(main())
