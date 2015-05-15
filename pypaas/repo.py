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
    Represents a git repo, the canonical storage of code.

    A repo can have no, one or multiple checkouts, which can have no, one or
    multiple instances.
    """
    def __init__(self, name):
        self.name = name

    @property
    def path(self):
        return os.path.join(options.BASEPATH, self.name, 'repo')

    def ensure_existence(self, fail_if_preexisting=True):
        testpath = os.path.join(self.path, 'refs')
        if os.path.isdir(testpath) and fail_if_preexisting:
            raise RuntimeError('Repo already exists')
        if not os.path.isdir(testpath):
            subprocess.check_output(['git', 'init', '--bare', self.path])
            hook = os.path.join(self.path, 'hooks/pre-receive')
            with open(hook, 'w') as hookf:
                hookf.write(HOOKSCRIPT.format(repo=self, options=options))
            os.chmod(hook, stat.S_IXUSR | os.stat(hook).st_mode)

    def new_checkout(self, commit, name):
        checkout = Checkout(self, commit, name)
        checkout.ensure_existence()
        return checkout
