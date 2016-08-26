from __future__ import absolute_import, print_function

import os
import textwrap
from argparse import RawDescriptionHelpFormatter

from conda import config
from conda.cli import common

from ..env import from_environment
from conda.config import default_prefix

description = """
Export a given environment
"""

example = """
examples:
    conda env export
    conda env export --file SOME_FILE
"""


def configure_parser(sub_parsers):
    p = sub_parsers.add_parser(
        'export',
        formatter_class=RawDescriptionHelpFormatter,
        description=description,
        help=description,
        epilog=example,
    )

    p.add_argument(
        '-c', '--channel',
        action='append',
        help='Additional channel to include in the export'
    )

    p.add_argument(
        "--override-channels",
        action="store_true",
        help="Do not include .condarc channels",
    )

    p.add_argument(
        '-n', '--name',
        action='store',
        help='name of environment (in %s)' % os.pathsep.join(config.envs_dirs),
        default=None,
    )
    p.add_argument(
        '-p', "--prefix",
        action="store",
        help="Full path to environment prefix (default: %s)." % default_prefix,
        metavar='PATH',
    )

    p.add_argument(
        '-f', '--file',
        default=None,
        required=False
    )

    p.add_argument(
        '--no-builds',
        default=False,
        action='store_true',
        required=False,
        help='Remove build specification from dependencies'
    )

    p.set_defaults(func=execute)


# TODO Make this aware of channels that were used to install packages
def execute(args, parser):

    if args.prefix:
        prefix = os.path.abspath(args.prefix)
    else:
        prefix = common.get_prefix(args)

    if not args.name:
        # Note, this is a hack fofr get_prefix that assumes argparse results
        # TODO Refactor common.get_prefix
        name = os.environ.get('CONDA_DEFAULT_ENV', False)

        if args.prefix:
            name = os.path.basename(prefix)
        elif not name:
            msg = "Unable to determine environment\n\n"
            msg += textwrap.dedent("""
                Please re-run this command with one of the following options:

                * Provide an environment name via --name or -n
                * Alternately, provide an environment path via --path or -p
                * Re-run this command inside an activated conda environment.""").lstrip()
            # TODO Add json support
            common.error_and_exit(msg, json=False)
        args.name = name
    else:
        name = args.name

    env = from_environment(name, prefix, no_builds=args.no_builds)

    if args.override_channels:
        env.remove_channels()

    if args.channel is not None:
        env.add_channels(args.channel)

    if args.file is None:
        print(env.to_yaml())
    else:
        fp = open(args.file, 'wb')
        env.to_yaml(stream=fp)
