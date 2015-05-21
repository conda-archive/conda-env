from __future__ import absolute_import, print_function
from argparse import RawDescriptionHelpFormatter
import os
import sys
import textwrap

from conda.cli import common
from conda import config

from ..env import from_environment
from . import helpers

ENTRY_POINTS = helpers.generate_entry_points(__name__)

description = """
Export a given environment
"""

example = """
examples:
    conda env export
    conda env export --file SOME_FILE
"""


@helpers.enable_entry_point_override(ENTRY_POINTS["configure_parser"])
def configure_parser(sub_parsers):
    p = sub_parsers.add_parser(
        'export',
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
        default=None,
        required=False
    )

    p.set_defaults(func=execute)
    return p


# TODO Make this aware of channels that were used to install packages
@helpers.enable_entry_point_override(ENTRY_POINTS["execute"])
def execute(args, parser):
    if not args.name:
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
        args.name = name
    else:
        name = args.name
    prefix = common.get_prefix(args)

    env = from_environment(name, prefix)

    if args.file is None:
        print(env.to_yaml())
    else:
        fp = open(args.file, 'wb')
        env.to_yaml(stream=fp)
