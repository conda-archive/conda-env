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
