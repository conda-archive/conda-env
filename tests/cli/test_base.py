import mock
import random
from unittest import TestCase

from conda_env.cli import base


class BaseCommandTestCase(TestCase):
    def get_name_as_entry_point(self, name):
        return "%s.%s" % (self.__class__.__module__, name)

    def test_get_entyr_point_name(self):
        class Foobar(base.BaseCommand):
            pass

        obj = Foobar()
        name = "foo_%d" % random.randint(100, 200)
        actual = obj.get_entry_point_name(name)
        expected = self.get_name_as_entry_point(name)
        self.assertEqual(expected, actual)

    def test_get_entry_points_dispatches_to_name(self):
        name = "foo_%d" % random.randint(100, 200)

        class Command(base.BaseCommand):
            pass

        obj = Command()
        with mock.patch.object(obj, "get_entry_point_name") as mocked:
            obj.get_entry_points(name)
        mocked.assert_called_with(name)

    def test_get_entry_points_dispatches_to_iter_entry_points(self):
        name = "foo_%d" % random.randint(100, 200)

        class Command(base.BaseCommand):
            pass

        obj = Command()
        with mock.patch.object(base.pkg_resources,
                               "iter_entry_points") as iter_entry_points:
            obj.get_entry_points(name)
        iter_entry_points.assert_called_with(obj.get_entry_point_name(name))

    def test_setup(self):
        sub_parsers = random.randint(1000, 2000)
        obj = base.BaseCommand()

        with mock.patch.object(
                obj, "get_wrapped_function") as get_wrapped_function:
            some_result = random.randint(1000, 2000)
            some_func = mock.Mock(return_value=some_result)
            get_wrapped_function.return_value = some_func
            actual = obj.setup(sub_parsers)

        get_wrapped_function.assert_called_once_with("configure_parser")
        some_func.assert_called_with(obj, sub_parsers)
        self.assertEqual(some_result, actual)

    def test_dispatch(self):
        obj = base.BaseCommand()

        with mock.patch.object(
                obj, "get_wrapped_function") as get_wrapped_function:
            some_result = random.randint(1000, 2000)
            some_func = mock.Mock(return_value=some_result)
            get_wrapped_function.return_value = some_func
            actual = obj.dispatch()

        get_wrapped_function.assert_called_once_with("execute")
        some_func.assert_called_with(obj)
        self.assertEqual(some_result, actual)

    def test_configure_parses_raises(self):
        with self.assertRaises(NotImplementedError):
            obj = base.BaseCommand()
            obj.configure_parser("foo")

    def test_execute(self):
        with self.assertRaises(NotImplementedError):
            obj = base.BaseCommand()
            obj.execute()


class get_wrapped_function_TestCase(TestCase):
    def test_returns_function_by_default(self):
        obj = base.BaseCommand()
        self.assertEqual(obj.execute, obj.get_wrapped_function("execute"))

    def test_dispatches_to_generate_next(self):
        my_entry_point = object()
        mock_entry_point = mock.Mock()
        mock_entry_point.load.return_value = my_entry_point

        obj = base.BaseCommand()
        with mock.patch.object(obj, "get_entry_points") as get_entry_points:
            get_entry_points.return_value = (mock_entry_point, )

            with mock.patch.object(base.helpers,
                                   "generate_next") as generate_next:
                obj.get_wrapped_function("execute")
        generate_next.assert_called_with(my_entry_point, obj.execute)

    def test_passes_each_entry_point_to_generate_next_in_reverse_order(self):
        first_entry_point = object()
        second_entry_point = object()
        mock_entry_point = mock.Mock()

        mock_entry_point.load.side_effect = [first_entry_point,
                                             second_entry_point]

        obj = base.BaseCommand()
        with mock.patch.object(obj, "get_entry_points") as get_entry_points:
            get_entry_points.return_value = (
                mock_entry_point,
                mock_entry_point,
            )

            with mock.patch.object(base.helpers,
                                   "generate_next") as generate_next:
                wrapped_one = object()
                wrapped_two = object()
                generate_next.side_effect = [wrapped_one, wrapped_two]
                actual = obj.get_wrapped_function("execute")

        generate_next.assert_has_calls([
            mock.call(first_entry_point, obj.execute),
            mock.call(second_entry_point, wrapped_one),
        ])
        self.assertEqual(wrapped_two, actual)
