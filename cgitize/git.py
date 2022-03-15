# Copyright (c) 2021 Egor Tensin <Egor.Tensin@gmail.com>
# This file is part of the "cgitize" project.
# For details, see https://github.com/egor-tensin/cgitize.
# Distributed under the MIT License.

from contextlib import contextmanager
import os

from cgitize import utils


GIT_ENV = os.environ.copy()
GIT_ENV['GIT_SSH_COMMAND'] = 'ssh -oBatchMode=yes -oLogLevel=QUIET -oStrictHostKeyChecking=no -oUserKnownHostsFile=/dev/null'


class Config:
    def __init__(self, path):
        self.path = path

    def exists(self):
        return os.path.exists(self.path)

    def open(self, mode='r'):
        return open(self.path, mode=mode, encoding='utf-8')

    def read(self):
        with self.open(mode='r') as fd:
            return fd.read()

    def write(self, contents):
        with self.open(mode='w') as fd:
            fd.write(contents)

    @contextmanager
    def backup(self):
        old_contents = self.read()
        try:
            yield old_contents
        finally:
            self.write(old_contents)

    # What follows is an exteremely loose interpretation of what the .gitconfig
    # syntax is. The source was git-config(1).

    class Section:
        def __init__(self, name, variables):
            Config.Section.validate_name(name)
            self.name = name
            self.variables = variables

        @staticmethod
        def validate_name(name):
            if not name:
                raise RuntimeError('section names cannot be empty')
            for c in name:
                if c.isalnum() or c == '-' or c == '.':
                    continue
                raise RuntimeError(f'section names must only contain alphanumeric characters, . or -: {name}')

        @staticmethod
        def format_name(name):
            return name

        def format(self):
            result = f'[{self.format_name(self.name)}]\n'
            result += ''.join((var.format() for var in self.variables))
            return result

    class Subsection:
        def __init__(self, section, name, variables):
            Config.Section.validate_name(section)
            Config.Subsection.validate_name(name)
            self.section = section
            self.name = name
            self.variables = variables

        @staticmethod
        def validate_name(name):
            if '\n' in name:
                raise RuntimeError(f'subsection names cannot contain newlines: {name}')

        def format_name(self):
            name = self.name
            # Escape the backslashes:
            name = name.replace('\\', '\\\\')
            # Escape the quotes:
            name = name.replace('"', '\\"')
            # Put in quotes:
            return f'"{name}"'

        def format(self):
            result = f'[{Config.Section.format_name(self.section)} {self.format_name()}]\n'
            result += ''.join((var.format() for var in self.variables))
            return result

    class Variable:
        def __init__(self, name, value):
            Config.Variable.validate_name(name)
            Config.Variable.validate_value(value)
            self.name = name
            self.value = value

        @staticmethod
        def validate_name(name):
            if not name:
                raise RuntimeError('variable names cannot be empty')
            for c in name:
                if c.isalnum() or c == '-':
                    continue
                raise RuntimeError(f'variable name can only contain alphanumeric characters or -: {name}')
            if not name[0].isalnum():
                raise RuntimeError(f'variable name must start with an alphanumeric character: {name}')

        @staticmethod
        def validate_value(value):
            pass

        def format_name(self):
            return self.name

        def format_value(self):
            value = self.value
            # Escape the backslashes:
            value = value.replace('\\', '\\\\')
            # Escape the supported escape sequences (\n, \t and \b):
            value = value.replace('\n', '\\n')
            value = value.replace('\t', '\\t')
            value = value.replace('\b', '\\b')
            # Escape the quotes:
            value = value.replace('"', '\\"')
            # Put in quotes:
            value = f'"{value}"'
            return value

        def format(self):
            return f'    {self.format_name()} = {self.format_value()}\n'


class Git:
    EXE = 'git'

    @staticmethod
    def check(*args, **kwargs):
        return utils.try_run(Git.EXE, *args, env=GIT_ENV, **kwargs)

    @staticmethod
    def capture(*args, **kwargs):
        return utils.try_capture(Git.EXE, *args, env=GIT_ENV, **kwargs)

    @staticmethod
    def get_global_config():
        return Config(os.path.expanduser('~/.gitconfig'))

    @staticmethod
    @contextmanager
    def setup_auth(repo):
        if not repo.url_auth:
            yield
            return
        config = Git.get_global_config()
        with utils.protected_file(config.path):
            with config.backup() as old_contents:
                variables = [Config.Variable('insteadOf', repo.clone_url)]
                subsection = Config.Subsection('url', repo.clone_url_with_auth, variables)
                new_contents = f'{old_contents}\n{subsection.format()}'
                config.write(new_contents)
                yield
