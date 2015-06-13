#!/usr/bin/env python
'''
Supports:
  * bash
  * cmd.exe (windows default shell)
  * tcc.exe (windows https://jpsoft.com/take-command-windows-scripting.html)
'''
from __future__ import print_function
import os


def print_env(action, environment={}, aliases={}):
    # Determine shell
    shell = os.environ.get('SHELL', os.environ.get('COMSPEC'))
    if shell is None:
        raise RuntimeError('Could not determine shell from environment variables {SHELL, COMSPEC}')
    shell = os.path.basename(shell).lower()
    pathsep = os.pathsep

    # Create environment configuration functions
    if shell == 'bash':
        def Export(name, value):
            if isinstance(value, basestring):
                return 'export %(name)s=%(value)s\n' % locals()
            else:
                value = pathsep.join(value)
                return 'export %(name)s=%(value)s%(pathsep)s$%(name)s\n' % locals()
        def Unset(name):
            return 'unset %(name)s\n' % locals()
        def Alias(name, value):
            return 'alias %(name)s="%(value)s"\n' % locals()
        def Unalias(name):
            return 'unalias %(name)s\n' % locals()

    elif shell == 'cmd.exe':
        def Export(name, value):
            if isinstance(value, basestring):
                return 'set %(name)s=%(value)s\n' % locals()
            else:
                value = pathsep.join(value)
                return 'set %(name)s=%(value)s%(pathsep)s%%%(name)s%%\n' % locals()
        def Unset(name):
            return 'set %(name)s=\n' % locals()
        def Alias(name, value):
            return 'doskey %(name)s=%(value)s\n' % locals()
        def Unalias(name):
            return 'doskey %(name)s=\n' % locals()

    elif shell == 'tcc.exe':
        def Export(name, value):
            if isinstance(value, basestring):
                return 'set %(name)s=%(value)s\n' % locals()
            else:
                value = pathsep.join(value)
                return 'set %(name)s=%(value)s%(pathsep)s%%%(name)s%%\n' % locals()
        def Unset(name):
            return 'set %(name)s=\n' % locals()
        def Alias(name, value):
            return 'alias %(name)s %(value)s\n' % locals()
        def Unalias(name):
            return 'unalias %(name)s\n' % locals()

    # Activate/Deactivate
    if action == 'activate':
        s = ''
        for k, v in sorted(environment.items()):
            s += Export(k, v)
        for k, v in sorted(aliases.items()):
            s += Alias(k, v)
        return s

    elif action == 'deactivate':
        s = ''
        for k, v in sorted(environment.items()):
            if k not in os.environ:
                continue

            if isinstance(v, basestring):
                s += Unset(k)
            else:
                current_value = os.environ[k].split(os.pathsep)
                current_value = [c for c in current_value if c != '']
                for path in v:
                    if path in current_value: current_value.remove(path)
                if len(current_value) == 0:
                    s += Unset(k)
                else:
                    s += Export(k, os.pathsep.join(current_value))

        for alias in sorted(aliases):
            s += Unalias(alias)
        return s


if __name__ == '__main__':
    import sys

    action = sys.argv[1]
    environment = eval(sys.argv[2])
    aliases = eval(sys.argv[3])

    s = print_env(action, environment, aliases)
    print(s)
