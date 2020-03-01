# Copyright (c) 2018 Egor Tensin <Egor.Tensin@gmail.com>
# This file is part of the "cgit repos" project.
# For details, see https://github.com/egor-tensin/cgit-repos.
# Distributed under the MIT License.

from argparse import ArgumentParser
import configparser
import importlib
import logging
import os.path
import sys

from cgit.repos.cgit import CGit, Output
from cgit.repos.repo import BitbucketRepo, GithubRepo, Repo


DEFAULT_OUTPUT_DIR = '/var/tmp/cgit-repos/output'
DEFAULT_CONFIG_PATH = '/etc/cgit-repos/cgit-repos.conf'
DEFAULT_MY_REPOS_PATH = '/etc/cgit-repos/my_repos.py'


def set_up_logging():
    logging.basicConfig(
        level=logging.DEBUG,
        datefmt='%Y-%m-%d %H:%M:%S',
        format='%(asctime)s | %(levelname)s | %(message)s')


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
        config = configparser.ConfigParser()
        config.read(path)
        return Config(config)

    def __init__(self, impl):
        self.impl = impl

    @property
    def output(self):
        return self.impl.get('DEFAULT', 'output', fallback=DEFAULT_OUTPUT_DIR)

    @property
    def clone_url(self):
        return self.impl.get('DEFAULT', 'clone_url', fallback=None)

    @property
    def default_owner(self):
        return self.impl.get('DEFAULT', 'owner', fallback=None)

    @property
    def github_username(self):
        return self.impl.get('GITHUB', 'username', fallback=None)

    @property
    def bitbucket_username(self):
        return self.impl.get('BITBUCKET', 'username', fallback=None)

    def set_defaults(self):
        Repo.DEFAULT_OWNER = self.default_owner
        GithubRepo.DEFAULT_USER = self.github_username
        BitbucketRepo.DEFAULT_USER = self.bitbucket_username

    @property
    def my_repos(self):
        return self.impl.get('DEFAULT', 'my_repos', fallback=DEFAULT_MY_REPOS_PATH)

    def import_my_repos(self):
        sys.path.append(os.path.dirname(self.my_repos))
        module_name = os.path.splitext(os.path.basename(self.my_repos))[0]
        module = importlib.import_module(module_name)
        return module.MY_REPOS


def main(args=None):
    set_up_logging()
    try:
        args = parse_args(args)
        config = Config.read(args.config)
        config.set_defaults()
        my_repos = config.import_my_repos()
        cgit = CGit(config.clone_url)
        output = Output(config.output, cgit)
        success = True
        for repo in my_repos:
            if args.repos is None or repo.repo_id in args.repos:
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
