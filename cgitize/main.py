# Copyright (c) 2018 Egor Tensin <Egor.Tensin@gmail.com>
# This file is part of the "cgitize" project.
# For details, see https://github.com/egor-tensin/cgitize.
# Distributed under the MIT License.

from argparse import ArgumentParser
import configparser
from contextlib import contextmanager
import importlib
import logging
import os.path
import sys

from cgitize.cgit import CGit, Output
import cgitize.utils as utils


DEFAULT_OUTPUT_DIR = '/var/tmp/cgitize/output'
DEFAULT_CONFIG_PATH = '/etc/cgitize/cgitize.conf'
DEFAULT_MY_REPOS_PATH = '/etc/cgitize/my_repos.py'


@contextmanager
def setup_logging():
    logging.basicConfig(
        level=logging.DEBUG,
        datefmt='%Y-%m-%d %H:%M:%S',
        format='%(asctime)s | %(levelname)s | %(message)s')
    try:
        yield
    except Exception as e:
        logging.exception(e)
        raise


def parse_args(argv=None):
    if argv is None:
        argv = sys.argv[1:]
    parser = ArgumentParser()
    parser.add_argument('--config', metavar='PATH',
                        default=DEFAULT_CONFIG_PATH,
                        help='config file path')
    parser.add_argument('--repo', metavar='REPO_ID',
                        nargs='*', dest='repos',
                        help='repos to pull')
    return parser.parse_args(argv)


class Config:
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
        with utils.chdir(os.path.dirname(self.path)):
            path = os.path.abspath(path)
            return path

    @property
    def output(self):
        path = self.impl.get('DEFAULT', 'output', fallback=DEFAULT_OUTPUT_DIR)
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
        path = self.impl.get('DEFAULT', 'my_repos', fallback=DEFAULT_MY_REPOS_PATH)
        return self._resolve_relative(path)

    def import_my_repos(self):
        sys.path.append(os.path.dirname(self.my_repos))
        module_name = os.path.splitext(os.path.basename(self.my_repos))[0]
        module = importlib.import_module(module_name)
        return module.MY_REPOS


def main(args=None):
    with setup_logging():
        args = parse_args(args)
        config = Config.read(args.config)
        my_repos = config.import_my_repos()
        cgit = CGit(config.clone_url)
        output = Output(config.output, cgit)
        success = True
        for repo in my_repos:
            if args.repos is None or repo.repo_id in args.repos:
                repo.fill_defaults(config)
                repo.validate()
                if not output.pull(repo):
                    success = False
        if success:
            logging.info('All repositories were updated successfully')
            return 0
        else:
            logging.warning("Some repositories couldn't be updated!")
            return 1


if __name__ == '__main__':
    sys.exit(main())
