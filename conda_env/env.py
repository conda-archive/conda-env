from __future__ import absolute_import, print_function
from collections import OrderedDict
from copy import copy
import os

# TODO This should never have to import from conda.cli
from conda.cli import common
from conda.cli import main_list
from conda import install

from . import compat
from . import exceptions
from . import yaml


def load_from_directory(directory):
    """Load and return an ``Environment`` from a given ``directory``"""
    files = ['environment.yml', 'environment.yaml']
    while True:
        for f in files:
            try:
                return from_file(os.path.join(directory, f))
            except exceptions.EnvironmentFileNotFound:
                pass
        old_directory = directory
        directory = os.path.dirname(directory)
        if directory == old_directory:
            break
    raise exceptions.EnvironmentFileNotFound(files[0])


# TODO This should lean more on conda instead of divining it from the outside
# TODO tests!!!
def from_environment(name, prefix):
    installed = install.linked(prefix)
    conda_pkgs = copy(installed)
    # json=True hides the output, data is added to installed
    main_list.add_pip_installed(prefix, installed, json=True)

    pip_pkgs = sorted(installed - conda_pkgs)

    dependencies = ['='.join(a.rsplit('-', 2)) for a in sorted(conda_pkgs)]
    if len(pip_pkgs) > 0:
        dependencies.append({'pip': ['=='.join(a.rsplit('-', 2)[:2]) for a in pip_pkgs]})

    return Environment(name=name, dependencies=dependencies)


def from_file(filename):
    if not os.path.exists(filename):
        raise exceptions.EnvironmentFileNotFound(filename)
    with open(filename, 'rb') as fp:
        data = yaml.load(fp)
    return Environment(filename=filename, **data)


# TODO test explicitly
class Dependencies(OrderedDict):
    def __init__(self, raw, *args, **kwargs):
        super(Dependencies, self).__init__(*args, **kwargs)
        self.raw = raw
        self.parse()

    def parse(self):
        if not self.raw:
            return

        self.update({'conda': []})

        for line in self.raw:
            if type(line) is dict:
                self.update(line)
            else:
                self['conda'].append(common.arg2spec(line))

    # TODO only append when it's not already present
    def add(self, package_name):
        self.raw.append(package_name)
        self.parse()


class Environment(object):
    def __init__(self, name=None, filename=None, channels=None,
                 dependencies=None, activate=None, deactivate=None):
        self.name = name
        self.filename = filename
        self.dependencies = Dependencies(dependencies)

        def abspath(path):
            """Obtain an absolute path for ``path`` assuming it is relative to ``filename``"""
            if filename is None or os.path.isabs(path):
                return path
            return os.path.abspath(os.path.join(os.path.dirname(filename), path))

        self.channels = channels or []
        self.dependencies = Dependencies(dependencies or [])
        self.activate = map(abspath, activate or [])
        self.deactivate = map(abspath, deactivate or [])

    def to_dict(self):
        d = yaml.dict([('name', self.name)])
        if self.channels:
            d['channels'] = self.channels
        if self.dependencies:
            d['dependencies'] = self.dependencies.raw
        if self.activate:
            d['activate'] = self.activate
        if self.deactivate:
            d['deactivate'] = self.deactivate
        return d

    def to_yaml(self, stream=None):
        d = self.to_dict()
        out = compat.u(yaml.dump(d, default_flow_style=False))
        if stream is None:
            return out
        stream.write(compat.b(out, encoding="utf-8"))

    def save(self):
        with open(self.filename, "wb") as fp:
            self.to_yaml(stream=fp)
