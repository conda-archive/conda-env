import random
from unittest import TestCase

from conda_env.cli import helpers


class GenerateEntryPointsTestCase(TestCase):
    def test_requires_one_argument(self):
        with self.assertRaises(TypeError):
            helpers.generate_entry_points()
            helpers.generate_entry_points("one", "two")

    def test_returns_dictionary(self):
        eps = helpers.generate_entry_points("foo")
        self.assertIsInstance(eps, dict)

    def test_has_configure_parser(self):
        eps = helpers.generate_entry_points("foo")
        self.assertTrue("configure_parser" in eps)

    def test_has_execute(self):
        eps = helpers.generate_entry_points("foo")
        self.assertTrue("execute" in eps)

    def test_configure_parser_maps_to_proper_entry_point_name(self):
        random_module = "some.module.foo%d" % random.randint(1000, 2000)
        eps = helpers.generate_entry_points(random_module)
        expected = "%s.configure_parser" % random_module
        self.assertEqual(expected, eps["configure_parser"])

    def test_execute_maps_to_proper_entry_point_name(self):
        random_module = "some.module.foo%d" % random.randint(1000, 2000)
        eps = helpers.generate_entry_points(random_module)
        expected = "%s.execute" % random_module
        self.assertEqual(expected, eps["execute"])
