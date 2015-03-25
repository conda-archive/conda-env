import pkg_resources

from . import helpers


# TODO Write tests
class BaseCommand(object):
    def get_entry_point_name(self, name):
        """
        Internal utility for determining entry point name
        """
        return "{module}.{name}".format(
            module=self.__class__.__module__, name=name)

    def get_entry_points(self, name):
        """
        Internal utility for loading entry points for a name
        """
        entry_point_name = self.get_entry_point_name(name)
        return pkg_resources.iter_entry_points(entry_point_name)

    def get_wrapped_function(self, name):
        """
        Wraps a method by ``name`` with entry points so they can be chained

        This works with ``helper.generate_next`` to wrap all of the entry
        points in reverse order.  It returns a callable function that can
        be invoked with all of the entry point functions chained via Conda's
        internal middleware-like extension mechanism.

        Note: This function is meant for internal use only.
        """
        entry_points = self.get_entry_points(name)
        func = getattr(self, name)
        for entry_point in reversed(list(entry_points)):
            func = helpers.generate_next(entry_point.load(), func)
        return func

    def setup(self, sub_parsers):
        """
        Invoke ``configure_parser`` wrapped with entry points
        """
        return self.get_wrapped_function("configure_parser")(
            self, sub_parsers)

    def dispatch(self):
        """
        Invoke ``execute`` wrapped with entry points
        """
        return self.get_wrapped_function("execute")(self)

    def configure_parser(self, sub_parsers):
        """
        Configure the command line argument parser for this command.

        Required by any sub-class of BaseCommand.
        """
        raise NotImplementedError()

    def execute(self):
        """
        Execute action for a given command.

        Required by any sub-class of BaseCommand.
        """
        raise NotImplementedError()
