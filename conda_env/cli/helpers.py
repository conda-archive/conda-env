def generate_entry_points(name):
    """
    Internal function for generating command entry points
    """
    return {
        "configure_parser": "%s.configure_parser" % name,
        "execute": "%s.execute" % name,
    }
