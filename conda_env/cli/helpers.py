from functools import wraps
import pkg_resources


# TODO Extract to third-party package
def generate_entry_points(name):
    """
    Internal function for generating command entry points
    """
    return {
        "configure_parser": "%s.configure_parser" % name,
        "execute": "%s.execute" % name,
    }


# TODO Extract to third-party package
def enable_entry_point_override(entry_point_name):
    """
    Wraps a given function with entry point calls that can override behavior

    Use this to add a middleware like layer to a function call.  It's used
    inside conda_env to allow third-party code to change the behavior of the
    various subcommands.  For example, you can add a hook that provides an
    additional parameter via the configure_parser hook, then if you detect that
    behavior, change code execution appropriately inside your execute hook.
    """
    def outer(func):
        @wraps(func)
        def inner(*args, **kwargs):
            entry_points = pkg_resources.iter_entry_points(entry_point_name)
            for entry_point in entry_points:
                ret = entry_point.load()(*args, **kwargs)
                if ret is not None:
                    return ret
            return func(*args, **kwargs)
        return inner
    return outer
