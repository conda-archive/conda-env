import random
from contextlib import contextmanager
from unittest import TestCase
try:
    from unitest import mock
except ImportError:
    import mock

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


class EntryPointOverrideDecoratorTestCase(TestCase):
    def test_requires_one_arguments(self):
        with self.assertRaises(TypeError):
            helpers.enable_entry_point_override()
            helpers.enable_entry_point_override("foo", "bar")

    def test_wraps_func_as_its_own(self):
        @helpers.enable_entry_point_override("foo")
        def my_execute():
            pass

        self.assertEqual("my_execute", my_execute.__name__)

    def test_passes_to_func_if_no_entry_points(self):
        r = random.randint(1000, 2000)

        @helpers.enable_entry_point_override("foo")
        def my_func():
            return r

        with mock.patch.object(helpers, "pkg_resources") as pkg_resources:
            pkg_resources.iter_entry_points.returns = []
            self.assertEqual(r, my_func())

    def test_passes_all_args_to_func(self):
        r = random.randint(1000, 2000)

        @helpers.enable_entry_point_override("foo")
        def my_func(one, two):
            return one * two

        with mock.patch.object(helpers, "pkg_resources") as pkg_resources:
            pkg_resources.iter_entry_points.returns = []
            self.assertEqual(r * r, my_func(r, r))

    def test_passes_all_kwargs_to_func(self):
        r = random.randint(1000, 2000)

        @helpers.enable_entry_point_override("foo")
        def my_func(one=1, two=1):
            return one * two

        with mock.patch.object(helpers, "pkg_resources") as pkg_resources:
            pkg_resources.iter_entry_points.returns = []
            self.assertEqual(1, my_func(), msg="call with default kwargs")
            self.assertEqual(r * r, my_func(one=r, two=r))

    def test_dispatches_to_execute_func(self):
        @helpers.enable_entry_point_override("foo")
        def my_func():
            self.fail(msg="should never execute")

        custom_execute = mock.Mock()
        with mock_execute_entry_point(custom_execute):
            my_func()

        self.assertTrue(custom_execute.called)

    def test_passes_args_to_helper(self):
        @helpers.enable_entry_point_override("foo")
        def my_func_with_args(one, two):
            self.fail(msg="should never execute")

        custom_execute = mock.Mock()
        with mock_execute_entry_point(custom_execute):
            expected_args = ["one", "two",
                             "random%d" % random.randint(100, 200)]
            my_func_with_args(*expected_args)
        custom_execute.assert_called_with(*expected_args)

    def test_passes_kwargs_to_helper(self):
        r = random.randint(1000, 2000)

        @helpers.enable_entry_point_override("foo")
        def my_func_with_kwargs(one=1, two=2, random=r):
            self.fail(msg="should never execute")

        custom_execute = mock.Mock()
        with mock_execute_entry_point(custom_execute):
            kwargs = {
                "one": "one",
                "two": "two",
                "random": random.randint(100, 200),
            }
            my_func_with_kwargs(**kwargs)

        custom_execute.assert_called_with(**kwargs)

    def test_can_capture_output_from_next(self):
        r = random.randint(1000, 2000)

        def middleware(next=None, *args, **kwargs):
            a = middleware.next(*args, **kwargs)
            return a * a

        @helpers.enable_entry_point_override("foo")
        def my_func():
            return r

        with mock_execute_entry_point(middleware):
            self.assertEqual(r * r, my_func(r))


@contextmanager
def mock_execute_entry_point(custom_execute=None):
    if custom_execute is None:
        def middleware(*args, **kwargs):
            return "foobar"

        custom_execute = middleware
    entry_point = mock.Mock()
    entry_point.load.return_value = custom_execute

    with mock.patch.object(helpers, "pkg_resources") as pkg_resources:
        pkg_resources.iter_entry_points = mock.Mock(
            return_value=[entry_point]
        )
        yield custom_execute
