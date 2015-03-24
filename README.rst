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

You can override the name of the created channel by providing either ``-n`` or
``--name`` and a valid environment name.  Likewise, you can explicitly provide
an environment spec file using ``-f`` or ``--file`` and the name of the file you
would like to use.


Extension of CLI
----------------
All commands are extendable by using entry points.  Care must be taken when
writing extensions as they change the way commands are executed.

There are two entry points for every ``main_`` module the ``conda_env.cli``
module:

``configure_parser``
    You use this to add command line arguments
``execute``
    You use this to adjust the execution of the actual command

You can register one or both of these entry points.  Generally, you should add
command line arguments in your ``configure_parser`` code that triggers behavior
in your your ``execute`` entry point.

The easiest way to understand how these work is to see them in action. Let's
create an extension to the ``conda env create`` command that adds ``--say``.
When it's added, the extension will print out the name of the environment when
it's done.

I'm going to create this as the ``conda_env_say`` module, but it could be named
anything.  You're going to need a ``setup.py`` file, so create that and make
sure to use ``setuptools.setup`` and not ``distutils.core.setup``.  The latter
does not have the required support for entry points.

Inside your ``setup.py``, add the following:

.. code-block:: python

    entry_points={
        'conda_env.cli.main_create.configure_parser': [
            'say = conda_env_say:say_configure_parser',
        ],
        'conda_env.cli.main_create.execute': [
            'say = conda_env_say:say_execute',
        ]
    }

This code adds the functions ``say_configure_parser`` and ``say_execute`` from
the ``conda_env_say`` module to their respective entry points.  The syntax
you're using here is a dictionary of entry points.  The keys,
``conda_env.cli.main_create.configure_parser`` and
``conda_env.cli.main_create.execute``, tell setuptools what entry points to
register with and the values are the functions you want to register.  For this
you need to include a unique name (it can be anything, Conda doesn't use it
currently, but may in the future), the name of the module where your code is
located, and the function you want to add.

Next up, you need to write your handlers for each of these new entry points.
You should create a ``say_configure_parser`` function that looks like this:

.. code-block:: python

    def say_configure_parser(sub_parsers):
        p = say_configure_parser.next(sub_parsers)
        p.add_argument('--say', action='store_true', default=False,
                       help='say the name')
        return p

There are a couple of things going on here.  Note that the function arguments
are the same as the ``conda_env.cli.main_create.configure_parser`` function,
just a ``sub_parsers`` argument.  That's provided from Conda.  The first line
we call ``say_configure_parser.next``.  This function is added by Conda to
allow you to control how this extension handles calling the main code base.

.. warning::

    You *must* invoke ``your_function.next`` with the arguments provided when
    it's executed or Conda will not behave like it should.  You must also return
    the result from ``your_function.next`` so your code plays nicely with
    other's.  You might not be the only extension installed.

The result of ``next`` is the sub parser that's generated for the ``conda env
create`` command.  You can add your own arguments to that, other sub parsers,
or generally anything that you can do with parsers.

Once that's in place, you need to add the execution code.  Add this to your
module:

.. code-block:: python

    def say_execute(args, parser):
        if args.say:
            if args.name:
                print("you're about to create %s" % args.name)
            else:
                print("you're about to create an environment, but I don't know "
                      "what the name is yet")
        return say_execute.next(args, parser)

This code checks to see if ``--say`` was used from the command line.  When it's
present, it starts trying to display the name.  Conda might note know the name
of the environment at this point since it can also read it from the
``environment.yml`` file.  Depending on whether ``--name`` was explicitly used
or not, this outputs a statement to the user, then continues.

Note again that it calls ``.next`` on the function it self.  That's put there
by Conda, just like the one you used in ``say_configure_parser``.  You *must*
call it and return its result if you want the normal behavior to execute.

Now if you install your new code and run ``conda env create --help`` you'll see
your new option:

.. code-block:: console

    ❯ conda env create --help
    usage: conda-env create [-h] [-n NAME] [-f FILE] [-q QUIET] [--json] [--say]

    Create an environment based on an environment file

    optional arguments:
      -h, --help            show this help message and exit
      -n NAME, --name NAME  name of environment (in /Users/travis/anaconda/envs)
      -f FILE, --file FILE  environment definition (default: environment.yml)
      -q QUIET, --quiet QUIET
      --json                report all output as json. Suitable for using conda
                            programmatically.
      --say                 say the name

Congratulations!  You've written your first Conda extension.
