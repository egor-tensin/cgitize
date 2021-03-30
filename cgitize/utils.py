# Copyright (c) 2018 Egor Tensin <Egor.Tensin@gmail.com>
# This file is part of the "cgitize" project.
# For details, see https://github.com/egor-tensin/cgitize.
# Distributed under the MIT License.

from contextlib import contextmanager
import logging
import os
import stat
import subprocess
import sys


@contextmanager
def setup_logging(verbose=False):
    level = logging.DEBUG if verbose else logging.INFO
    logging.basicConfig(
        level=level,
        datefmt='%Y-%m-%d %H:%M:%S',
        format='%(asctime)s | %(levelname)s | %(message)s',
        # Log to stdout, because that's where subprocess's output goes (so that
        # the don't get interleaved).
        stream=sys.stdout)
    try:
        yield
    except Exception as e:
        logging.exception(e)
        raise


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


@contextmanager
def chdir(new_cwd):
    old_cwd = os.getcwd()
    os.chdir(new_cwd)
    try:
        yield
    finally:
        os.chdir(old_cwd)


@contextmanager
def protected_file(path):
    # 0600:
    new_permissions = stat.S_IRUSR | stat.S_IWUSR
    if os.path.exists(path):
        old_permissions = stat.S_IMODE(os.stat(path).st_mode)
        os.chmod(path, new_permissions)
        try:
            yield
        finally:
            os.chmod(path, old_permissions)
    else:
        with open(path, mode='w'):
            pass
        os.chmod(path, new_permissions)
        try:
            yield
        finally:
            os.unlink(path)
