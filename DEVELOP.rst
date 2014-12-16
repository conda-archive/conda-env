=========
conda-env
=========

Installing dev dependencies
---------------------------
`conda create --name conda-env-dev python binstar pip conda`
`source activate conda-env-dev`
`pip install watchdog nose-progressive`

Testing
-------
To run tests as you modify the source, simply run.
`./runtests`

To run a particular test and only that test, add to the relevant test file
`from nose.plugins.attrib import attr`
and then before your test function
`@attr('now')`
Then from your shell, run `nosetests -s -a'attr'`
