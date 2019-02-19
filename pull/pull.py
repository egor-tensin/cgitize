from argparse import ArgumentParser
import contextlib
from enum import Enum
import logging
import os
import os.path
import shutil
import socket
import sys
import subprocess

from pull.registry import MY_REPOS


env = os.environ.copy()
env['GIT_SSH_COMMAND'] = 'ssh -oStrictHostKeyChecking=no -oBatchMode=yes'

DEFAULT_OUTPUT_DIR = 'output'

DEFAULT_CGIT_CLONE_USER = 'egor'
DEFAULT_CGIT_CLONE_HOST = 'tensin-ext1.home'
DEFAULT_CGIT_CLONE_PORT = 8080


def set_up_logging():
    logging.basicConfig(
        level=logging.DEBUG,
        datefmt='%Y-%m-%d %H:%M:%S',
        format='%(asctime)s | %(levelname)s | %(message)s')


def parse_args(argv=None):
    if argv is None:
        argv = sys.argv[1:]
    parser = ArgumentParser()
    parser.add_argument('--output', default=DEFAULT_OUTPUT_DIR,
                        help='output directory path')
    parser.add_argument('--cgit-user', default=DEFAULT_CGIT_CLONE_USER,
                        help='cgit clone username')
    parser.add_argument('--cgit-host', default=DEFAULT_CGIT_CLONE_HOST,
                        help='cgit clone host')
    parser.add_argument('--cgit-port', default=DEFAULT_CGIT_CLONE_PORT,
                        help='cgit clone port number', type=int)
    return parser.parse_args(argv)


def check_output(*args, stdout=subprocess.PIPE):
    result = subprocess.run(args, stdout=stdout, stderr=subprocess.STDOUT,
                            env=env, encoding='utf-8')
    try:
        result.check_returncode()
        if stdout != subprocess.DEVNULL:
            if result.stdout is None:
                logging.debug('%s', args)
            else:
                logging.debug('%s\n%s', args, result.stdout)
        return result.returncode == 0, result.stdout
    except subprocess.CalledProcessError as e:
        if stdout != subprocess.DEVNULL:
            logging.error('%s\n%s', e, e.output)
        return e.returncode == 0, e.output


def run(*args, discard_output=False):
    if discard_output:
        success, _ = check_output(*args, stdout=subprocess.DEVNULL)
    else:
        success, _ = check_output(*args)
    return success


@contextlib.contextmanager
def chdir(new_cwd):
    old_cwd = os.getcwd()
    os.chdir(new_cwd)
    try:
        yield
    finally:
        os.chdir(old_cwd)


class CGit:
    def __init__(self, user, host, port):
        self.user = user
        self.host = host
        self.ip = socket.gethostbyname(self.host)
        self.port = port

    def get_clone_url(self, repo):
        return f'http://{self.user}@{self.ip}:{self.port}/git/{repo.repo_id}'


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
        clone_urls.append(self.cgit.get_clone_url(repo))
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
        with chdir(repo_dir):
            if not run('git', 'rev-parse', '--is-inside-work-tree', discard_output=True):
                logging.warning('Not a repository, so going to mirror: %s', repo_dir)
                return RepoVerdict.SHOULD_MIRROR
            success, output = check_output('git', 'config', '--get', 'remote.origin.url')
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
        return run('git', 'clone', '--mirror', repo.clone_url, repo_dir)

    def update(self, repo):
        logging.info("Updating repository '%s'", repo.repo_id)
        repo_dir = self.get_repo_dir(repo)
        with chdir(repo_dir):
            if not run('git', 'remote', 'update', '--prune'):
                return False
            if run('git', 'rev-parse', '--verify', '--quiet', 'origin/master', discard_output=True):
                if not run('git', 'reset', '--soft', 'origin/master'):
                    return False
            return True


class RepoVerdict(Enum):
    SHOULD_MIRROR = 1
    SHOULD_UPDATE = 2
    CANT_DECIDE = 3


def main(args=None):
    set_up_logging()
    try:
        args = parse_args(args)
        cgit = CGit(args.cgit_user, args.cgit_host, args.cgit_port)
        output = Output(args.output, cgit)
        success = True
        for repo in MY_REPOS:
            if not output.pull(repo):
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
