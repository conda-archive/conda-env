import pkg_resources

from . import helpers


# TODO Write tests
class BaseCommand(object):
    def get_entry_point_name(self, name):
        return "{module}.{name}".format(
            module=self.__class__.__module__, name=name)

    def get_entry_points(self, name):
        entry_point_name = self.get_entry_point_name(name)
        return pkg_resources.iter_entry_points(entry_point_name)

    def get_wrapped_function(self, name):
        entry_points = self.get_entry_points(name)
        func = getattr(self, name)
        for entry_point in reversed(list(entry_points)):
            func = helpers.generate_next(entry_point.load(), func)
        return func

    def setup(self, sub_parsers):
        return self.get_wrapped_function("configure_parser")(
            self, sub_parsers)

    def dispatch(self):
        return self.get_wrapped_function("execute")(self)

    def configure_parser(self, sub_parsers):
        raise NotImplementedError()

    def execute(self):
        raise NotImplementedError()
