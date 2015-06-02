from conda_env.print_env import print_env
import os
import textwrap
import unittest


class EnvironmentAndAliasesTestCase(unittest.TestCase):

    ENVIRONMENT = [
        {'PATH' : ['mypath1', 'mypath2']},
        {'PATH' : ['mypath3']},
        {'ANY_LIST_REALLY' : ['something1', 'something2']},
        {'SINGLE_VAR' : 'single_value'},
        {'SINGLE_INT' : 200},
    ]
    ALIASES = {
        'my_ls' : 'ls -la'
    }

    def test_environment_and_aliases_bash(self):
        old_environ = os.environ.copy()
        old_pathsep = os.pathsep

        try:
            os.environ['SHELL'] = '/bin/bash'
            os.pathsep = ':'

            activate = print_env('activate', self.ENVIRONMENT, self.ALIASES)
            assert activate == textwrap.dedent(
                '''
                export ANY_LIST_REALLY=something1:something2:$ANY_LIST_REALLY
                export PATH=mypath1:mypath2:mypath3:$PATH
                export SINGLE_INT=200
                export SINGLE_VAR=single_value
                alias my_ls="ls -la"
                '''
            ).lstrip()

            os.environ['PATH'] = '/usr/bin:mypath1:mypath2:mypath3:/usr/local/bin'
            os.environ['SINGLE_VAR'] = 'single_value'
            os.environ['ANY_LIST_REALLY'] = 'something1:something2:'
            deactivate = print_env('deactivate', self.ENVIRONMENT, self.ALIASES)
            assert deactivate == textwrap.dedent(
                '''
                unset ANY_LIST_REALLY
                export PATH=/usr/bin:/usr/local/bin
                unset SINGLE_VAR
                [ `alias | grep my_ls= | wc -l` != 0 ] && unalias my_ls
                '''
            ).lstrip()
        finally:
            os.environ.clear()
            os.environ.update(old_environ)
            os.pathsep = old_pathsep

    def test_environment_and_aliases_cmd(self):
        old_environ = os.environ.copy()
        old_pathsep = os.pathsep

        try:
            os.environ['SHELL'] = 'C:\\Windows\\system32\\cmd.exe'
            os.pathsep = ';'

            activate = print_env('activate', self.ENVIRONMENT, self.ALIASES)
            assert activate == textwrap.dedent(
                '''
                set ANY_LIST_REALLY=something1;something2;%ANY_LIST_REALLY%
                set PATH=mypath1;mypath2;mypath3;%PATH%
                set SINGLE_INT=200
                set SINGLE_VAR=single_value
                doskey my_ls=ls -la
                '''
            ).lstrip()

            os.environ['PATH'] = 'C:\\bin;mypath1;mypath2;mypath3;C:\\Users\\me\\bin'
            os.environ['SINGLE_VAR'] = 'single_value'
            os.environ['ANY_LIST_REALLY'] = 'something1;something2;'
            deactivate = print_env('deactivate', self.ENVIRONMENT, self.ALIASES)
            assert deactivate == textwrap.dedent(
                '''
                set ANY_LIST_REALLY=
                set PATH=C:\\bin;C:\\Users\\me\\bin
                set SINGLE_VAR=
                doskey my_ls=
                '''
            ).lstrip()
        finally:
            os.environ.clear()
            os.environ.update(old_environ)
            os.pathsep = old_pathsep

    def test_environment_and_aliases_tcc(self):
        old_environ = os.environ.copy()
        old_pathsep = os.pathsep

        try:
            os.environ['SHELL'] = 'C:\\Program Files\\tcmd\\TCC.EXE'
            os.pathsep = ';'

            activate = print_env('activate', self.ENVIRONMENT, self.ALIASES)
            assert activate == textwrap.dedent(
                '''
                set ANY_LIST_REALLY=something1;something2;%ANY_LIST_REALLY%
                set PATH=mypath1;mypath2;mypath3;%PATH%
                set SINGLE_INT=200
                set SINGLE_VAR=single_value
                alias my_ls ls -la
                '''
            ).lstrip()

            os.environ['PATH'] = 'C:\\bin;mypath1;mypath2;mypath3;C:\\Users\\me\\bin'
            os.environ['SINGLE_VAR'] = 'single_value'
            os.environ['ANY_LIST_REALLY'] = 'something1;something2;'
            deactivate = print_env('deactivate', self.ENVIRONMENT, self.ALIASES)
            assert deactivate == textwrap.dedent(
                '''
                set ANY_LIST_REALLY=
                set PATH=C:\\bin;C:\\Users\\me\\bin
                set SINGLE_VAR=
                unalias my_ls
                '''
            ).lstrip()
        finally:
            os.environ.clear()
            os.environ.update(old_environ)
            os.pathsep = old_pathsep
