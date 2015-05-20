#!/usr/bin/env python
# -*- coding: utf-8 -*-

import os
import os.path
import stat
import subprocess

from . import options
from .checkout import Checkout


HOOKSCRIPT = """
#!/usr/bin/env bash
set -e; set -o pipefail;
export PATH=$PATH:{options.PATH_SUFFIX}
cat | pypaas git-pre-receive-hook {repo.name}
""".strip()


class Repo(object):
    """
    A git repository.

    This is the canonical storage of source code and the only way to get code
    into pyPaaS or update it.
    """
    def __init__(self, name):
        self.name = name

    @property
    def path(self):
        return os.path.join(options.BASEPATH, 'repos', self.name)

    @classmethod
    def create(cls, name, ignore_existing=False):
        self = cls(name)
        testpath = os.path.join(self.path, 'refs')
        if os.path.isdir(testpath) and not ignore_existing:
            raise ValueError('Repo already exists')
        if not os.path.isdir(testpath):
            subprocess.check_call(['mkdir', os.path.join(options.BASEPATH,
                                                         'repos')])
            subprocess.check_output(['git', 'init', '--bare', self.path])
            hook = os.path.join(self.path, 'hooks/pre-receive')
            with open(hook, 'w') as hookf:
                hookf.write(HOOKSCRIPT.format(repo=self, options=options))
            os.chmod(hook, stat.S_IXUSR | os.stat(hook).st_mode)
