import unittest

from conda_env import env
from conda_env.specs.jinja2_file import Jinja2Spec

from .. import utils


class TestJinja2(unittest.TestCase):
    def test_no_environment_file(self):
        spec = Jinja2Spec(name=None, filename='not-a-file')
        self.assertEqual(spec.can_handle(), False)

    def test_no_name(self):
        spec = Jinja2Spec(filename=utils.support_file('jinja2.yml'))
        self.assertEqual(spec.can_handle(), True)

    def test_get_environment(self):
        spec = Jinja2Spec(filename=utils.support_file('jinja2.yml'))
        self.assertIsInstance(spec.environment, env.Environment)
