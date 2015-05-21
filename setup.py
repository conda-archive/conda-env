#!/usr/bin/env python
import sys

if 'develop' in sys.argv:
    from setuptools import setup
    using_setuptools = True
else:
    from distutils.core import setup
    using_setuptools = False

if sys.version_info[:2] < (2, 7):
    sys.exit("conda is only meant for Python 2.7, with experimental support "
             "for python 3.  current version: %d.%d" % sys.version_info[:2])

if sys.platform == 'win32':
    scripts = [
        'bin\\activate.bat',
        'bin\\deactivate.bat',
    ]
else:
    scripts = [
        'bin/activate',
        'bin/deactivate',
    ]

setup(
    name="conda-env",
    version="2.2alpha.0",
    author="Continuum Analytics, Inc.",
    author_email="support@continuum.io",
    url="https://github.com/conda/conda-env",
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
    long_description=open('README.rst', 'rb').read().decode('UTF-8'),
    packages=[
        'conda_env',
        'conda_env.cli',
        'conda_env.installers',
    ],
    entry_points={
        'conda_env.cli.main_create.configure_parser': [
            'say = conda_env.cli.main_create:say_configure_parser',
        ],
        'conda_env.cli.main_create.execute': [
            'say = conda_env.cli.main_create:say_execute',
        ]
    },
    scripts=[
        'bin/conda-env',
    ] + scripts,
    package_data={},
)
