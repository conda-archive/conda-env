from __future__ import absolute_import, print_function
import subprocess

INITIALIZED_STR = "# conda-env initialized"
CUSTOM_ACTIVATE = """

# Launch any conda.d scripts,
_ENV_PATH="$(echo $(echo $PATH | awk -F ':' '{print $1}')/..)"
_CONDA_ACTIVATE_D="${_ENV_PATH}/etc/conda/activate.d"
if [[ -d $_CONDA_ACTIVATE_D ]]; then
    _CONDA_ACTIVATE_D_FILES="${_CONDA_ACTIVATE_D}/*.sh"
    for f in $_CONDA_ACTIVATE_D_FILES; do
        source $f
    done
fi

"""

_help = "Add conda-env functionality to activate script"


def configure_parser(sub_parsers):
    p = sub_parsers.add_parser(
        'init-activate',
        help=_help,
        description=_help,
    )

    p.set_defaults(func=execute)


def execute(args, parser):
    activate_name = subprocess.check_output(['which', 'activate']).strip()
    with open(activate_name, "rb+") as fp:
        activate = fp.read()

    activate_lines = activate.splitlines()
    if INITIALIZED_STR in activate_lines:
        print("Already initialized")
        return

    for i in range(len(activate_lines)):
        if activate_lines[-i] == '':
            break
    new_lines = activate_lines[0:-i] + [CUSTOM_ACTIVATE] + activate_lines[-i:]
    new_lines.append(INITIALIZED_STR + "\n")
    with open(activate_name, "w") as fp:
        fp.write("\n".join(new_lines))
    print("Initialized")
