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
        msg = 'The anaconda-client cli must be installed to perform this action'
        super(NoBinstar, self).__init__(msg)


class AlreadyExist(CondaEnvRuntimeError):
    def __init__(self):
        msg = 'The environment path already exists'
        super(AlreadyExist, self).__init__(msg)


class EnvironmentAlreadyInNotebook(CondaEnvRuntimeError):
    def __init__(self, notebook, *args, **kwargs):
        msg = "The notebook {} already has an environment"
        super(EnvironmentAlreadyInNotebook, self).__init__(msg, *args, **kwargs)


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


class NBFormatNotInstalled(CondaEnvRuntimeError):
    def __init__(self):
        msg = """nbformat is not installed. Install it with:
        conda install nbformat
        """
        super(NBFormatNotInstalled, self).__init__(msg)


class Jinja2NotInstalled(CondaEnvRuntimeError):
    def __init__(self):
        msg = """jinja2 is not installed. Install it with:
        conda install jinja2
        """
        super(NBFormatNotInstalled, self).__init__(msg)
