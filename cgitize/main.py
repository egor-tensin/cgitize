# Copyright (c) 2018 Egor Tensin <Egor.Tensin@gmail.com>
# This file is part of the "cgitize" project.
# For details, see https://github.com/egor-tensin/cgitize.
# Distributed under the MIT License.

from argparse import ArgumentParser
import logging
import sys

from cgitize.cgit import CGitRepositories, CGitServer
from cgitize.config import Config
from cgitize.utils import setup_logging
from cgitize.version import __version__


def parse_args(argv=None):
    if argv is None:
        argv = sys.argv[1:]
    parser = ArgumentParser()
    parser.add_argument('--config', '-c', metavar='PATH',
                        default=Config.DEFAULT_PATH,
                        help='config file path')
    parser.add_argument('--repo', metavar='REPO_ID',
                        nargs='*', dest='repos',
                        help='repos to pull')
    parser.add_argument('--force', '-f', action='store_true',
                        help='overwrite existing repositories')
    parser.add_argument('--verbose', '-v', action='store_true',
                        help='verbose log output')
    parser.add_argument('--version', '-V', action='version',
                        version=f'%(prog)s {__version__}')
    return parser.parse_args(argv)


def main(argv=None):
    args = parse_args(argv)
    with setup_logging(args.verbose):
        config = Config.read(args.config)
        cgit_server = CGitServer(config.main.clone_url)
        output = CGitRepositories(config.main.output_dir, cgit_server, force=args.force)
        success = True
        for repo in config.parse_repositories():
            if args.repos is None or repo.name in args.repos:
                if not output.update(repo):
                    success = False
        if success:
            logging.info('All repositories were updated successfully')
            return 0
        else:
            logging.warning("Some repositories couldn't be updated!")
            return 1


if __name__ == '__main__':
    sys.exit(main())
