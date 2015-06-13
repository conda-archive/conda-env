class CondaEnvException(Exception):
    pass


class CondaEnvRuntimeError(RuntimeError, CondaEnvException):
    pass


class EnvironmentFileNotFound(CondaEnvException):
    def __init__(self, filename, *args, **kwargs):
        msg = '{} file not found'.format(filename)
        self.filename = filename
        super(EnvironmentFileNotFound, self).__init__(msg, *args, **kwargs)


class NoBinstar(CondaEnvRuntimeError):
    def __init__(self):
        msg = 'The binstar client must be installed to perform this action'
        super(NoBinstar, self).__init__(msg)


class AlreadyExist(CondaEnvException):
    def __init__(self):
        msg = 'The environment path already exists'
        super(AlreadyExist, self).__init__(msg)


class EnvironmentFileDoesNotExist(CondaEnvRuntimeError):
    def __init__(self, handle, *args, **kwargs):
        self.handle = handle
        msg = "{} does not have an environment definition".format(handle)
        super(EnvironmentFileDoesNotExist, self).__init__(msg, *args, **kwargs)


class EnvironmentFileNotDownloaded(CondaEnvRuntimeError):
    def __init__(self, username, packagename, *args, **kwargs):
        msg = '{}/{} file not downloaded'.format(username, packagename)
        self.username = username
        self.packagename = packagename
        super(EnvironmentFileNotDownloaded, self).__init__(msg, *args, **kwargs)


class SpecNotFound(CondaEnvRuntimeError):
    def __init__(self, msg, *args, **kwargs):
        super(SpecNotFound, self).__init__(msg, *args, **kwargs)


class InvalidLoader(Exception):
    def __init__(self, name):
        msg = 'Unable to load installer for {}'.format(name)
        super(InvalidLoader, self).__init__(msg)


# TODO: This is copied from conda_build. Could yaml parsing from both libraries
# be merged instead of duplicated? This could include jinja2 and "# [unix]" flags.
class UnableToParseMissingJinja2(CondaEnvRuntimeError):
    def __init__(self, *args, **kwargs):
        msg = 'It appears you are missing jinja2.  Please install that ' + \
            'package, then attempt to create the environment.'
        super(UnableToParseMissingJinja2, self).__init__(msg, *args, **kwargs)
