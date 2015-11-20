import os
import sys
try:
    import jinja2
except ImportError:
    jinja2 = None
from .. import env
from ..exceptions import EnvironmentFileNotFound, Jinja2NotInstalled


class Jinja2Spec(object):
    _environment = None

    def __init__(self, filename=None, **kwargs):
        self.filename = filename
        self.msg = None

    def can_handle(self):
        try:
            self._environment = env.from_yaml(
                self._jinja2(self.filename)
            )
            return True
        except (EnvironmentFileNotFound, Jinja2NotInstalled, IOError) as e:
            self.msg = str(e)
            return False

    def _jinja2(self, filename):
        if jinja2 is None:
            raise Jinja2NotInstalled()
        with open(filename) as jinjafile:
            return jinja2.Template(jinjafile.read()).render(sys=sys, os=os)

    @property
    def environment(self):
        if not self._environment:
            self.can_handle()
        return self._environment
