# Copyright (c) 2018 Egor Tensin <Egor.Tensin@gmail.com>
# This file is part of the "cgit repos" project.
# For details, see https://github.com/egor-tensin/cgit-repos.
# Distributed under the MIT License.

import contextlib
import logging
import os
import subprocess


def check_output(*args, stdout=subprocess.PIPE, **kwargs):
    result = subprocess.run(args, stdout=stdout, stderr=subprocess.STDOUT,
                            encoding='utf-8', **kwargs)
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


def run(*args, discard_output=False, **kwargs):
    if discard_output:
        success, _ = check_output(*args, stdout=subprocess.DEVNULL, **kwargs)
    else:
        success, _ = check_output(*args, **kwargs)
    return success


@contextlib.contextmanager
def chdir(new_cwd):
    old_cwd = os.getcwd()
    os.chdir(new_cwd)
    try:
        yield
    finally:
        os.chdir(old_cwd)
