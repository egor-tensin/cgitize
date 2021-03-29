# Copyright (c) 2018 Egor Tensin <Egor.Tensin@gmail.com>
# This file is part of the "cgitize" project.
# For details, see https://github.com/egor-tensin/cgitize.
# Distributed under the MIT License.

import contextlib
import logging
import os
import subprocess


def run(*args, capture_output=False, **kwargs):
    stdout = None
    stderr = None
    if capture_output:
        stdout = subprocess.PIPE
        stderr = subprocess.STDOUT

    logging.debug('%s', args)
    result = subprocess.run(args, check=True, stdout=stdout, stderr=stderr,
                            encoding='utf-8', **kwargs)

    if result.stdout is not None:
        logging.debug('\n%s', result.stdout)
    return result.stdout


def try_run(*args, **kwargs):
    try:
        run(*args, **kwargs)
        return True
    except subprocess.CalledProcessError as e:
        return e.returncode == 0


def run_capture(*args, **kwargs):
    return run(*args, capture_output=True, **kwargs)


def try_run_capture(*args, **kwargs):
    try:
        return True, run(*args, capture_output=True, **kwargs)
    except subprocess.CalledProcessError as e:
        return e.returncode == 0, e.output


@contextlib.contextmanager
def chdir(new_cwd):
    old_cwd = os.getcwd()
    os.chdir(new_cwd)
    try:
        yield
    finally:
        os.chdir(old_cwd)
