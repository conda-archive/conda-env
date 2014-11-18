#!/usr/bin/env python
import sys

from setuptools import setup


if sys.version_info[:2] < (2, 7):
    sys.exit("conda is only meant for Python 2.7, with experimental support "
             "for python 3.  current version: %d.%d" % sys.version_info[:2])

setup(
    name="conda-env",
    version="1.2.0alpha",
    author="Continuum Analytics, Inc.",
    author_email="travis.swicegood@continuum.io",
    url="https://github.com/tswicegood/conda-build",
    license="BSD",
    classifiers=[
        "Development Status :: 4 - Beta",
        "Intended Audience :: Developers",
        "Operating System :: OS Independent",
        "Programming Language :: Python :: 2",
        "Programming Language :: Python :: 2.7",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.3",
    ],
    description="tools for interacting with conda environments",
    long_description=open('README.rst').read(),
    packages=[
        'conda_env',
        'conda_env.cli',
        'conda_env.installers',
    ],
    scripts=[
        'bin/conda-env',
    ],
    entry_points={
        'conda.env.installers': [
            'conda = conda_env.installers.conda',
            'pip = conda_env.installers.pip',
        ],
    },
    package_data={},
)
