import os
import yaml


# TODO Refactor
def configure_parser(sub_parsers):
    p = sub_parsers.add_parser(
        'info',
    )
    p.add_argument(
        '--only',
        action='store',
        help='only display these names (comma-separated)',
        required=False
    )
    p.add_argument(
        '--quiet',
        action='store_true',
        help='reduce output',
        default=False
    )
    p.add_argument(
        '-f', '--file',
        action='store',
        help='environment definition (default: environment.yml)',
        default='environment.yml',
    )
    p.set_defaults(func=execute)
    return p


def execute(args, parser):
    # TODO create a Python API for interacting with "environments"
    if not os.path.exists(args.file):
        if getattr(args, 'quiet', False):
            # TODO print something here
            pass
        return 1

    with open(args.file, 'rb') as fp:
        data = yaml.load(fp)

    if args.only:
        # TODO support . notation to acccess dependencies.pip, etc
        for a in args.only.split(','):
            print(data[a])

    else:
        for k, v in data.items():
            print("%s == %s" % (k, v))
