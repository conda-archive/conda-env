from __future__ import absolute_import, print_function

import os
from collections import OrderedDict
from copy import copy
from io import open

# TODO This should never have to import from conda.cli
from conda import install
from conda.api import get_index
from conda.cli import common, main_list
from conda.resolve import NoPackagesFound, Resolve, MatchSpec

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
def from_environment(name, prefix, no_builds=False):
    installed = install.linked(prefix)
    conda_pkgs = copy(installed)
    # json=True hides the output, data is added to installed
    main_list.add_pip_installed(prefix, installed, json=True)

    pip_pkgs = sorted(installed - conda_pkgs)

    if no_builds:
        dependencies = ['='.join(a.rsplit('-', 2)[0:2]) for a in sorted(conda_pkgs)]
    else:
        dependencies = ['='.join(a.rsplit('-', 2)) for a in sorted(conda_pkgs)]
    if len(pip_pkgs) > 0:
        dependencies.append({'pip': ['=='.join(a.rsplit('-', 2)[:2]) for a in pip_pkgs]})

    return Environment(name=name, dependencies=dependencies)


def from_yaml(yamlstr, **kwargs):
    """Load and return an ``Environment`` from a given ``yaml string``"""
    data = yaml.load(yamlstr)
    if kwargs is not None:
        for key, value in kwargs.items():
            data[key] = value
    return Environment(**data)


def from_requirements_txt(reqs_file, **kwargs):
    """Load and return an ``Environment`` from a given ``requirements.txt``"""
    pip_reqs = []
    dep_list = []
    r = Resolve(get_index())
    for line in reqs_file:
        line = line.strip()
        # If it's not an editable package, check if it's available via conda
        if not line.startswith('-e'):
            line = line.split('#', 1)[0].strip()
            if line:
                try:
                    # If package is available via conda, use that
                    r.get_pkgs(MatchSpec(common.arg2spec(line)))
                    dep_list.append(line)
                except NoPackagesFound:
                    # Otherwise, just use pip
                    pip_reqs.append(line)
        # Editable packages just use pip
        elif line:
            pip_reqs.append(line)
    dep_list.append('pip')
    dep_list.append({'pip': pip_reqs})
    data = {'dependencies': dep_list}
    if kwargs is not None:
        for key, value in kwargs.items():
            data[key] = value
    return Environment(**data)


def from_file(filename):
    if not os.path.exists(filename):
        raise exceptions.EnvironmentFileNotFound(filename)
    if filename.endswith('.txt'):
        with open(filename, encoding='utf-8') as fp:
            return from_requirements_txt(fp, filename=filename)
    else:
        with open(filename, 'rb') as fp:
            return from_yaml(fp.read(), filename=filename)


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
            if isinstance(line, dict):
                self.update(line)
            else:
                self['conda'].append(common.arg2spec(line))

    # TODO only append when it's not already present
    def add(self, package_name):
        self.raw.append(package_name)
        self.parse()


class Environment(object):
    def __init__(self, name=None, filename=None, channels=None,
                 dependencies=None):
        self.name = name
        self.filename = filename
        self.dependencies = Dependencies(dependencies)

        if channels is None:
            channels = []
        self.channels = channels

    def to_dict(self):
        d = yaml.dict([('name', self.name)])
        if self.channels:
            d['channels'] = self.channels
        if self.dependencies:
            d['dependencies'] = self.dependencies.raw
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
