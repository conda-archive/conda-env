from __future__ import print_function

description = """
Prints content from environment.yml files.

Handles includes and jinja2 parsing.
"""

example = """
examples:
    conda env print path/to/environment.yml
    conda env print path/to/environment.yml --json
"""


def configure_parser(sub_parsers):
    from argparse import RawDescriptionHelpFormatter

    p = sub_parsers.add_parser(
        'print',
        formatter_class=RawDescriptionHelpFormatter,
        description=description,
        help=description,
        epilog=example,
    )
    p.add_argument(
        '-f', '--file',
        action='store',
        help='environment definition file (default: environment.yml)',
        default='environment.yml',
    )

    from conda.cli import common
    common.add_parser_json(p)

    p.set_defaults(func=execute)


def execute(args, parser):
    from conda_env.env import from_file
    env = from_file(args.file)

    if args.json:
        from conda.cli.common import stdout_json
        stdout_json(env.to_dict())
    else:
        import sys
        env.to_yaml(sys.stdout)
