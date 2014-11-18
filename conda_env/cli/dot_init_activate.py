from __future__ import absolute_import, print_function
import subprocess
import sys

INITIALIZED_STR = "# conda-env initialized"
SOURCE_TEMPLATE = """
# Launch any conda.d scripts,
_ENV_PATH="$(echo $(echo $PATH | awk -F ':' '{print $1}')/..)"
_CONDA_D="${_ENV_PATH}/etc/conda/%s.d"
if [[ -d $_CONDA_D ]]; then
    _CONDA_D_FILES="${_CONDA_D}/*.sh"
    for f in $_CONDA_D_FILES; do
        source $f
    done
fi

"""

CUSTOM_ACTIVATE = SOURCE_TEMPLATE % "activate"
CUSTOM_DEACTIVATE = SOURCE_TEMPLATE % "deactivate"

_help = "Add conda-env functionality to activate script"


def configure_parser(sub_parsers):
    p = sub_parsers.add_parser(
        'init-activate',
        help=_help,
        description=_help,
    )

    p.set_defaults(func=execute)


def execute(args, parser):
    if sys.platform.startswith("win"):
        return execute_windows(args, parser)
    else:
        return execute_posix(args, parser)


def execute_windows(args, parser):
    print("Windows support not yet implemented", file=sys.stderr)
    return -1


def execute_posix(args, parser):
    def modify_script(which, code):
        script_name = subprocess.check_output(['which', which]).strip()
        with open(script_name, "rb+") as fp:
            script = fp.read()

        script_lines = script.splitlines()
        if INITIALIZED_STR in script_lines:
            print("Already initialized {}".format(which))
            return

        for i in range(len(script_lines)):
            if which == "activate" and script_lines[-i] == '':
                break
            if (which == "deactivate"
                    and script_lines[-i].startswith("_NEW_PATH")):
                break
        new_lines = script_lines[0:-i] + [code] + script_lines[-i:]
        new_lines.append(INITIALIZED_STR + "\n")
        with open(script_name, "w") as fp:
            fp.write("\n".join(new_lines))
        print("Initialized {}".format(which))

    modify_script("activate", CUSTOM_ACTIVATE)
    modify_script("deactivate", CUSTOM_DEACTIVATE)
