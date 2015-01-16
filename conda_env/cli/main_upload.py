from argparse import RawDescriptionHelpFormatter
import os
import textwrap

from conda import config
from conda.cli import common

from ..env import from_file
from .. import exceptions


# Raise an appropriate error later only if conda-env upload is called
try:
    from binstar_client.utils import get_binstar
    from binstar_client import errors as binstar_errors
    from ..utils import binstar_uilts
except ImportError:
    get_binstar = None

description = """
Upload an environment to binstar
"""

example = """
examples:
    conda env upload 
    conda env upload -n=foo
    conda env upload -f=/path/to/environment.yml
    conda env upload --name=foo --file=environment.yml
"""

def configure_parser(sub_parsers):
    p = sub_parsers.add_parser(
        'upload',
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
        '-u', '--user',
        help='Binstar user to upload environment',
    )
    p.add_argument(
        '--version',
        help='Version of the environment',
    )
    p.add_argument(
        '--summary',
        help='Short summary of the environment',
    )
    p.add_argument(
        '--force',
        action='store_true',
        help='Force remove any existing files with the same version and name',
    )
    p.add_argument(
        '-q', '--quiet',
        default=False,
    )
    common.add_parser_json(p)
    p.set_defaults(func=execute)


def execute(args, parser):

    if get_binstar is None:
        raise exceptions.NoBinstar()

    try:
        env = from_file(args.file)
    except exceptions.EnvironmentFileNotFound as e:
        msg = 'Unable to locate environment file: %s\n\n' % e.filename
        msg += "\n".join(textwrap.wrap(textwrap.dedent("""
            Please verify that the above file is present and that you have
            permission read the file's contents.  Note, you can specify the
            file to use by explictly adding --file=/path/to/file when calling
            conda env create.""").lstrip()))

        common.error_and_exit(msg, json=args.json)

    if not args.name:
        if not env.name:
            # TODO It would be nice to be able to format this more cleanly
            common.error_and_exit(
                'An environment name is required.\n\n'
                'You can either specify one directly with --name or you can add\n'
                'a name property to your %s file.' % args.file,
                json=args.json
            )
        # Note: stubbing out the args object as all of the
        # conda.cli.common code thinks that name will always
        # be specified.
        args.name = env.name

    env_data = dict(env.to_dict())
    if not (args.version or env_data.get('version')):
            # TODO It would be nice to be able to format this more cleanly
            common.error_and_exit(
                'A version is required to upload environments to binstar.\n\n'
                'You can either specify one directly with --version or you can add\n'
                'a version property to your %s file.' % args.file,
                json=args.json
            )
        # Note: stubbing out the args object as all of the
        # conda.cli.common code thinks that name will always
        # be specified.
    elif not args.version:
        args.version = env_data['version']

    binstar = get_binstar()

    user = binstar_uilts.ensure_loggedin(binstar)

    if not args.user:
        args.user = user['login']

    if not args.summary:
        args.summary = env_data.get('summary')

    binstar_uilts.ensure_package_namespace(binstar,
                                           args.user, args.name, args.version,
                                           args.summary)

    basename = os.path.basename(args.file)
    print("Uploading environment %s to anaconda-server (%s)... " % (args.name, binstar.domain))
    try:
        binstar.distribution(args.user, args.name, args.version, basename)
    except binstar_errors.NotFound:
        pass
    else:
        if args.force:
            binstar.remove_dist(args.user, args.name, args.version, basename)
        else:
            env_path = "%s/%s/%s/%s" % (args.user, args.name, args.version, basename)
            common.error_and_exit(
                'The environment path %s already exists on binstar \n\n'
                'If you want to overwrite this file use the --force option' % (env_path),
                json=args.json
            )

    binstar.upload(args.user, args.name, args.version,
                   basename, open(args.file),
                   distribution_type=binstar_uilts.ENVIRONMENT_TYPE,
                   attrs=env_data)

    print("done")


