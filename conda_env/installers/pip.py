from __future__ import absolute_import

import subprocess
from itertools import chain
from os.path import join

import conda.config as config
from conda.cli import main_list


def install(prefix, specs, args, env):
    # This mess is necessary to get --editable package sent to subprocess
    # properly.
    specs = list(chain(*[s.split() if '-e' in s else [s] for s in specs]))
    # Directory where pip will store VCS checkouts for editable packages
    src_dir = join(config.envs_dirs[0], env.name, 'src')
    pip_cmd = main_list.pip_args(prefix) + ['install', '--src', src_dir] + specs
    process = subprocess.Popen(pip_cmd, universal_newlines=True)
    process.communicate()
