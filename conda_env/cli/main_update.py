from argparse import RawDescriptionHelpFormatter
import os
import textwrap
import sys

from conda import config
from conda.cli import common
from conda.cli import install as cli_install
from conda.misc import touch_nonadmin

from ..env import from_file
from ..installers.base import get_installer, InvalidInstaller
from .. import exceptions
from . import helpers

ENTRY_POINTS = helpers.generate_entry_points(__name__)

description = """
Update the current environment based on environment file
"""

example = """
examples:
    conda env update
    conda env update -n=foo
    conda env update -f=/path/to/environment.yml
    conda env update --name=foo --file=environment.yml
"""

@helpers.enable_entry_point_override(ENTRY_POINTS["configure_parser"])
def configure_parser(sub_parsers):
    p = sub_parsers.add_parser(
        'update',
        formatter_class=RawDescriptionHelpFormatter,
        description=description,
        help=description,
        epilog=example,
    )

    p.add_argument(
        '-n', '--name',
        action='store',
        help='name of environment (in %s)' % os.pathsep.join(config.envs_dirs),
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
    p.set_defaults(func=execute)
    return p


@helpers.enable_entry_point_override(ENTRY_POINTS["execute"])
def execute(args, parser):
    try:
        env = from_file(args.file)
    except exceptions.EnvironmentFileNotFound as e:
        msg = 'Unable to locate environment file: %s\n\n' % e.filename
        msg += "\n".join(textwrap.wrap(textwrap.dedent("""
            Please verify that the above file is present and that you have
            permission read the file's contents.  Note, you can specify the
            file to use by explictly adding --file=/path/to/file when calling
            conda env update.""").lstrip()))

        common.error_and_exit(msg, json=args.json)

    if not args.name:
        if not env.name:
                    # Note, this is a hack fofr get_prefix that assumes argparse results
            # TODO Refactor common.get_prefix
            name = os.environ.get('CONDA_DEFAULT_ENV', False)
            if not name:
                msg = "Unable to determine environment\n\n"
                msg += textwrap.dedent("""
                    Please re-run this command with one of the following options:

                    * Provide an environment name via --name or -n
                    * Re-run this command inside an activated conda environment.""").lstrip()
                # TODO Add json support
                common.error_and_exit(msg, json=False)

        # Note: stubbing out the args object as all of the
        # conda.cli.common code thinks that name will always
        # be specified.
        args.name = env.name

    prefix = common.get_prefix(args, search=False)
    # CAN'T Check with this function since it assumes we will create prefix.
    # cli_install.check_prefix(prefix, json=args.json)

    # TODO, add capability
    # common.ensure_override_channels_requires_channel(args)
    # channel_urls = args.channel or ()

    for installer_type, specs in env.dependencies.items():
        try:
            installer = get_installer(installer_type)
            installer.install(prefix, specs, args, env)
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

    touch_nonadmin(prefix)
    if not args.json:
        cli_install.print_activate(args.name if args.name else prefix)
