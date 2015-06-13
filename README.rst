=========
conda-env
=========

Provides the `conda env` interface to Conda environments.

Installing
----------

To install `conda env` with conda, run the following command in your root environment:

.. code-block:: bash

    $ conda install -c conda conda-env


Usage
-----
All of the usage is documented via the ``--help`` flag.

.. code-block:: bash

    $ conda env --help
    usage: conda-env [-h] {create,export,list,remove} ...

    positional arguments:
      {create,export,list,remove}
        create              Create an environment based on an environment file
        export              Export a given environment
        list                List the Conda environments
        remove              Remove an environment
        upload              Upload an environment to binstar
        update              Updates the current environment based on environment
                            file

    optional arguments:
      -h, --help            show this help message and exit


``environment.yml``
-------------------
conda-env allows creating environments using the ``environment.yml``
specification file.  This allows you to specify a name, channels to use when
creating the environment, and the dependencies.  For example, to create an
environment named ``stats`` with numpy and pandas create an ``environment.yml``
file with this as the contents:

.. code-block:: yaml

    name: stats
    dependencies:
      - numpy
      - pandas

Then run this from the command line:

.. code-block:: bash

    $ conda env create
    Fetching package metadata: ...
    Solving package specifications: .Linking packages ...
    [      COMPLETE      ] |#################################################| 100%
    #
    # To activate this environment, use:
    # $ source activate numpy
    #
    # To deactivate this environment, use:
    # $ source deactivate
    #

Your output might vary a little bit depending on whether you have the packages
in your local package cache.

You can explicitly provide an environment spec file using ``-f`` or ``--file``
and the name of the file you would like to use.


``environment.yml`` jinja2 rendering
------------------------------------

If you have ``jinja2`` available in the environment, ``environment.yml`` files will be
rendered with it before processing.

.. code-block:: yaml

    name: pytest
    dependencies:
    {% for i in ['xunit', 'coverage','mock'] %}
      - pytest-{{ i }}
    {% endfor %}

In this example, the previous file with ``jinja2`` syntax is equivalent to:

.. code-block:: yaml

    name: pytest
    dependencies:
      - pytest-xunit
      - pytest-coverage
      - pytest-mock

Available variables
^^^^^^^^^^^^^^^^^^^

When using ``jinja2``, on top of the usual template capabilities, you have access to the
following variables:

- ``root``: The directory containing ``environment.yml``
- ``os``: Python's ``os`` module.


``environment.yml`` examples
----------------------------

Name and dependencies
^^^^^^^^^^^^^^^^^^^^^

.. code-block:: yaml

    name: stats
    dependencies:
      - numpy
      - pandas

Name and version specific dependencies
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

.. code-block:: yaml

    name: stats
    dependencies:
      - numpy==1.8
      - pandas==0.16.1


Environment/aliases
^^^^^^^^^^^^^^^^^^^

.. code-block:: yaml

    name: oracle
    dependencies:
      - oracle_instantclient

    # List type environment variables will be joined with os.pathsep (':' in unix, ';' in windows).
    # These values will be inserted in front of any existing value in the current environment.
    # e.g.:
    #   current PATH: "/usr/local/bin:/usr/bin"
    #   new     PATH: "{{ root }}/bin:/usr/local/bin:/usr/bin"
    environment:
      ORACLE_HOME: /usr/local/oracle_instantclient
      PATH:
        - {{ root }}/bin

    aliases:
      run_db: bash {{ root }}/bin/run_db.sh
