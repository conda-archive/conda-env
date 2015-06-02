import os
import shutil
import sys
import textwrap
import unittest

from conda_env import env
from conda_env.cli.main_create import write_activate_deactivate

from . import utils


class activate_deactivate_TestCase(unittest.TestCase):
    _ENV = env.Environment(environment=[{'FOO' : 'BAR'}], aliases={'my_ls' : 'ls -la'})
    _CONDA_DIR = utils.support_file('conda')
    _PREFIX = os.path.join(_CONDA_DIR, 'envs', 'test_write_activate_deactivate')
    _OBTAINED_PRINT_ENV = os.path.join(_PREFIX, 'etc', 'conda', 'print_env.py')
    _EXPECTED_PRINT_ENV = os.path.join(
        os.path.dirname(__file__),
        '..',
        'conda_env',
        'print_env.py'
    )

    def test_write_activate_deactivate_unix(self):
        old_platform = sys.platform
        sys.platform = 'linux2'
        try:
            write_activate_deactivate(self._ENV, self._PREFIX)

            with open(os.path.join(self._PREFIX, 'etc', 'conda', 'activate.d', '_activate.sh')) as activate:
                self.assertEqual(activate.read(), textwrap.dedent(
                    '''
                    python "%s" activate "[{\'FOO\': \'BAR\'}]" "{\'my_ls\': \'ls -la\'}" > _tmp_activate.sh
                    source _tmp_activate.sh
                    rm _tmp_activate.sh
                    '''
                ).lstrip() % self._OBTAINED_PRINT_ENV)

            with open(os.path.join(self._PREFIX, 'etc', 'conda', 'deactivate.d', '_deactivate.sh')) as deactivate:
                self.assertEqual(deactivate.read(), textwrap.dedent(
                    '''
                    python "%s" deactivate "[{\'FOO\': \'BAR\'}]" "{\'my_ls\': \'ls -la\'}" > _tmp_deactivate.sh
                    source _tmp_deactivate.sh
                    rm _tmp_deactivate.sh
                    '''
                ).lstrip() % self._OBTAINED_PRINT_ENV)

            with open(self._OBTAINED_PRINT_ENV) as obtained_print_env:
                with open(self._EXPECTED_PRINT_ENV) as expected_print_env:
                    self.assertEqual(obtained_print_env.read(), expected_print_env.read())
        finally:
            sys.platform = old_platform
            shutil.rmtree(self._CONDA_DIR)


    def test_write_activate_deactivate_win(self):
        try:
            write_activate_deactivate(self._ENV, self._PREFIX)

            with open(os.path.join(self._PREFIX, 'etc', 'conda', 'activate.d', '_activate.bat')) as activate:
                self.assertEqual(activate.read(), textwrap.dedent(
                    '''
                    python "%s" activate "[{\'FOO\': \'BAR\'}]" "{\'my_ls\': \'ls -la\'}" > _tmp_activate.bat
                    call _tmp_activate.bat
                    del _tmp_activate.bat
                    '''
                ).lstrip() % self._OBTAINED_PRINT_ENV)

            with open(os.path.join(self._PREFIX, 'etc', 'conda', 'deactivate.d', '_deactivate.bat')) as deactivate:
                self.assertEqual(deactivate.read(), textwrap.dedent(
                    '''
                    python "%s" deactivate "[{\'FOO\': \'BAR\'}]" "{\'my_ls\': \'ls -la\'}" > _tmp_deactivate.bat
                    call _tmp_deactivate.bat
                    del _tmp_deactivate.bat
                    '''
                ).lstrip() % self._OBTAINED_PRINT_ENV)

            with open(self._OBTAINED_PRINT_ENV) as obtained_print_env:
                with open(self._EXPECTED_PRINT_ENV) as expected_print_env:
                    self.assertEqual(obtained_print_env.read(), expected_print_env.read())
        finally:
            shutil.rmtree(self._CONDA_DIR)
