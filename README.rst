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
        update              Updates the current environment based on environment file

    optional arguments:
      -h, --help            show this help message and exit


``environment.yml``
-------------------
conda-env allows creating environments using the ``environment.yml``
specification file.  This allows you to specify a name, channels to use when
creating the environment, dependencies and activate/deactivate scripts.

To create an environment named ``stats`` with numpy and pandas create an ``environment.yml``
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
    # $ source activate stats
    #
    # To deactivate this environment, use:
    # $ source deactivate
    #

Your output might vary a little bit depending on whether you have the packages
in your local package cache.

You can override the name of the created channel by providing either ``-n`` or
``--name`` and a valid environment name.  Likewise, you can explicitly provide
an environment spec file using ``-f`` or ``--file`` and the name of the file you
would like to use.

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


Activate/deactivate scripts
^^^^^^^^^^^^^^^^^^^^^^^^^^^

.. code-block:: yaml

    name: oracle
    dependencies:
      - oracle_instantclient
    
    # Note that relative paths are relative to this file's location
    activate:
      - set_oraclehome.sh
    deactivate:
      - unset_oraclehome.sh