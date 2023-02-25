#!/usr/bin/env python3

from argparse import ArgumentParser
import sys

from cgitize.config import Config


def parse_args(argv=None):
    if argv is None:
        argv = sys.argv[1:]
    parser = ArgumentParser()
    parser.add_argument('config', metavar='PATH',
                        help='config file path')
    return parser.parse_args(argv)


def main(argv=None):
    args = parse_args(argv)
    cfg = Config.read(args.config)
    print(cfg.main.output_dir)


if __name__ == '__main__':
    main()
