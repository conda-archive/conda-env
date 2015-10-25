#!/usr/bin/env python
import sys
import os

if 'develop' in sys.argv:
    from setuptools import setup
    using_setuptools = True
else:
    from distutils.core import setup
    using_setuptools = False

from distutils.command.install import install as _install

if sys.version_info[:2] < (2, 7):
    sys.exit("conda is only meant for Python 2.7, with experimental support "
             "for python 3.  current version: %d.%d" % sys.version_info[:2])

if sys.platform == 'win32':
    scripts = [
        'bin\\activate.bat',
        'bin\\deactivate.bat',
    ]

    def _post_install(dir):
        from subprocess import call
        for script in ("activate.bat", "deactivate.bat"):
            call(["unix2dos", os.path.join(sys.prefix, "Scripts", script)],)

    class install(_install):
        def run(self):
            _install.run(self)
            self.execute(_post_install, (self.install_lib,),
                        msg="Converting UNIX line endings to Windows")

    cmdclass = {"install": install, "develop": install}
else:
    scripts = [
        'bin/activate',
        'bin/deactivate',
    ]
    cmdclass = {}

setup(
    name="conda-env",
    version="2.5.0alpha",
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
        "Programming Language :: Python :: 3.4",
    ],
    description="tools for interacting with conda environments",
    long_description=open('README.rst').read(),
    packages=[
        'conda_env',
        'conda_env.cli',
        'conda_env.installers',
        'conda_env.specs',
        'conda_env.utils',
    ],
    scripts=[
        'bin/conda-env',
    ] + scripts,
    package_data={},
    cmdclass=cmdclass,
)
