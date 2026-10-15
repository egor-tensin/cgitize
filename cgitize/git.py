# Copyright (c) 2021 Egor Tensin <egor@tensin.name>
# This file is part of the "cgitize" project.
# For details, see https://github.com/egor-tensin/cgitize
# Distributed under the MIT License.

from contextlib import contextmanager
import os
import tempfile

from cgitize import utils

GIT_ENV = os.environ.copy()
GIT_ENV["GIT_SSH_COMMAND"] = (
    "ssh -oBatchMode=yes -oLogLevel=QUIET -oStrictHostKeyChecking=no -oUserKnownHostsFile=/dev/null"
)
GIT_ENV["GIT_CONFIG_NOSYSTEM"] = "true"
GIT_ENV["GIT_CONFIG_GLOBAL"] = "/dev/null"


class Config:
    # What follows is an exteremely loose interpretation of what the .gitconfig
    # syntax is. The source was git-config(1).

    @staticmethod
    @contextmanager
    def make_tmp():
        tmp = tempfile.NamedTemporaryFile(mode="w", encoding="utf-8")
        with tmp as result, utils.protected_file(result.name):
            yield result

    class Section:
        def __init__(self, name, variables):
            Config.Section.validate_name(name)
            self.name = name
            self.variables = variables

        @staticmethod
        def validate_name(name):
            if not name:
                raise RuntimeError("section names cannot be empty")
            for c in name:
                if c.isalnum() or c == "-" or c == ".":
                    continue
                raise RuntimeError(
                    f"section names must only contain alphanumeric characters, . or -: {name}"
                )

        @staticmethod
        def format_name(name):
            return name

        def format(self):
            result = f"[{self.format_name(self.name)}]\n"
            result += "".join((var.format() for var in self.variables))
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
            if "\n" in name:
                raise RuntimeError(f"subsection names cannot contain newlines: {name}")

        def format_name(self):
            name = self.name
            # Escape the backslashes:
            name = name.replace("\\", r"\\")
            # Escape the quotes:
            name = name.replace('"', r"\"")
            # Put in quotes:
            return f'"{name}"'

        def format(self):
            result = (
                f"[{Config.Section.format_name(self.section)} {self.format_name()}]\n"
            )
            result += "".join((var.format() for var in self.variables))
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
                raise RuntimeError("variable names cannot be empty")
            for c in name:
                if c.isalnum() or c == "-":
                    continue
                raise RuntimeError(
                    f"variable name can only contain alphanumeric characters or -: {name}"
                )
            if not name[0].isalnum():
                raise RuntimeError(
                    f"variable name must start with an alphanumeric character: {name}"
                )

        @staticmethod
        def validate_value(value):
            pass

        def format_name(self):
            return self.name

        def format_value(self):
            value = self.value
            # Escape the backslashes:
            value = value.replace("\\", r"\\")
            # Escape the supported escape sequences (\n, \t and \b):
            value = value.replace("\n", r"\n")
            value = value.replace("\t", r"\t")
            value = value.replace("\b", r"\b")
            # Escape the quotes:
            value = value.replace('"', r"\"")
            # Put in quotes:
            value = f'"{value}"'
            return value

        def format(self):
            return f"    {self.format_name()} = {self.format_value()}\n"


class Git:
    EXE = "git"

    def __init__(self, config=None):
        self._env = GIT_ENV.copy()
        if config is not None:
            self._env["GIT_CONFIG_GLOBAL"] = config

    def check(self, *args, **kwargs):
        return utils.try_run(Git.EXE, *args, env=self._env, **kwargs)

    def capture(self, *args, **kwargs):
        return utils.try_capture(Git.EXE, *args, env=self._env, **kwargs)

    @staticmethod
    @contextmanager
    def setup_auth(repo):
        if not repo.url_auth:
            yield Git()
            return
        with Config.make_tmp() as config:
            variables = [Config.Variable("insteadOf", repo.clone_url)]
            subsection = Config.Subsection("url", repo.clone_url_with_auth, variables)
            config.write(subsection.format())
            config.flush()
            yield Git(config.name)
