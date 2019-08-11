from argparse import ArgumentParser
import logging
import sys

from pull.cgit import CGit, Output
from pull.my_repos import MY_REPOS


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
    parser.add_argument('--output', metavar='PATH',
                        default=DEFAULT_OUTPUT_DIR,
                        help='output directory path')
    parser.add_argument('--cgit-user', metavar='USERNAME',
                        default=DEFAULT_CGIT_CLONE_USER,
                        help='cgit clone username')
    parser.add_argument('--cgit-host', metavar='HOST',
                        default=DEFAULT_CGIT_CLONE_HOST,
                        help='cgit clone host')
    parser.add_argument('--cgit-port', metavar='PORT', type=int,
                        default=DEFAULT_CGIT_CLONE_PORT,
                        help='cgit clone port number')
    parser.add_argument('--repo', metavar='REPO_ID', nargs='*', dest='repos',
                        help='repos to pull')
    return parser.parse_args(argv)


def main(args=None):
    set_up_logging()
    try:
        args = parse_args(args)
        cgit = CGit(args.cgit_user, args.cgit_host, args.cgit_port)
        output = Output(args.output, cgit)
        success = True
        for repo in MY_REPOS:
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
