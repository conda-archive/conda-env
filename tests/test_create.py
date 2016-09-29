# -*- coding: utf-8 -*-
from __future__ import absolute_import, division, print_function

from contextlib import contextmanager
from logging import getLogger, Handler
from os.path import exists, join
from shlex import split
from shutil import rmtree
from tempfile import mkdtemp
from unittest import TestCase

from conda import config
from conda.cli import conda_argparse
from conda.install import linked as install_linked, dist2dirname
from conda.install import on_win
from conda_env.cli.main_create import configure_parser as create_configure_parser
from conda_env.cli.main_update import configure_parser as update_configure_parser

from . import utils


PYTHON_BINARY = 'python.exe' if on_win else 'bin/python'


def escape_for_winpath(p):
    return p.replace('\\', '\\\\')


def disable_dotlog():
    class NullHandler(Handler):
        def emit(self, record):
            pass
    dotlogger = getLogger('dotupdate')
    saved_handlers = dotlogger.handlers
    dotlogger.handlers = []
    dotlogger.addHandler(NullHandler())
    return saved_handlers


def reenable_dotlog(handlers):
    dotlogger = getLogger('dotupdate')
    dotlogger.handlers = handlers


class Commands:
    CREATE = "create"
    UPDATE = "update"


parser_config = {
    Commands.CREATE: create_configure_parser,
    Commands.UPDATE: update_configure_parser,
}


def run_command(command, envs_dir, env_name, *arguments):
    p = conda_argparse.ArgumentParser()
    sub_parsers = p.add_subparsers(metavar='command', dest='cmd')
    parser_config[command](sub_parsers)

    arguments = list(map(escape_for_winpath, arguments))
    command_line = "{0} -n {1} -f {2}".format(command, env_name, " ".join(arguments))

    args = p.parse_args(split(command_line))
    try:
        old_envs_dirs = config.envs_dirs
        config.envs_dirs[:] = [envs_dir]
        args.func(args, p)
    finally:
        config.envs_dirs[:] = old_envs_dirs


@contextmanager
def make_temp_envs_dir():
    envs_dir = mkdtemp()
    try:
        yield envs_dir
    finally:
        rmtree(envs_dir, ignore_errors=True)


def package_is_installed(prefix, package, exact=False):
    packages = list(install_linked(prefix))
    if '::' not in package:
        packages = list(map(dist2dirname, packages))
    if exact:
        return package in packages
    return any(p.startswith(package) for p in packages)


def assert_package_is_installed(prefix, package, exact=False):
    if not package_is_installed(prefix, package, exact):
        print(list(install_linked(prefix)))
        raise AssertionError("package {0} is not in prefix".format(package))


class IntegrationTests(TestCase):

    def setUp(self):
        self.saved_dotlog_handlers = disable_dotlog()

    def tearDown(self):
        reenable_dotlog(self.saved_dotlog_handlers)

    def test_create_update(self):
        with make_temp_envs_dir() as envs_dir:
            env_name = 'test'
            prefix = join(envs_dir, env_name)
            python_path = join(prefix, PYTHON_BINARY)

            run_command(Commands.CREATE, envs_dir, env_name, utils.support_file('example/environment_pinned.yml'))
            self.assertTrue(exists(python_path),
                            'Python file {} does not exist'.format(python_path))
            assert_package_is_installed(prefix, 'flask-0.9')

            run_command(Commands.UPDATE, envs_dir, env_name, utils.support_file('example/environment_pinned_updated.yml'))
            assert_package_is_installed(prefix, 'flask-0.10')
            self.assertFalse(package_is_installed(prefix, 'flask-0.9'))
