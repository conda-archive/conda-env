from argparse import RawDescriptionHelpFormatter
import os
import textwrap
import sys

import pkg_resources

from conda import config
from conda.cli import common
from conda.cli import install as cli_install
from conda.misc import touch_nonadmin

from ..env import from_file
from ..installers.base import get_installer, InvalidInstaller
from .. import exceptions
from . import helpers
from . import base

ENTRY_POINTS = helpers.generate_entry_points(__name__)

description = """
Create an environment based on an environment file
"""

example = """
examples:
    conda env create
    conda env create -n=foo
    conda env create -f=/path/to/environment.yml
    conda env create --name=foo --file=environment.yml
"""


def say_configure_parser(command, sub_parsers):
    p = say_configure_parser.next(sub_parsers)
    p.add_argument('--say', action='store_true', default=False,
                   help='say the name')
    return p


def say_execute(command):
    if command.args.say:
        if command.name:
            print("you're about to create %s" % command.name)
        else:
            print("you're about to create an environment, but I don't know "
                  "what the name is yet")
    return say_execute.next()


class Command(base.BaseCommand):
    def __init__(self, *args, **kwargs):
        super(Command, self).__init__(*args, **kwargs)
        self._env = None
        self._prefix = None

    def configure_parser(self, sub_parsers):
        p = sub_parsers.add_parser(
            'create',
            formatter_class=RawDescriptionHelpFormatter,
            description=description,
            help=description,
            epilog=example,
        )

        p.add_argument(
            '-n', '--name',
            action='store',
            help='name of environment (in %s)' % os.pathsep.join(
                config.envs_dirs),
            default=None,
        )

        p.add_argument(
            '-f', '--file',
            action='store',
            help='environment definition (default: environment.yml)',
            default='environment.yml',
        )
        p.add_argument(
            '-q', '--quiet',
            default=False,
        )
        common.add_parser_json(p)

        p.set_defaults(command=self)
        return p

    @property
    def env(self):
        try:
            if self._env is None:
                self._env = from_file(self.args.file)
            return self._env
        except exceptions.EnvironmentFileNotFound as e:
            # TODO Update to use a method on this object
            msg = 'Unable to locate environment file: %s\n\n' % e.filename
            msg += "\n".join(textwrap.wrap(textwrap.dedent("""
                Please verify that the above file is present and that you have
                permission read the file's contents.  Note, you can specify the
                file to use by explictly adding --file=/path/to/file when calling
                conda env create.""").lstrip()))

            common.error_and_exit(msg, json=self.args.json)

    @property
    def name(self):
        if not self.args.name:
            if not self.env.name:
                # TODO It would be nice to be able to format this more cleanly
                common.error_and_exit(
                    'An environment name is required.\n\n'
                    'You can either specify one directly with --name or you can add\n'
                    'a name property to your %s file.' % self.args.file,
                    json=self.args.json
                )
            # Note: stubbing out the args object as all of the
            # conda.cli.common code thinks that name will always
            # be specified.
            self.args.name = self.env.name
        return self.args.name

    @property
    def prefix(self):
        if self._prefix is None:
            prefix = common.get_prefix(self.args, search=False)
            cli_install.check_prefix(prefix, json=self.args.json)
            self._prefix = prefix
        return self._prefix

    def execute(self):
        # FIXME Make sure that this isn't required by fixing Conda
        self.name

        # TODO, add capability
        # common.ensure_override_channels_requires_channel(args)
        # channel_urls = args.channel or ()

        for installer_type, specs in self.env.dependencies.items():
            try:
                installer = get_installer(installer_type)
                installer.install(self.prefix, specs, self.args, self.env)
            except InvalidInstaller:
                sys.stderr.write(textwrap.dedent("""
                    Unable to install package for {0}.

                    Please double check and ensure you dependencies file has
                    the correct spelling.  You might also try installing the
                    conda-env-{0} package to see if provides the required
                    installer.
                    """).lstrip().format(installer_type)
                )
                return -1

        touch_nonadmin(self.prefix)
        self.run_after()

    def run_after(self):
        if self.args.json:
            return
        cli_install.print_activate(
            self.args.name if self.args.name else self.prefix
        )
