#!/usr/bin/env python
# -*- coding: utf-8 -*-

import errno
import functools
import os
import os.path


def mkdir_p(path):
    try:
        os.makedirs(path)
    except OSError as exc:
        if exc.errno == errno.EEXIST and os.path.isdir(path):
            pass
        else:
            raise


def replace_file(filename, new_contents, chmod=None):
    """
    Leaves either the old file, the old file and a .new file or the new file.

    Writes to .new, calls fsync and then renames to the original filename.
    """
    with open(filename + '.new', 'w') as newf:
        newf.write(new_contents)
        newf.flush()
        if chmod is not None:
            os.chmod(filename + '.new', chmod)
        os.fsync(newf.fileno())
    os.rename(filename + '.new', filename)


class HooksMixin(object):
    """
    Mixin providing the @hook(name) decorator and the call_hook method
    """
    @classmethod
    def hook(cls, name):
        if not hasattr(cls, '_hooks'):
            cls._hooks = {}

        class HookFunction(object):
            def __init__(self, func):
                try:
                    cls._hooks[name].append(func)
                except KeyError:
                    cls._hooks[name] = [func]
                self.func = func
                functools.update_wrapper(self, func)

            def __call__(self, *args, **kwargs):
                return self.func(*args, **kwargs)

        return HookFunction

    def call_hook(self, name, **kwargs):
        if hasattr(self, '_hooks') and name in self._hooks:
            for f in self._hooks[name]:
                f(self, **kwargs)
